import tkinter as tk
from tkinter import messagebox
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
from PIL import Image, ImageDraw, ImageTk
import os
import traceback

# Sample file setup
SAMPLE_FILE = "sample.txt"
BACKUP_FILE = "sample_backup.txt"
BUSINESS_FILES = ["business_letter.txt", "invoice.txt"]
REQUIRED_IMAGES = ["cyber_bg.png", "CyberSmokey.jpg"]

def readfile(filename, is_binary=False):
    mode = "rb" if is_binary else "r"
    encoding = None if is_binary else "utf-8"
    with open(filename, mode, encoding=encoding) as file:
        return file.read()

def writefile(data, filename, is_binary=False):
    mode = "wb" if is_binary else "w"
    encoding = None if is_binary else "utf-8"
    with open(filename, mode, encoding=encoding) as file:
        file.write(data if is_binary else data)

def initialize_sample_files():
    """Create all required sample files for the ransomware demo."""
    try:
        if not os.path.exists(SAMPLE_FILE):
            writefile("This is a sample file to demonstrate a file configuration with 64 bytes of data.", SAMPLE_FILE)
        if not os.path.exists(BACKUP_FILE):
            writefile(readfile(SAMPLE_FILE), BACKUP_FILE)
        for file in BUSINESS_FILES:
            backup_file = file + ".bak"
            if not os.path.exists(file):
                if file == "business_letter.txt":
                    writefile("Dear Client,\nWe are pleased to offer you a contract worth $500,000 for Q3 2025.\nRegards,\nBusiness Inc.", file)
                elif file == "invoice.txt":
                    writefile("Invoice #1234\n50 units of Product X at $200 each\nTotal: $10,000\nDue: 04/01/2025", file)
            if not os.path.exists(backup_file):
                writefile(readfile(file), backup_file)
        
        with open(SAMPLE_FILE, "rb") as f:
            print(f"File size: {len(f.read())} bytes")
            
        return True, None
    except Exception as e:
        error_msg = f"Error creating sample files: {str(e)}"
        print(error_msg)
        return False, error_msg

def verify_required_images():
    """Verify that image files exist, but don't block initialization if they're missing."""
    missing_images = []
    for image_file in REQUIRED_IMAGES:
        if not os.path.exists(image_file):
            missing_images.append(image_file)
    
    if missing_images:
        print(f"Note: Missing image files: {', '.join(missing_images)}. Will use fallback backgrounds.")
    return True, None  # Always return True, images are optional

def initialize_ransomware_demo(parent_window):
    """
    Wrapper function to initialize the RansomwareDemo with proper error handling.
    
    Args:
        parent_window: The Tkinter window to use as parent for the RansomwareDemo
        
    Returns:
        tuple: (success, result_or_error_message)
            - If successful: (True, RansomwareDemo instance)
            - If failed: (False, error message string)
    """
    try:
        # Step 1: Check if required image files exist
        print("Verifying required image files...")
        images_ok, image_error = verify_required_images()
        if not images_ok:
            return False, image_error
            
        # Step 2: Initialize sample files
        print("Initializing sample files...")
        files_ok, file_error = initialize_sample_files()
        if not files_ok:
            return False, file_error
        
        # Step 3: Create the RansomwareDemo instance
        print("Creating RansomwareDemo instance...")
        ransom_demo = RansomwareDemo(parent_window)
        
        # If we got here, everything worked
        return True, ransom_demo
    
    except Exception as e:
        # Get full traceback for detailed error information
        tb = traceback.format_exc()
        error_msg = f"Error initializing ransomware demo: {str(e)}\n\nTraceback:\n{tb}"
        print(error_msg)
        return False, error_msg

