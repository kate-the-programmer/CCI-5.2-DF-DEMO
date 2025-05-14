import tkinter as tk
from tkinter import ttk, font, messagebox
import subprocess
import os
import platform
from PIL import Image, ImageTk

# Import modules with error handling
try:
    import raid
    import ransom
except ImportError as e:
    print(f"Error importing module: {e}")
except Exception as e:
    print(f"Unexpected error during import: {e}")
class DigitalForensicsDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Forensics Demo")
        self.geometry("800x600")
        self.configure(bg="#000000")  # Black background
        self.image_label = None  # Will store the image widget when needed
        
        # Define summary texts for each demo
        self.autopsy_summary = "Autopsy is a powerful open-source digital forensics platform used by law enforcement, military, and corporate examiners to investigate what happened on a computer. It provides a comprehensive, graphical interface to analyze disk images, perform file recovery, browse file systems, and search for specific content. Autopsy can recover deleted files, extract metadata, analyze browser history, detect malware, create timelines of events, and index files for keyword searches. It's an essential tool for digital evidence collection, incident response, and legal investigations."
        self.raid_summary = "RAID (Redundant Array of Independent Disks) recovery is a critical process for retrieving data from damaged or failed RAID arrays. RAID systems distribute data across multiple drives for redundancy, performance, or both. When drives fail or arrays become corrupted, specialized recovery techniques are needed to reconstruct the data. This demo showcases methods for identifying RAID parameters (level, stripe size, disk order), rebuilding virtual arrays, handling partial failures, and extracting data from compromised RAID systems — essential skills for data recovery professionals and incident responders."
        self.writeblocker_summary = "Write Blockers are specialized hardware devices that create a read-only connection between a storage device (like a hard drive or USB drive) and a forensic workstation. They prevent any write commands from reaching the target storage device, ensuring that no data is altered during forensic acquisition and analysis. This maintains the integrity of digital evidence, prevents contamination of the original media, and helps ensure admissibility in legal proceedings. Write blockers are fundamental tools in the digital forensic process, allowing investigators to create exact duplicates of storage media while preserving the chain of custody."
        self.ransomware_summary = "Ransomware is a type of malicious software that encrypts files on a victim's computer, making them inaccessible, and demands a ransom payment to restore access. This demonstration explores ransomware attack vectors, encryption techniques, file system impacts, and defense strategies. It also covers digital forensic approaches to ransomware incident response, including affected file identification, timeline creation, possible decryption options, and preventative measures. Understanding ransomware is essential for security professionals to protect systems and respond effectively to attacks."
        self.default_summary = "Select a demo option below to see its description and proceed with the demonstration."
        
        # Configure the style for all widgets
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure colors for ttk widgets
        self.style.configure('TFrame', background='#000000')
        self.style.configure('TLabel', 
                             background='#000000', 
                             foreground='#00FF00', 
                             font=('Courier', 12))
        self.style.configure('TButton', 
                             background='#000000', 
                             foreground='#00FF00', 
                             font=('Courier', 12),
                             borderwidth=0,  # No border on the button itself
                             relief='flat')  # Flat relief for the button
        # Add border color for buttons
        self.style.map('TButton',
                       background=[('active', '#003300')],
                       foreground=[('active', '#00FF00')])
                       
        # Configure Custom.TButton style with hover effects
        self.style.configure('Custom.TButton', 
                             background='#000000',
                             foreground='#00FF00',
                             font=('Courier', 12),
                             borderwidth=1,
                             relief='ridge')
                             
        # Configure hover effects for Custom.TButton
        self.style.map('Custom.TButton',
                       background=[('active', '#111111')],
                       foreground=[('active', '#FFFFFF')],
                       relief=[('active', 'ridge'), ('pressed', 'groove')])
                       
        # COMMENTED OUT: Green border frame styling - kept for future reference
        # self.style.configure('Green.TFrame', 
        #                     background='#00FF00',  # Bright green
        #                     borderwidth=3,  # Increased border width
        #                     relief='solid')  # Solid relief for visible borders
        
        # Create a frame style for button containers with top-left border effect
        self.style.configure('TopLeft.TFrame',
                            background='#000000')
        
        # Update Custom.TButton with padding
        self.style.configure('Custom.TButton', 
                            padding=(6, 6, 4, 4))  # More padding on left/top, less on right/bottom 
                            
        # Update Custom.TButton map to handle disabled state
        self.style.map('Custom.TButton',
                      background=[('active', '#111111'), ('disabled', '#1a1a1a')],
                      foreground=[('active', '#FFFFFF'), ('disabled', '#005500')],
                      relief=[('active', 'ridge'), ('pressed', 'groove')])
        # Store the original ttk.Button class for later use
        self.original_button = ttk.Button
        
        self.style.configure('TEntry', 
                             fieldbackground='#000000', 
                             foreground='#00FF00', 
                             insertcolor='#00FF00',
                             font=('Courier', 12))
        self.style.configure('TEntry', 
                             fieldbackground='#000000', 
                             foreground='#00FF00', 
                             insertcolor='#00FF00',
                             font=('Courier', 12))
        # Create the main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Create and setup widgets
        self.setup_widgets()
        
        # Bind the Return/Enter key to process commands
        self.cmd_entry.bind('<Return>', lambda e: self.process_command())
    
    def create_styled_button(self, parent, text, command=None, **kwargs):
        """Create a styled button with subtle top and left borders"""
        # Create a frame to hold the button and provide custom border effect
        button_frame = ttk.Frame(parent, style='TopLeft.TFrame')
        
        # Set the custom button style
        if 'style' not in kwargs:
            kwargs['style'] = 'Custom.TButton'
        
        # Create the button with subtle top-left borders
        button = ttk.Button(button_frame, text=text, command=command, **kwargs)
        button.pack(fill=tk.BOTH, expand=True)
        
        # Store reference to frame to prevent garbage collection
        button._frame = button_frame
        
        return button_frame
        
        # COMMENTED OUT: Original button with green border implementation
        # Below is the original implementation with green borders, kept for reference
        """
        # Create a frame with green border to hold the button
        border_frame = tk.Frame(parent, bg="#00FF00", highlightthickness=0, bd=0)
        
        # Border thickness in pixels
        border_size = 3
        
        # Create inner frame for the black background
        inner_frame = tk.Frame(border_frame, bg="#000000", highlightthickness=0)
        inner_frame.pack(padx=border_size, pady=border_size, fill=tk.BOTH, expand=True)
        
        # Create the button with custom style
        if 'style' not in kwargs:
            kwargs['style'] = 'Custom.TButton'
        
        button = self.original_button(inner_frame, text=text, command=command, **kwargs)
        button.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Store references to prevent garbage collection
        button._border_frame = border_frame
        button._inner_frame = inner_frame
        
        # Create highlight effect when mouse hovers over button
        def on_enter(e):
            border_frame.config(bg="#00FF99")  # Slightly different green for hover
            
        def on_leave(e):
            border_frame.config(bg="#00FF00")  # Return to original green
            
        # Bind events to button
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        # Update button state change to reflect in border color
        original_state = button.state
        
        def custom_state(*args):
            result = original_state(*args)
            if args and border_frame.winfo_exists():
                if 'disabled' in args[0]:
                    border_frame.config(bg="#005500")  # Darker green for disabled
                else:
                    border_frame.config(bg="#00FF00")  # Regular green for normal
            return result
        
        # Replace the state method with our custom version
        button.state = custom_state
        
        return border_frame
        """
        
    def setup_widgets(self):
        """Setup all the widgets for the GUI"""
        # Create a custom font for the title
        title_font = font.Font(family='Courier', size=20, weight='bold')
        # Title label
        self.title_label = tk.Label(self.main_frame,
                             text="Welcome to the Digital Forensics Demo",
                             bg="#000000",
                             fg="#00FF00",
                             font=title_font,
                             cursor="hand2")
        self.title_label.pack(pady=(0, 30))
        self.title_label.bind("<Button-1>", lambda e: self.handle_title_click())
        
        # Command input label
        cmd_label = ttk.Label(self.main_frame, text="Type a command to begin:")
        cmd_label.pack(anchor='w', pady=(0, 5))
        
        # Command input entry
        self.cmd_entry = ttk.Entry(self.main_frame, width=50)
        self.cmd_entry.pack(fill=tk.X, pady=(0, 20))
        self.cmd_entry.focus_set()
        
        # Summary text widget
        summary_frame = ttk.Frame(self.main_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        summary_label = ttk.Label(summary_frame, text="Demo Summary:")
        summary_label.pack(anchor='w', pady=(0, 5))
        
        self.summary_text = tk.Text(summary_frame, 
                                    height=4, 
                                    bg="#000000", 
                                    fg="#00FF00", 
                                    font=('Courier', 12),
                                    wrap=tk.WORD,
                                    bd=1,
                                    relief=tk.SOLID)
        self.summary_text.pack(fill=tk.X, expand=True)
        self.summary_text.insert(tk.END, self.default_summary)
        self.summary_text.config(state=tk.DISABLED)
        
        # Create button frame for better layout
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        # Create the demo buttons with green borders
        self.autopsy_btn = self.create_styled_button(self.button_frame, text="Autopsy", command=self.handle_autopsy)
        self.autopsy_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        self.raid_btn = self.create_styled_button(self.button_frame, text="RAID", command=self.handle_raid)
        self.raid_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.writeblocker_btn = self.create_styled_button(self.button_frame, text="Write Blocker", command=self.handle_writeblocker)
        self.writeblocker_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.ransomware_btn = self.create_styled_button(self.button_frame, text="Ransomware", command=self.handle_ransomware)
        self.ransomware_btn.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)
        
        # Autopsy options frame - initially hidden
        self.autopsy_options_frame = ttk.Frame(self.main_frame)
        self.autopsy_options_frame.pack(fill=tk.X, pady=10)
        self.autopsy_options_frame.pack_forget()  # Hide initially
        
        # Instructions label for Autopsy options
        instructions_label = tk.Label(self.autopsy_options_frame,
                                    text="Select an Autopsy option to continue:",
                                    bg="#000000",
                                    fg="#00FF00",
                                    font=('Courier', 12))
        instructions_label.pack(pady=(0, 10))
        
        # Button frame for Autopsy options
        autopsy_button_frame = ttk.Frame(self.autopsy_options_frame)
        autopsy_button_frame.pack(fill=tk.X)
        
        # View Documentation button
        self.doc_button = self.create_styled_button(autopsy_button_frame, 
                                   text="View Documentation", 
                                   command=self.view_autopsy_documentation)
        self.doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        # Launch Kali button
        self.kali_button = self.create_styled_button(autopsy_button_frame, 
                                    text="Launch Kali Linux", 
                                    command=self.launch_kali)
        self.kali_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)
        
        # RAID options frame - initially hidden
        self.raid_options_frame = ttk.Frame(self.main_frame)
        self.raid_options_frame.pack(fill=tk.X, pady=10)
        self.raid_options_frame.pack_forget()  # Hide initially
        
        # Instructions label for RAID options
        raid_instructions_label = tk.Label(self.raid_options_frame,
                                    text="Select a RAID option to continue:",
                                    bg="#000000",
                                    fg="#00FF00",
                                    font=('Courier', 12))
        raid_instructions_label.pack(pady=(0, 10))
        
        # Button frame for RAID options
        raid_button_frame = ttk.Frame(self.raid_options_frame)
        raid_button_frame = ttk.Frame(self.raid_options_frame)
        raid_button_frame.pack(fill=tk.X)
        
        # View Documentation button for RAID
        self.raid_doc_button = self.create_styled_button(raid_button_frame, 
                                   text="View Documentation", 
                                   command=self.view_raid_documentation)
        self.raid_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        # Launch RAID GUI button
        self.raid_gui_button = self.create_styled_button(raid_button_frame, 
                                    text="Launch RAID GUI", 
                                    command=self.launch_raid_gui)
        self.raid_gui_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)
        # Write Blocker options frame - initially hidden
        self.writeblocker_options_frame = ttk.Frame(self.main_frame)
        self.writeblocker_options_frame.pack(fill=tk.X, pady=10)
        self.writeblocker_options_frame.pack_forget()  # Hide initially
        
        # Instructions label for Write Blocker options
        writeblocker_instructions_label = tk.Label(self.writeblocker_options_frame,
                                    text="Select a Write Blocker option to continue:",
                                    bg="#000000",
                                    fg="#00FF00",
                                    font=('Courier', 12))
        writeblocker_instructions_label.pack(pady=(0, 10))
        
        # Button frame for Write Blocker options
        writeblocker_button_frame = ttk.Frame(self.writeblocker_options_frame)
        writeblocker_button_frame.pack(fill=tk.X)
        
        # View Documentation button
        self.writeblocker_doc_button = self.create_styled_button(writeblocker_button_frame, 
                                   text="View Documentation", 
                                   command=self.view_writeblocker_documentation)
        self.writeblocker_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        # Launch Write Blocker GUI button
        self.writeblocker_gui_button = self.create_styled_button(writeblocker_button_frame, 
                                    text="Launch Write Blocker GUI", 
                                    command=self.launch_writeblocker_gui)
        self.writeblocker_gui_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)
        
        # Ransomware options frame - initially hidden
        self.ransomware_options_frame = ttk.Frame(self.main_frame)
        self.ransomware_options_frame.pack(fill=tk.X, pady=10)
        self.ransomware_options_frame.pack_forget()  # Hide initially
        
        # Instructions label for Ransomware options
        ransomware_instructions_label = tk.Label(self.ransomware_options_frame,
                                    text="Select a Ransomware option to continue:",
                                    bg="#000000",
                                    fg="#00FF00",
                                    font=('Courier', 12))
        ransomware_instructions_label.pack(pady=(0, 10))
        
        # Button frame for Ransomware options
        ransomware_button_frame = ttk.Frame(self.ransomware_options_frame)
        ransomware_button_frame.pack(fill=tk.X)
        
        # View Documentation button
        self.ransomware_doc_button = self.create_styled_button(ransomware_button_frame, 
                                   text="View Documentation", 
                                   command=self.view_ransomware_documentation)
        self.ransomware_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        # Launch Ransomware Demo button
        self.ransomware_demo_button = self.create_styled_button(ransomware_button_frame, 
                                    text="Launch Ransomware Demo", 
                                    command=lambda: self.launch_ransomware_demo('ransomware_demo_button'))
        self.ransomware_demo_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)
        # Output text area
        # Output text area
        # # Add a separator between main buttons and the standalone ransomware button
        # separator = ttk.Frame(self.main_frame, height=2, style='TSeparator')
        # separator.pack(fill=tk.X, pady=15)
        # # Create a frame for the standalone ransomware button with a border
        # ransomware_standalone_frame = ttk.Frame(self.main_frame, style='Danger.TFrame')
        # ransomware_standalone_frame.pack(fill=tk.X, pady=5)
        
        # # Add warning label above the button
        # warning_label = tk.Label(
        #     ransomware_standalone_frame,
        #     text="⚠️ Educational Ransomware Demonstration ⚠️",
        #     font=('Courier', 12),
        #     bg='#000000',
        #     fg='#FF0000'
        # )
        # warning_label.pack(pady=(0, 5))
        
        # Create the standalone ransomware button with updated styling
        # self.standalone_ransomware_btn = tk.Button(
        #     ransomware_standalone_frame,
        #     text="Launch Ransomware Demo",
        #     font=('Courier', 14, 'bold'),
        #     bg='#FF0000',
        #     fg='#FFFFFF',
        #     activebackground='#CC0000',
        #     activeforeground='#FFFFFF',
        #     relief='raised',
        #     borderwidth=2,
        #     command=self.launch_standalone_ransomware
        # )
        # self.standalone_ransomware_btn.pack(expand=True, fill=tk.X, padx=100, pady=5)
        
        # Add hover effect for the standalone button
        # def on_enter(e):
        #     if str(self.standalone_ransomware_btn['state']) != 'disabled':
        #         self.standalone_ransomware_btn.configure(
        #             bg='#CC0000',
        #             relief='sunken'
        #         )
            
        # def on_leave(e):
        #     if str(self.standalone_ransomware_btn['state']) != 'disabled':
        #         self.standalone_ransomware_btn.configure(
        #             bg='#FF0000',
        #             relief='raised'
        #         )
        
        # self.standalone_ransomware_btn.bind("<Enter>", on_enter)
        # self.standalone_ransomware_btn.bind("<Leave>", on_leave)
        # Output text area
        self.output_text = tk.Text(self.main_frame, 
                                height=15, 
                                bg="#000000", 
                                fg="#00FF00", 
                                insertbackground="#00FF00")
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        self.output_text.config(state=tk.DISABLED)
        
    def handle_autopsy(self):
        self.update_summary(self.autopsy_summary)
        self.display_output("Preparing Autopsy digital forensics options...")
        
        # Hide all option frames and then show only Autopsy options
        # hide_all_option_frames also removes any displayed image
        self.hide_all_option_frames()
        self.autopsy_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    def view_autopsy_documentation(self):
        """Open the Autopsy documentation PDF file"""
        self.display_output("Opening Autopsy documentation PDF...")
        pdf_filename = "Step-by-Step Guide_ Using Autopsy.pdf"
        
        try:
            # Check if the file exists
            if not os.path.exists(pdf_filename):
                raise FileNotFoundError(f"PDF file '{pdf_filename}' not found")
            
            # Open PDF file with the default system viewer
            if platform.system() == 'Windows':
                os.startfile(pdf_filename)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_filename])
            else:  # Linux/Unix
                subprocess.run(['xdg-open', pdf_filename])
                
            self.display_output(f"Successfully opened {pdf_filename}")
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error opening PDF: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def launch_kali(self):
        """Launch Kali Linux or relevant forensic tools"""
        self.display_output("Attempting to launch Kali Linux environment...")
        
        try:
            # This is a placeholder - when deployed on the Pi, 
            # replace with the actual command to launch Kali
            if platform.system() == 'Windows':
                # For Windows testing - display a message
                self.display_output("Kali Linux launching is simulated in Windows environment")
                messagebox.showinfo("Kali Linux", "In the Raspberry Pi environment, this would launch Kali Linux with Autopsy.")
            else:
                # For Linux (Raspberry Pi) - this would be the actual command
                # Replace with the correct command for your Pi setup
                subprocess.run(['bash', '-c', 'echo "Launching Kali Linux with Autopsy..."'])
                self.display_output("Kali Linux environment started successfully")
        except Exception as e:
            error_msg = f"Error launching Kali Linux: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
        
    def view_raid_documentation(self):
        """Open the RAID documentation Markdown file"""
        self.display_output("Opening RAID documentation...")
        md_filename = "README.md"
        
        try:
            # Check if the file exists
            if not os.path.exists(md_filename):
                raise FileNotFoundError(f"Markdown file '{md_filename}' not found")
            
            # Open Markdown file with the default system viewer
            if platform.system() == 'Windows':
                os.startfile(md_filename)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', md_filename])
            else:  # Linux/Unix
                subprocess.run(['xdg-open', md_filename])
                
            self.display_output(f"Successfully opened {md_filename}")
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error opening Markdown file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def launch_raid_gui(self):
        """Launch RAID GUI visualization"""
        self.display_output("Launching RAID visualization module...")
        
        try:
            # Create the Toplevel window first
            raid_toplevel = tk.Toplevel(self)
            # Create the RAID visualization app with the Toplevel window
            raid_window = raid.RAIDVisualizationApp(raid_toplevel)
            self.display_output("RAID visualization started successfully")
            
            # Handle window close properly
            raid_toplevel.protocol("WM_DELETE_WINDOW", lambda: self.on_raid_window_close(raid_toplevel))
            
            # Force focus on the new window
            raid_toplevel.focus_force()
            
        except Exception as e:
            error_msg = f"Error launching RAID visualization: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def on_raid_window_close(self, window):
        """Handle proper cleanup when the RAID window is closed"""
        try:
            self.display_output("RAID visualization window closed")
            window.destroy()
        except Exception as e:
            pass  # Silently handle any errors during window cleanup
            
    def handle_raid(self):
        self.update_summary(self.raid_summary)
        self.display_output("Initializing RAID recovery tools...")
        
        # Hide all option frames and then show only RAID options
        # hide_all_option_frames also removes any displayed image
        self.hide_all_option_frames()
        self.raid_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    def handle_writeblocker(self):
        self.update_summary(self.writeblocker_summary)
        self.display_output("Preparing Write Blocker options...")
        
        # Hide all option frames and then show only Write Blocker options
        # hide_all_option_frames also removes any displayed image
        self.hide_all_option_frames()
        
        # Show Write Blocker options
        self.writeblocker_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    def view_writeblocker_documentation(self):
        """Open the Write Blocker documentation PDF file"""
        self.display_output("Opening Write Blocker documentation PDF...")
        pdf_filename = "Write_Blocker_Documentation.pdf"
        
        try:
            # Check if the file exists
            if not os.path.exists(pdf_filename):
                raise FileNotFoundError(f"PDF file '{pdf_filename}' not found")
            
            # Open PDF file with the default system viewer
            if platform.system() == 'Windows':
                os.startfile(pdf_filename)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_filename])
            else:  # Linux/Unix
                subprocess.run(['xdg-open', pdf_filename])
                
            self.display_output(f"Successfully opened {pdf_filename}")
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error opening PDF: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def launch_writeblocker_gui(self):
        """Launch Write Blocker GUI or relevant tools"""
        self.display_output("Attempting to launch Write Blocker tools...")
        
        try:
            # This is a placeholder - when deployed on the Pi, 
            # replace with the actual command to launch Write Blocker tools
            if platform.system() == 'Windows':
                # For Windows testing - display a message
                self.display_output("Write Blocker GUI launching is simulated in Windows environment")
                messagebox.showinfo("Write Blocker GUI", "In the Raspberry Pi environment, this would launch the Write Blocker tools.")
            else:
                # For Linux (Raspberry Pi) - this would be the actual command
                # Replace with the correct command for your Pi setup
                subprocess.run(['bash', '-c', 'echo "Launching Write Blocker tools..."'])
                self.display_output("Write Blocker tools started successfully")
        except Exception as e:
            error_msg = f"Error launching Write Blocker tools: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
        
    def handle_ransomware(self):
        self.update_summary(self.ransomware_summary)
        self.display_output("Preparing Ransomware demonstration options...")
        
        # Hide all option frames and then show only Ransomware options
        self.hide_all_option_frames()
        self.ransomware_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    def view_ransomware_documentation(self):
        """Open the Ransomware documentation PDF file"""
        self.display_output("Opening Ransomware documentation PDF...")
        pdf_filename = "Ransomware_Documentation.pdf"
        
        try:
            # Check if the file exists
            if not os.path.exists(pdf_filename):
                raise FileNotFoundError(f"PDF file '{pdf_filename}' not found")
            
            # Open PDF file with the default system viewer
            if platform.system() == 'Windows':
                os.startfile(pdf_filename)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_filename])
            else:  # Linux/Unix
                subprocess.run(['xdg-open', pdf_filename])
                
            self.display_output(f"Successfully opened {pdf_filename}")
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error opening PDF: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def manage_ransomware_buttons(self, state='normal'):
        """Enable or disable all ransomware launch buttons
        Args:
            state: The state to set the buttons to ('normal' or 'disabled')
        """
        if hasattr(self, 'ransomware_demo_button'):
            try:
                button = self.ransomware_demo_button.winfo_children()[0]  # Get the actual button from the frame
                button.configure(state=state)
            except (IndexError, AttributeError) as e:
                print(f"Error configuring ransomware_demo_button: {e}")
        
        if hasattr(self, 'standalone_ransomware_btn'):
            try:
                self.standalone_ransomware_btn.configure(state=state)
            except tk.TclError as e:
                print(f"Error configuring standalone_ransomware_btn: {e}")

    def initialize_ransomware_files(self):
        """Initialize the required files for the ransomware demo"""
        try:
            self.display_output("Initializing ransomware demo files...")
            test_files = {
                "business_letter.txt": "Dear Client,\nWe are pleased to offer you a contract worth $500,000 for Q3 2025.\nRegards,\nBusiness Inc.",
                "invoice.txt": "Invoice #1234\n50 units of Product X at $200 each\nTotal: $10,000\nDue: 04/01/2025"
            }
            
            created = []
            for filename, content in test_files.items():
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        f.write(content)
                    with open(f"{filename}.bak", 'w') as f:
                        f.write(content)
                    created.append(filename)
            
            if created:
                self.display_output(f"Created demo files: {', '.join(created)}")
            else:
                self.display_output("Demo files already exist")
                
            return True, "Files initialized successfully"
        except Exception as e:
            return False, str(e)

    def launch_ransomware_demo(self, source_button=None):
        """Launch Ransomware Demo visualization
        Args:
            source_button: The button that triggered the demo (for state management)
        """
        self.display_output("Launching Ransomware demonstration...")
        try:
            # Initialize sample files
            success, files_created = self.initialize_ransomware_files()
            if not success:
                raise Exception(f"Failed to initialize files: {files_created}")
                
            # Create new window for ransomware demo
            ransomware_window = tk.Toplevel(self)
            ransomware_window.title("Ransomware Demonstration")
            ransomware_window.geometry("1100x880")
            
            # Create the ransomware demo instance
            demo = ransom.RansomwareDemo(ransomware_window)
            
            # Store reference to prevent garbage collection
            self._ransomware_demo = demo
            
            # Configure window
            ransomware_window.lift()
            ransomware_window.focus_force()
            
            # Disable all ransomware buttons while demo is running
            self.manage_ransomware_buttons('disabled')
            # Handle window closing
            def on_window_close():
                self.on_ransomware_window_close(ransomware_window, source_button)
                    
            ransomware_window.protocol("WM_DELETE_WINDOW", on_window_close)
            
        except Exception as e:
            error_msg = f"Error launching Ransomware demonstration: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            # Re-enable all ransomware buttons if there was an error
            self.manage_ransomware_buttons('normal')
    def on_ransomware_window_close(self, window, source_button=None):
        """Handle proper cleanup when the ransomware demo window is closed
        Args:
            window: The window to close
            source_button: The button that launched the demo (for state management)
        """
        try:
            self.display_output("Ransomware demo window closed")
            
            # Re-enable all ransomware buttons
            self.manage_ransomware_buttons('normal')
            window.destroy()
        except Exception as e:
            # Log any errors during cleanup but don't show to user
            print(f"Error during window cleanup: {str(e)}")
    
    # def launch_standalone_ransomware(self):
    #     """Launch Ransomware Demo from the standalone button"""
    #     self.launch_ransomware_demo('standalone_ransomware_btn')
        
    def handle_meow(self):
        
        cat_art = """
         /\\___/\\
        (  o o  )
        (  =^=  ) 
          (__)
        """
        self.display_output("MEOW! You found the secret cat! \U0001F431")
        self.display_output(cat_art)
        self.cmd_entry.delete(0, tk.END)
        
    def process_command(self):
        command = self.cmd_entry.get().strip().lower()
        # Hide all option frames when a command is processed
        self.hide_all_option_frames()
        
        # Only remove currently displayed image for non-image commands
        if command != "hakercat":
            self.remove_displayed_image()
            
        if command == "meow":
            self.handle_meow()
        elif command == "hakercat":
            self.display_output("HakerCat activated! Displaying Meow-Frame...")
            self.display_image("Meow-Frame.webp")
        self.cmd_entry.delete(0, tk.END)
    
    def update_summary(self, summary_text):
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
        self.summary_text.config(state=tk.DISABLED)
        
    def display_output(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f">> {message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def display_image(self, image_path):
        """Display an image in the GUI"""
        try:
            # First, ensure any existing image is removed
            self.remove_displayed_image()
            
            # Check if the file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file '{image_path}' not found")
            
            # Load and resize the image
            img = Image.open(image_path)
            width, height = img.size
            max_width = 500
            max_height = 400
            
            # Resize if the image is too large while maintaining aspect ratio
            if width > max_width or height > max_height:
                ratio = min(max_width/width, max_height/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            photo = ImageTk.PhotoImage(img)
            
            # Create new label with the image
            self.image_label = tk.Label(self.main_frame, image=photo, bg="#000000")
            self.image_label.image = photo  # Keep a reference to prevent garbage collection
            self.image_label.pack(pady=10, before=self.output_text)
            
            # Image displayed successfully - no need for output message
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error displaying image: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def remove_displayed_image(self):
        """Remove any currently displayed image"""
        if self.image_label is not None:
            self.image_label.destroy()
            self.image_label = None

    def hide_all_option_frames(self):
        """Hide all option frames to ensure only relevant UI elements are visible"""
        self.autopsy_options_frame.pack_forget()
        self.raid_options_frame.pack_forget()
        self.writeblocker_options_frame.pack_forget()
        self.ransomware_options_frame.pack_forget()
        # Also remove any displayed image for a clean UI state
        self.remove_displayed_image()
        
    def handle_title_click(self):
        """Display the Cyber Ring image when the title is clicked"""
        self.display_output("The one GUI to rule them all!")
        self.display_image("Cyber Rring Edited 2.PNG")

if __name__ == "__main__":
    app = DigitalForensicsDemo()
    app.mainloop()

