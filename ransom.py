import tkinter as tk
from tkinter import messagebox
import random
import string
from cryptography.fernet import Fernet
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os

# Core encryption/decryption functions
def writeAESKey(bits=128):
    key = get_random_bytes(bits//8)
    if bits == 128:
        writefile(key, "aes128_key.bin", is_binary=True)
    elif bits == 192:
        writefile(key, "aes192_key.bin", is_binary=True)
    elif bits == 256:
        writefile(key, "aes256_key.bin", is_binary=True)
    return key

def encryptAES(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    initialVector = cipher.iv
    if isinstance(message, str):
        message_bytes = message.encode('utf-8')
    else:
        message_bytes = message
    ciphertext = cipher.encrypt(pad(message_bytes, AES.block_size))
    return b64encode(initialVector + ciphertext)

def decryptAES(ciphertext, key):
    cipherData = b64decode(ciphertext)
    initialVector = cipherData[:AES.block_size]
    ciphertext = cipherData[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, initialVector)
    message = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return message

def readfile(filename, is_binary=False):
    mode = "rb" if is_binary else "r"
    encoding = None if is_binary else "utf-8"
    with open(filename, mode, encoding=encoding) as file:
        content = file.read()
        return content

def writefile(data, filename, is_binary=False):
    mode = "wb" if is_binary else "w"
    encoding = None if is_binary else "utf-8"
    with open(filename, mode, encoding=encoding) as file:
        if is_binary:
            file.write(data)
        else:
            file.write(data)

def getKey(filename):
    if filename.endswith('.pem'):
        return readfile(filename, is_binary=False)
    return readfile(filename, is_binary=True)

# Sample file setup
SAMPLE_FILE = "sample.txt"
BACKUP_FILE = "sample_backup.txt"
BUSINESS_FILES = ["resource1.mhtml", "resource2.mhtml"]  # Update to your actual .mhtml files

if not os.path.exists(SAMPLE_FILE):
    with open(SAMPLE_FILE, "w", encoding="utf-8") as f:
        f.write("This is a sample file to demonstrate a file configuration with 64 bytes of data.")
if not os.path.exists(BACKUP_FILE):
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write(readfile(SAMPLE_FILE))
for file in BUSINESS_FILES:
    if not os.path.exists(file):
        mhtml_content = (
            "MIME-Version: 1.0\n"
            "Content-Type: multipart/related; boundary=\"boundary\"\n\n"
            "--boundary\n"
            "Content-Type: text/html\n\n"
            f"<html><body><h1>{file}</h1><p>This is a placeholder for {file}.</p></body></html>\n"
            "--boundary--"
        )
        with open(file, "w", encoding="utf-8") as f:
            f.write(mhtml_content)
    backup_file = file + ".bak"
    if not os.path.exists(backup_file):
        with open(backup_file, "wb") as f:
            f.write(readfile(file, is_binary=True))

with open(SAMPLE_FILE, "rb") as f:
    file_data = f.read()
    print(f"File size: {len(file_data)} bytes")

# Window setup with hacker theme
root = tk.Tk()
root.title("Ransomware Attacks")
root.geometry("1000x800")
root.configure(bg="#1a1a1a")

# Cyber color scheme
BG_COLOR = "#1a1a1a"
TEXT_COLOR = "#FF0000"
BUTTON_BG = "#ff0000"
BUTTON_FG = "#000000"
ENTRY_BG = "#333333"

# Global variables
page = 0
aes_key = None
encrypted_files = {}
current_text_widget = None
current_text = ""
canvas_item_id = None

# Page navigation
def page_counter(increment=True):
    global page
    if increment:
        page += 1
    else:
        page -= 1
    return page

def animate_fall(widget_id, y_pos=20, target_y=900):
    canvas.move(widget_id, 0, 10)
    y_pos += 10
    if y_pos < target_y:
        root.after(20, animate_fall, widget_id, y_pos, target_y)
    else:
        canvas.delete("all")
        load_next_page()

def slow_encrypt_text(widget, text, step=0):
    if step >= len(text):
        root.after(500, lambda: animate_fall(canvas_item_id))
        return
    scrambled = list(text)
    for i in range(min(step, len(text))):
        if scrambled[i] not in '\n ':
            scrambled[i] = random.choice(string.printable)
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", ''.join(scrambled))
    widget.config(state="disabled")
    root.after(10, slow_encrypt_text, widget, text, step + 5)

def slow_decrypt_text(widget, encrypted_text, original_text, step=0):
    total_steps = 50
    if step >= total_steps:
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", original_text)
        widget.config(state="disabled")
        return
    fraction = step / total_steps
    display_text = list(encrypted_text.decode('utf-8'))
    for i in range(len(original_text)):
        if i < int(fraction * len(original_text)):
            display_text[i] = original_text[i]
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice(string.printable)
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", ''.join(display_text))
    widget.config(state="disabled")
    root.after(40, slow_decrypt_text, widget, encrypted_text, original_text, step + 1)

def load_next_page():
    global page
    page_counter(increment=True)
    draw_background()
    if page == 1:
        show_ransom_text()
    elif page == 2:
        show_ransom_attacks()
    elif page == 3:
        show_ransom_mitigation()
    elif page == 4:
        show_ransom_detection_techniques()
    elif page == 5:
        show_ransom_response_strategies()
    elif page == 6:
        show_ransom_critical_infrastructure()
    elif page == 7:
        show_ransomware_demo()
    elif page == 8:
        show_ransomware_encrypted()
    elif page == 9:
        show_ransomware_backup_recovery()
    elif page == 10:
        show_sources()
    else:
        page_reset()
        show_ransom_text()

def next_page():
    global current_text_widget
    if current_text_widget:
        slow_encrypt_text(current_text_widget, current_text)
    else:
        load_next_page()

def back_page():
    canvas.delete("all")
    page_counter(increment=False)
    draw_background()
    if page == 1:
        show_ransom_text()
    elif page == 2:
        show_ransom_attacks()
    elif page == 3:
        show_ransom_mitigation()
    elif page == 4:
        show_ransom_detection_techniques()
    elif page == 5:
        show_ransom_response_strategies()
    elif page == 6:
        show_ransom_critical_infrastructure()
    elif page == 7:
        show_ransomware_demo()
    elif page == 8:
        show_ransomware_encrypted()
    elif page == 9:
        show_ransomware_backup_recovery()
    elif page == 10:
        show_sources()
    else:
        page_reset()
        show_ransom_text()

def page_reset():
    global page
    page = 1

# Load background image
try:
    bg_image = Image.open("cyber_bg.png")
    bg_image = bg_image.resize((1000, 800), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
except FileNotFoundError:
    bg_photo = None

def draw_background():
    if bg_photo:
        canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    else:
        canvas.configure(bg=BG_COLOR)

def inspect_files():
    inspect_window = tk.Toplevel(root)
    inspect_window.title("MHTML File Inspection")
    inspect_window.geometry("800x600")
    inspect_window.configure(bg=BG_COLOR)

    frame = tk.Frame(inspect_window, bg=BG_COLOR)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(frame, wrap="word", font=("Courier New", 12), bg=BG_COLOR, fg=TEXT_COLOR, 
                          borderwidth=2, relief="flat", spacing1=5, yscrollcommand=scrollbar.set)
    text_widget.pack(fill=tk.BOTH, expand=True)

    scrollbar.config(command=text_widget.yview)

    for file in BUSINESS_FILES:
        try:
            content = readfile(file, is_binary=True)
            display_content = b64encode(content).decode('utf-8')[:500]  # Truncate to 500 chars
            text_widget.insert(tk.END, f"{file} (base64-encoded, truncated):\n{display_content}...\n(Full content available in file)\n\n")
        except Exception as e:
            text_widget.insert(tk.END, f"{file}: Error reading file - {str(e)}\n\n")
    
    text_widget.config(state="disabled")

# Page content
def show_ransom_text():
    global current_text_widget, current_text, aes_key, canvas_item_id
    if aes_key is None:
        aes_key = writeAESKey(bits=128)
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
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(500, 780, anchor="s", window=next_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_ransom_attacks():
    global current_text_widget, current_text, aes_key, canvas_item_id
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
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(400, 780, anchor="s", window=back_button)
    canvas.create_window(600, 780, anchor="s", window=next_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_ransom_mitigation():
    global current_text_widget, current_text, aes_key, canvas_item_id
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
        "- Develop an incident response plan to quickly respond to and recover from a ransomware attack.\n"
        "- Regularly test your backups and ensure they can be restored in the event of an attack.\n"
        "- Consider using data redundancy and encryption to protect sensitive information.\n"
        "- Monitor network traffic for signs of suspicious activity and unauthorized access.\n"
        "- Work with law enforcement and cybersecurity experts to investigate and respond to ransomware attacks."
    )
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(400, 780, anchor="s", window=back_button)
    canvas.create_window(600, 780, anchor="s", window=next_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_ransom_detection_techniques():
    global current_text_widget, current_text, aes_key, canvas_item_id
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
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(400, 780, anchor="s", window=back_button)
    canvas.create_window(600, 780, anchor="s", window=next_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_ransom_response_strategies():
    global current_text_widget, current_text, aes_key, canvas_item_id
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
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(400, 780, anchor="s", window=back_button)
    canvas.create_window(600, 780, anchor="s", window=next_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_ransom_critical_infrastructure():
    global current_text_widget, current_text, aes_key, canvas_item_id
    text = (
        "Ransomware and Critical Infrastructure\n\n"
        "Ransomware attacks on critical infrastructure can have severe consequences, including:\n"
        "- Disruption of essential services, such as electricity, water, and transportation.\n"
        "- Financial losses due to downtime, recovery costs, and ransom payments.\n"
        "- Compromised public safety and national security.\n"
        "- Damage to critical infrastructure systems, such as industrial control systems and emergency response networks.\n"
        "- Loss of public trust and confidence in government and private sector organizations.\n"
        "- Legal and regulatory consequences, including fines and penalties for failing to protect critical infrastructure.\n"
        "- Increased risk of future ransomware attacks and cyber threats against critical infrastructure.\n"
        "- Example: The 2021 Colonial Pipeline ransomware attack disrupted fuel supplies on the East Coast of the United States.\n"
        "- This attack highlighted the vulnerability of critical infrastructure to cyber threats and the need for enhanced cybersecurity measures.\n\n"
        "Critical Infrastructure Attack Vectors:\n"
        "- Phishing emails: Malicious emails sent to employees to gain system access.\n"
        "- Remote access: Exploiting vulnerabilities in remote access systems.\n"
        "- Supply chain attacks: Compromising third-party vendors to infiltrate systems.\n"
        "- Zero-day exploits: Leveraging unknown software/hardware vulnerabilities.\n"
        "- Social engineering: Manipulating employees to disclose sensitive information or grant access."
    )
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(400, 780, anchor="s", window=back_button)
    canvas.create_window(600, 780, anchor="s", window=next_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_ransomware_demo():
    global aes_key, encrypted_files, current_text_widget, current_text, canvas_item_id
    if aes_key is None:
        aes_key = writeAESKey(bits=128)

    text = (
        "How Does Ransomware Encrypt Files?\n\n"
        "Some ransomware uses symmetric encryption (e.g., AES) to encrypt files, using the same key for encryption and decryption. "
        "The attacker encrypts your files and demands a ransom for the key.\n\n"
        "Others use hybrid encryption: a symmetric key encrypts files, then an asymmetric key (e.g., RSA) encrypts the symmetric key. "
        "The ransom is for the asymmetric key.\n\n"
        "Here, we use AES to encrypt two sample business files: 'resource1.mhtml' and 'resource2.mhtml'. Click 'Encrypt' to see the results."
    )
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    encrypt_button = tk.Button(root, text="Encrypt", 
                               command=lambda: [set_encrypted_files(), next_page()], 
                               font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    inspect_button = tk.Button(root, text="Inspect Files", command=inspect_files, font=("Courier New", 12), 
                               bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(300, 780, anchor="s", window=back_button)
    canvas.create_window(450, 780, anchor="s", window=encrypt_button)
    canvas.create_window(600, 780, anchor="s", window=next_button)
    canvas.create_window(750, 780, anchor="s", window=inspect_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def set_encrypted_files():
    global encrypted_files, aes_key
    encrypted_files = {}
    for file in BUSINESS_FILES:
        content = readfile(file, is_binary=True)
        encrypted_files[file] = encryptAES(content, aes_key)
        with open(file, "wb") as f:
            f.write(b64decode(encrypted_files[file]))

def show_ransomware_encrypted():
    global current_text_widget, encrypted_files, current_text, aes_key, canvas_item_id
    if not encrypted_files:
        encrypted_files = {file: encryptAES(readfile(file, is_binary=True), aes_key) for file in BUSINESS_FILES}

    text = (
        "What a Victim Sees After Encryption\n\n"
        "Once ransomware encrypts your files, they become inaccessible. The encrypted contents of the sample files "
        "are now unreadable binary data (base64-encoded). Use 'Inspect Files' to see a sample:\n\n"
    )
    for file in BUSINESS_FILES:
        text += f"{file}: Encrypted data (base64-encoded)\n\n"
    text += (
        "Files like Word documents would either show gibberish, fail to open, or have a new extension (e.g., .locked). "
        "A ransom note (popping up now) demands payment for decryption."
    )
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    inspect_button = tk.Button(root, text="Inspect Files", command=inspect_files, font=("Courier New", 12), 
                               bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(350, 780, anchor="s", window=back_button)
    canvas.create_window(500, 780, anchor="s", window=next_button)
    canvas.create_window(650, 780, anchor="s", window=inspect_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)
    
    messagebox.showwarning(
        "Ransom Note",
        "Your files have been encrypted!\n\n"
        "To recover your data, send 0.5 Bitcoin to: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n"
        "Email proof of payment to: attacker@darkweb.com\n"
        "You have 48 hours, or your files will be lost forever!"
    )

def show_ransomware_backup_recovery():
    global current_text_widget, encrypted_files, current_text, aes_key, canvas_item_id
    if not encrypted_files:
        encrypted_files = {file: encryptAES(readfile(file, is_binary=True), aes_key) for file in BUSINESS_FILES}

    restored_texts = {}
    for file in BUSINESS_FILES:
        backup_file = file + ".bak"
        if os.path.exists(backup_file):
            restored_texts[file] = readfile(backup_file, is_binary=True)
            with open(file, "wb") as f:
                f.write(restored_texts[file])
        else:
            restored_texts[file] = b"No backup available."

    text = (
        "Recovering with Backups\n\n"
        "Backups are a key mitigation strategy against ransomware. Here’s how they work:\n"
        "- Regular backups (e.g., to an offline drive or cloud with versioning) preserve your data.\n"
        "- After an attack, isolate the system, remove the ransomware, and restore from a clean backup.\n\n"
        "Demo: We encrypted 'resource1.mhtml' and 'resource2.mhtml'. Below is the status after restoration:\n\n"
    )
    for file in BUSINESS_FILES:
        text += f"Encrypted {file}: Encrypted data (base64-encoded)\n"
        text += f"Restored {file}: Restored original data (base64-encoded sample in 'Inspect Files')\n\n"
    text += (
        "Key Practices:\n"
        "- Keep backups offline or air-gapped.\n"
        "- Test restores regularly.\n"
        "- Encrypt backups for security."
    )
    current_text = text
    encrypted_text = encryptAES(text, aes_key)
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Next", command=next_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    inspect_button = tk.Button(root, text="Inspect Files", command=inspect_files, font=("Courier New", 12), 
                               bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", padx=10, pady=5)
    
    current_text_widget = text_widget
    canvas_item_id = canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(350, 780, anchor="s", window=back_button)
    canvas.create_window(500, 780, anchor="s", window=next_button)
    canvas.create_window(650, 780, anchor="s", window=inspect_button)
    root.after(100, slow_decrypt_text, text_widget, encrypted_text, text)

def show_sources():
    text = (
        "Sources and resources\n\n"
        "1. Cryptographic ransomware encryption detection: Survey -- https://www.sciencedirect.com/science/article/pii/S0167404823002596\n"
        "2. Ransomware: Recent advances, analysis, challenges and future research directions -- https://pmc.ncbi.nlm.nih.gov/articles/PMC8463105/\n"
        "3. Ransomware: Minimizing the Risks -- https://pmc.ncbi.nlm.nih.gov/articles/PMC5300711/\n"
        "4. STOPRANSOMWARE -- https://www.cisa.gov/stopransomware\n"
        "5. Cyber Incident -- https://www.secretservice.gov/investigations/cyberincident \n"
        "6. I've Been Hit by Ransomware -- https://www.cisa.gov/stopransomware/ive-been-hit-ransomware\n"
        "7. Demo Resources: resource1.mhtml and resource2.mhtml\n"
    )
    
    text_widget = tk.Text(root, wrap="word", font=("Courier New", 14), bg=BG_COLOR, fg=TEXT_COLOR, borderwidth=2, 
                          relief="flat", spacing1=5, spacing2=2, spacing3=5)
    text_widget.insert("1.0", text)
    text_widget.config(state="disabled")
    
    back_button = tk.Button(root, text="Back", command=back_page, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG, 
                            relief="flat", padx=10, pady=5)
    next_button = tk.Button(root, text="Finish", command=root.quit, font=("Courier New", 12), bg=BUTTON_BG, fg=BUTTON_FG,
                            relief="flat", padx=10, pady=5)
    
    canvas.create_window(20, 20, anchor="nw", window=text_widget, width=960, height=720)
    canvas.create_window(500, 780, anchor="s", window=back_button)
    canvas.create_window(700, 780, anchor="s", window=next_button)

# GUI Layout
canvas = tk.Canvas(root, width=1000, height=800, bg=BG_COLOR, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

draw_background()
next_page()
root.mainloop()