class RansomwareDemo(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent
        
        # Color scheme
        self.BG_COLOR = "#1a1a1a"
        self.TEXT_COLOR = "#ff0000"
        self.BUTTON_BG = "#ff0000"
        self.BUTTON_FG = "#000000"
        
        # Font sizes (all increased by factor of 1.2 from original)
        self.TITLE_FONT_SIZE = 20    # Was ~16-17
        self.TEXT_FONT_SIZE = 17     # Was 14
        self.BUTTON_FONT_SIZE = 14   # Was 12
        self.SMALL_FONT_SIZE = 12    # For smaller text elements
        
        # Debug logging for font sizes
        print(f"Font sizes initialized - Title: {self.TITLE_FONT_SIZE}, Text: {self.TEXT_FONT_SIZE}, Button: {self.BUTTON_FONT_SIZE}, Small: {self.SMALL_FONT_SIZE}")
        
        # Initialize variables
        self.page = 0
        self.aes_key = None
        self.encrypted_files = {}
        self.current_text_widget = None
        self.current_text = ""
        self.canvas_items = []  # Non-button items to fade
        self.button_items = []  # Buttons to keep
        self.bg_image_id = None  # Track background image
        
        # Set up the frame
        self.pack(fill=tk.BOTH, expand=True)
        self.configure(bg=self.BG_COLOR)
        
        # Initialize GUI
        self.init_gui()
        
    def init_gui(self):
        """Initialize the GUI components of the demo."""
        # Initialize file icons
        self.init_file_icons()
        
        # Initialize background images
        self.init_background_images()
        
        # Create canvas - slightly increase canvas size to accommodate larger text
        self.canvas = tk.Canvas(self, width=1100, height=880, bg=self.BG_COLOR, highlightthickness=0)
        print(f"Canvas dimensions: {self.canvas.winfo_reqwidth()}x{self.canvas.winfo_reqheight()} to accommodate larger text")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Start the demo
        self.draw_background()
        self.next_page()
    
    def init_file_icons(self):
        """Initialize file icons for the demo."""
        # Load file icon
        try:
            file_icon = Image.open("file_icon.png").resize((50, 50), Image.Resampling.LANCZOS)
        except FileNotFoundError:
            # Create a simple file icon since the image file was not found
            file_icon = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
            draw = ImageDraw.Draw(file_icon)
            draw.rectangle([5, 5, 45, 45], outline="black", fill="white")
            draw.text((10, 20), "TXT", fill="black")
        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"Error creating file icon: {str(e)}")
            # Create a very basic fallback icon
            file_icon = Image.new("RGBA", (50, 50), (200, 200, 200, 255))
            draw = ImageDraw.Draw(file_icon)
            draw.rectangle([5, 5, 45, 45], outline="black", fill="gray")
            draw.text((10, 20), "FILE", fill="black")
        
        self.file_icon_tk = ImageTk.PhotoImage(file_icon)
    
    def init_background_images(self):
        """Initialize background images for the demonstration."""
        try:
            # Try to load the main background image
            print("Loading background image: cyber_bg.png")
            bg_image = Image.open("cyber_bg.png")
            # Resize if needed to fit the canvas
            bg_image = bg_image.resize((1100, 880), Image.Resampling.LANCZOS)  # Match new canvas size
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            print("Successfully loaded cyber_bg.png")
        except FileNotFoundError:
            # Create a solid color background if image is missing
            print("Creating fallback background for cyber_bg.png")
            bg_image = Image.new('RGB', (1100, 880), self.BG_COLOR)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        except Exception as e:
            print(f"Error loading background image: {str(e)}")
            bg_image = Image.new('RGB', (1100, 880), self.BG_COLOR)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
        try:
            # Try to load the final background image
            print("Loading background image: CyberSmokey.jpg")
            final_image = Image.open("CyberSmokey.jpg")
            # Resize if needed to fit the canvas
            final_image = final_image.resize((1100, 880), Image.Resampling.LANCZOS)  # Match new canvas size
            self.final_photo = ImageTk.PhotoImage(final_image)
            print("Successfully loaded CyberSmokey.jpg")
        except FileNotFoundError:
            # Create a solid color background if image is missing
            print("Creating fallback background for CyberSmokey.jpg")
            final_image = Image.new('RGB', (1100, 880), self.BG_COLOR)
            self.final_photo = ImageTk.PhotoImage(final_image)
        except Exception as e:
            print(f"Error loading final image: {str(e)}")
            final_image = Image.new('RGB', (1100, 880), self.BG_COLOR)
            self.final_photo = ImageTk.PhotoImage(final_image)
    
    # Core encryption/decryption functions
    def writeAESKey(self, bits=128):
        """Generate and save an AES key of the specified bit size."""
        key = get_random_bytes(bits//8)
        writefile(key, "aes128_key.bin", is_binary=True)
        return key
    
    def encryptAES(self, message, key):
        """Encrypt a message using AES encryption with the provided key."""
        cipher = AES.new(key, AES.MODE_CBC)
        initialVector = cipher.iv
        message_bytes = message.encode('utf-8') if isinstance(message, str) else message
        ciphertext = cipher.encrypt(pad(message_bytes, AES.block_size))
        return b64encode(initialVector + ciphertext)
    
    def decryptAES(self, ciphertext, key):
        """Decrypt an AES encrypted message using the provided key."""
        cipherData = b64decode(ciphertext)
        initialVector = cipherData[:AES.block_size]
        ciphertext = cipherData[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CBC, initialVector)
        message = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return message.decode('utf-8')
    # Navigation methods
    def next_page(self):
        """Navigate to the next page of the presentation."""
        if self.current_text_widget:
            self.slow_encrypt_text(self.current_text_widget, self.current_text)
        else:
            self.fade_out(self.canvas_items)

    def load_next_page(self):
        """Load the next page of the demo based on the current page number."""
        for item in self.button_items:
            self.canvas.delete(item)
        self.canvas_items = []
        self.button_items = []
        if self.bg_image_id:
            self.canvas.delete(self.bg_image_id)
        self.page_counter(increment=True)
        self.draw_background()
        if self.page == 1:
            self.show_ransom_text()
        elif self.page == 2:
            self.show_ransom_attacks()
        elif self.page == 3:
            self.show_ransom_mitigation()
        elif self.page == 4:
            self.show_ransom_detection_techniques()
        elif self.page == 5:
            self.show_ransom_response_strategies()
        elif self.page == 6:
            self.show_ransom_critical_infrastructure()
        elif self.page == 7:
            self.show_demo_email()
        elif self.page == 8:
            self.show_ransomware_encrypted()
        elif self.page == 9:
            self.show_ransomware_backup_recovery()
        elif self.page == 10:
            self.show_sources()
        elif self.page == 11:
            self.show_final_page()
        else:
            self.page_reset()
            self.show_ransom_text()
    def back_page(self):
        self.canvas.delete("all")
        self.canvas_items = []
        self.button_items = []
        self.bg_image_id = None
        self.page_counter(increment=False)
        self.draw_background()
        if self.page == 1:
            self.show_ransom_text()
        elif self.page == 2:
            self.show_ransom_attacks()
        elif self.page == 3:
            self.show_ransom_mitigation()
        elif self.page == 4:
            self.show_ransom_detection_techniques()
        elif self.page == 5:
            self.show_ransom_response_strategies()
        elif self.page == 6:
            self.show_ransom_critical_infrastructure()
        elif self.page == 7:
            self.show_demo_email()
        elif self.page == 8:
            self.show_ransomware_encrypted()
        elif self.page == 9:
            self.show_ransomware_backup_recovery()
        elif self.page == 10:
            self.show_sources()
        else:
            self.page_reset()
            self.show_ransom_text()
    def page_reset(self):
        """Reset the page counter to the first page."""
        self.page = 1

    def page_counter(self, increment=True):
        """Increment or decrement the page counter."""
        if increment:
            self.page += 1
        else:
            self.page = max(1, self.page - 1)
            
    def draw_background(self):
        """Draw the appropriate background image based on the current page."""
        try:
            if self.page <= 10 and hasattr(self, 'bg_photo') and self.bg_photo:
                self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            elif self.page == 11 and hasattr(self, 'final_photo') and self.final_photo:
                self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.final_photo)
            else:
                # If no image is available, just use the background color
                self.canvas.configure(bg=self.BG_COLOR)
        except Exception as e:
            print(f"Error drawing background: {str(e)}")
            self.canvas.configure(bg=self.BG_COLOR)

    # Inspection functions
    def inspect_encrypted_file(self, file):
        """Display the encrypted contents of a file in a message box."""
        content = self.encrypted_files.get(file, b"No encryption performed yet.").decode('utf-8')[:100] + "..." if self.encrypted_files.get(file) else "No encryption yet."
        messagebox.showinfo(f"Encrypted {file}", f"Contents of {file}:\n\n{content}")
    
    def inspect_restored_file(self, file):
        """Display the restored contents of a file in a message box."""
        content = readfile(file)
        messagebox.showinfo(f"Restored {file}", f"Contents of {file}:\n\n{content}")

    # Page content
    def show_ransom_text(self):
        if self.aes_key is None:
            self.aes_key = self.writeAESKey(bits=128)
        text = (
            "Ransomware Attack\n\n"
            "A ransomware attack is a type of malware that encrypts a victim's files. The attacker then demands a ransom "
            "from the victim to restore access to the data upon payment.\n\n"
            "Key Characteristics:\n"
            "- Users are shown instructions for how to pay a fee to get the decryption key.\n"
            "- Costs can range from a few hundred dollars to thousands, payable to cybercriminals in Bitcoin.\n\n"
            "Impact:\n"
            "The ransomware attack is a growing threat to individuals and organizations of all sizes."
        )
        self.current_text = text
        encrypted_text = self.encryptAES(text, self.aes_key)
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                            relief="flat", padx=12, pady=6)  # Increased padding
        
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(500, 780, anchor="s", window=next_button)]

    def show_ransom_attacks(self):
        text = (
            "Ransomware Attacks\n\n"
            "Some of the most famous ransomware attacks include:\n"
            "- WannaCry: A ransomware attack that spread globally in May 2017, affecting hundreds of thousands of computers.\n"
            "- Petya/NotPetya: A ransomware attack that hit in June 2017, affecting organizations worldwide.\n"
            "- Ryuk: A ransomware attack that has targeted businesses, government agencies, and healthcare organizations.\n"
            "- REvil/Sodinokibi: A ransomware group known for targeting large corporations and demanding high ransoms.\n\n"
            "- Damages from ransomware attacks do not just come in the form of payment to the attackers. They can also include "
            "downtime, data loss, and reputational damage, including legal consequences including fines and lawsuits.\n\n"
            "Attack Vectors:\n"
            "Ransomware assaults can be delivered via email attachments, malicious links, or software vulnerabilities.\n"
            "Common vectors include phishing emails, exploit kits, and remote desktop protocol (RDP) vulnerabilities.\n"
            "Maintaining up-to-date software and security practices is crucial to protect against ransomware."
        )
        self.current_text = text
        encrypted_text = self.encryptAES(text, self.aes_key)
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                            relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                            relief="flat", padx=12, pady=6)  # Increased padding
        
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]
        self.master.after(100, lambda: self.slow_decrypt_text(text_widget, encrypted_text, text))

    def show_ransom_mitigation(self):
        text = (
            "Ransomware Mitigation\n\n"
            "To protect against ransomware attacks, consider the following mitigation strategies:\n"
            "- Regularly back up your data and store it in a secure, offline location (e.g., external drive, cloud with versioning).\n"
            "- Keep your software up to date with the latest security patches.\n"
            "- Be cautious when opening email attachments or clicking on links from unknown sources.\n"
            "- Use strong, unique passwords for all accounts and enable two-factor authentication where possible.\n"
            "- Educate employees about the risks of ransomware and how to recognize phishing attempts.\n"
            "- Implement network segmentation and restrict user access to sensitive data.\n"
            "- Consider using security software that can detect and block ransomware attacks.\n"
        )
        self.current_text = text
        encrypted_text = self.encryptAES(text, self.aes_key)
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]

    def show_ransom_detection_techniques(self):
        text = (
            "Ransomware Detection Techniques\n\n"
            "Some common ransomware detection techniques include:\n"
            "- Signature-based detection: Antivirus software can detect known ransomware signatures and block malicious files.\n"
            "- Heuristic analysis: Security software can identify ransomware based on its behavior, such as file encryption.\n"
            "- Anomaly detection: Monitoring network traffic and user behavior for unusual patterns that may indicate a ransomware attack.\n"
            "- File integrity monitoring: Checking for changes to files and directories that may indicate ransomware activity.\n"
            "- Endpoint detection and response (EDR): Monitoring and responding to suspicious activity on endpoints to prevent ransomware attacks.\n"
            "- Security information and event management (SIEM): Collecting and analyzing log data to detect and respond to ransomware threats.\n"
            "- User training: Educating employees about ransomware risks and how to recognize and report suspicious activity.\n"
            "- Honey pots: Setting up decoy systems to attract and detect ransomware attacks before they can infect production systems.\n"
            "- Machine learning: Using artificial intelligence to detect ransomware patterns and behaviors that may be missed by traditional methods.\n"
            "- Threat intelligence: Sharing information about ransomware threats and tactics to improve detection and response capabilities."
        )
        self.current_text = text
        encrypted_text = self.encryptAES(text, self.aes_key)
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]
        self.master.after(100, lambda: self.slow_decrypt_text(text_widget, encrypted_text, text))
        
    def show_ransom_response_strategies(self):
        text = (
            "Ransomware Response Strategies\n\n"
            "In the event of a ransomware attack, consider the following response strategies:\n"
            "- Isolate infected systems: Disconnect compromised devices from the network to prevent the spread of ransomware.\n"
            "- Preserve evidence: Document the attack, including ransom notes, encrypted files, and any communication with the attackers.\n"
            "- Notify law enforcement: Report the ransomware attack to local authorities or cybersecurity agencies for investigation.\n"
            "- Contact cybersecurity experts: Work with professionals who specialize in ransomware response to assess the situation and develop a recovery plan.\n"
            "- Determine the extent of the attack: Identify which systems and data have been affected by the ransomware and prioritize recovery efforts.\n"
            "- Evaluate the ransom demand: Consider the risks and benefits of paying the ransom versus restoring data from backups.\n"
            "- Restore data from backups: Recover encrypted files from secure backups to restore normal operations and avoid paying the ransom.\n"
            "- Implement security measures: Strengthen security controls, update software, and educate employees to prevent future ransomware attacks.\n"
            "- Test incident response plan: Review the effectiveness of your response to the ransomware attack and make improvements for future incidents.\n"
            "- Communicate with stakeholders: Keep employees, customers, and partners informed about the ransomware attack and recovery efforts."
        )
        self.current_text = text
        encrypted_text = self.encryptAES(text, self.aes_key)
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]
        self.master.after(100, lambda: self.slow_decrypt_text(text_widget, encrypted_text, text))
    def show_demo_email(self):
        if self.aes_key is None:
            self.aes_key = self.writeAESKey(bits=128)
        text = (
            "From: NetflixCustomer5ervice@ntflx.com\n"
            "To: YourEmailAddress@email.com\n"
            "Subject: Netflix Account Verification\n\n"
            "Dear YourName,\n\n"
            "We've detected unusual activity on your Netflix account. "
            "To ensure your account security, please click the link below to verify your information.\n\n"
            "Your account will be locked if you don't verify within 24 hours.\n\n"
            "Thank you,\n"
            "The Netflix Customer Support Team"
        )
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        
        def on_link_click():
            self.set_encrypted_files()
            messagebox.showwarning(
                "Ransom Note",
                "Your files have been encrypted!\n\n"
                "To recover your data, send 0.5 Bitcoin to: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n"
                "Email proof of payment to: attacker@darkweb.com\n"
                "You have 48 hours, or your files will be lost forever!"
            )
            self.fade_out([self.canvas_items[1]])
        
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        link_button = tk.Button(self.master, text="https://www.netflx.com/verify?token=1234567890abcdef", fg="blue", bg=self.BG_COLOR, 
                                relief="flat", font=("Courier New", self.BUTTON_FONT_SIZE, "underline"), cursor="hand2", command=on_link_click)
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button),
                        self.canvas.create_window(500, 650, anchor="center", window=link_button)]

    def show_ransomware_encrypted(self):
        """Display the ransomware encrypted files view with proper text sizing."""
        if not self.encrypted_files:
            self.set_encrypted_files()
            
        text = (
            "Ransomware in Action\n\n"
            "Your files have been encrypted with a strong AES encryption algorithm.\n\n"
            "The impact of ransomware:\n"
            "- All your important files are now inaccessible\n"
            "- Without the decryption key, recovery is nearly impossible\n"
            "- Attackers typically demand payment in cryptocurrency\n"
            "- Even if you pay, there's no guarantee you'll get your files back\n\n"
            "Click on the file icons below to see what encrypted files look like:"
        )
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        file1_label = tk.Label(self.master, image=self.file_icon_tk, text="business_letter.txt", compound="top", bg=self.BG_COLOR, fg=self.TEXT_COLOR, 
                               font=("Courier New", self.SMALL_FONT_SIZE), cursor="hand2")  # Using consistent font size
        file1_label.bind("<Button-1>", lambda e: self.inspect_encrypted_file("business_letter.txt"))
        
        file2_label = tk.Label(self.master, image=self.file_icon_tk, text="invoice.txt", compound="top", bg=self.BG_COLOR, fg=self.TEXT_COLOR, 
                               font=("Courier New", self.SMALL_FONT_SIZE), cursor="hand2")  # Using consistent font size
        file2_label.bind("<Button-1>", lambda e: self.inspect_encrypted_file("invoice.txt"))
        
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]
                        
        # Add the file icons below the explanatory text
        self.canvas_items.extend([
            self.canvas.create_window(300, 500, anchor="center", window=file1_label),
            self.canvas.create_window(700, 500, anchor="center", window=file2_label)
        ])
    
    def set_encrypted_files(self):
        """Encrypt the sample files and store them in the encrypted_files dictionary."""
        self.encrypted_files = {}
        try:
            for file in BUSINESS_FILES:
                try:
                    content = readfile(file)
                    self.encrypted_files[file] = self.encryptAES(content, self.aes_key)
                    with open(file, "wb") as f:
                        f.write(b64decode(self.encrypted_files[file]))
                except Exception as e:
                    print(f"Error encrypting file {file}: {str(e)}")
                    # Add a fallback encrypted content for demo purposes
                    self.encrypted_files[file] = self.encryptAES(f"Encrypted content for {file}", self.aes_key)
        except Exception as e:
            print(f"Error in set_encrypted_files: {str(e)}")
            messagebox.showwarning("Encryption Error", "There was an error encrypting the files. The demo will continue with simulated encryption.")
        text = (
            "Files Encrypted!\n\n"
            "After clicking the malicious link, your files are now encrypted. Click the file icons below to inspect their contents:"
        )
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        file1_label = tk.Label(self.master, image=self.file_icon_tk, text="business_letter.txt", compound="top", bg=self.BG_COLOR, fg=self.TEXT_COLOR, 
                               font=("Courier New", self.SMALL_FONT_SIZE), cursor="hand2")  # Using consistent font size
        file1_label.bind("<Button-1>", lambda e: self.inspect_encrypted_file("business_letter.txt"))
        
        file2_label = tk.Label(self.master, image=self.file_icon_tk, text="invoice.txt", compound="top", bg=self.BG_COLOR, fg=self.TEXT_COLOR, 
                               font=("Courier New", self.SMALL_FONT_SIZE), cursor="hand2")  # Using consistent font size
        file2_label.bind("<Button-1>", lambda e: self.inspect_encrypted_file("invoice.txt"))
        
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800),  # Increased for larger text
                        self.canvas.create_window(300, 500, anchor="center", window=file1_label),
                        self.canvas.create_window(700, 500, anchor="center", window=file2_label)]
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]
    def show_ransomware_backup_recovery(self):
        for file in BUSINESS_FILES:
            backup_content = readfile(file + ".bak")
            writefile(backup_content, file)
        
        text = (
            "Recovering with Backups\n\n"
            "Backups are a key mitigation strategy against ransomware. Here's how they work:\n"
            "- Regular backups (e.g., to an offline drive or cloud with versioning) preserve your data.\n"
            "- After an attack, isolate the system, remove the ransomware, and restore from a clean backup.\n\n"
            "Demo: We encrypted 'business_letter.txt' and 'invoice.txt'. Files have now been restored. Click icons to inspect:"
        )
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Next", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        file1_label = tk.Label(self.master, image=self.file_icon_tk, text="business_letter.txt", compound="top", bg=self.BG_COLOR, fg=self.TEXT_COLOR, 
                               font=("Courier New", self.SMALL_FONT_SIZE), cursor="hand2")  # Using consistent font size
        file1_label.bind("<Button-1>", lambda e: self.inspect_restored_file("business_letter.txt"))
        
        file2_label = tk.Label(self.master, image=self.file_icon_tk, text="invoice.txt", compound="top", bg=self.BG_COLOR, fg=self.TEXT_COLOR, 
                               font=("Courier New", self.SMALL_FONT_SIZE), cursor="hand2")  # Using consistent font size
        file2_label.bind("<Button-1>", lambda e: self.inspect_restored_file("invoice.txt"))
        
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800),  # Increased for larger text
                        self.canvas.create_window(300, 500, anchor="center", window=file1_label),
                        self.canvas.create_window(700, 500, anchor="center", window=file2_label)]
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]

    def show_sources(self):
        text = (
            "Sources and resources\n\n"
            "1. Cryptographic ransomware encryption detection: Survey -- https://www.sciencedirect.com/science/article/pii/S0167404823002596\n"
            "2. Ransomware: Recent advances, analysis, challenges and future research directions -- https://pmc.ncbi.nlm.nih.gov/articles/PMC8463105/\n"
            "3. Ransomware: Minimizing the Risks -- https://pmc.ncbi.nlm.nih.gov/articles/PMC5300711/\n"
            "4. STOPRANSOMWARE -- https://www.cisa.gov/stopransomware\n"
        )
        self.current_text = text
        encrypted_text = self.encryptAES(text, self.aes_key)
        
        text_widget = tk.Text(self.master, wrap="word", font=("Courier New", self.TEXT_FONT_SIZE), bg=self.BG_COLOR, fg=self.TEXT_COLOR, borderwidth=2, 
                              relief="flat", spacing1=6, spacing2=3, spacing3=6)  # Increased spacing
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        back_button = tk.Button(self.master, text="Back", command=self.back_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG, 
                                relief="flat", padx=12, pady=6)  # Increased padding
        next_button = tk.Button(self.master, text="Finish", command=self.next_page, font=("Courier New", self.BUTTON_FONT_SIZE), bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                                relief="flat", padx=12, pady=6)  # Increased padding
        
        self.current_text_widget = text_widget
        self.canvas_items = [self.canvas.create_window(20, 20, anchor="nw", window=text_widget, width=1060, height=800)]  # Increased for larger text
        self.button_items = [self.canvas.create_window(400, 780, anchor="s", window=back_button),
                        self.canvas.create_window(600, 780, anchor="s", window=next_button)]
        self.master.after(100, lambda: self.slow_decrypt_text(text_widget, encrypted_text, text))
        
    def show_final_page(self):
        """Display the final page of the demo and set a timer to exit."""
        self.canvas.delete("all")
        self.draw_background()
        print("Final page displayed with larger font sizes")
        self.master.after(10000, self.fade_out_final)  # Display for 10 seconds, then fade
        
    def fade_out_final(self, alpha=1.0, step=0.05):
        """Gradually fade out the final page and exit the application."""
        if alpha <= 0:
            self.canvas.delete(self.bg_image_id)
            self.master.quit()
            return
        
        self.master.after(50, lambda a=alpha-step, s=step: self.fade_out_final(a, s))

    # Animation functions
    def fade_out(self, items, alpha=1.0, step=0.05):
        """Gradually fade out the specified canvas items and load the next page."""
        if alpha <= 0:
            self.load_next_page()
            return
        for item in items:
            self.canvas.itemconfig(item, state="hidden")
        self.master.after(50, lambda a=alpha-step, s=step: self.fade_out(items, a, s))

    def slow_encrypt_text(self, text_widget, original_text, current_pos=0, step=3):
        """Animate text encryption by gradually replacing characters with random ones."""
        if current_pos >= len(original_text):
            self.master.after(500, lambda: self.fade_out(self.canvas_items))
            return

        text_widget.config(state="normal")
        encrypted_chars = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) 
                                for _ in range(min(step, len(original_text) - current_pos)))
        text_widget.delete(f"1.{current_pos}", f"1.{current_pos + min(step, len(original_text) - current_pos)}")
        text_widget.insert(f"1.{current_pos}", encrypted_chars)
        text_widget.config(state="disabled")
        
        self.master.after(5, lambda cp=current_pos+step: self.slow_encrypt_text(text_widget, original_text, cp, step))
    
    def slow_decrypt_text(self, text_widget, encrypted_text, original_text, current_pos=0, step=3):
        """Animate text decryption by gradually revealing the original text."""
        if current_pos >= len(original_text):
            return

        text_widget.config(state="normal")
        text_widget.delete(f"1.{current_pos}", f"1.{current_pos + min(step, len(original_text) - current_pos)}")
        text_widget.insert(f"1.{current_pos}", original_text[current_pos:current_pos + min(step, len(original_text) - current_pos)])
        text_widget.config(state="disabled")
        
        self.master.after(5, lambda cp=current_pos+step: self.slow_decrypt_text(text_widget, encrypted_text, original_text, cp, step))
