import tkinter as tk
from tkinter import ttk, font, messagebox, Menu
import subprocess
import os
import platform
from PIL import Image, ImageTk
import shutil  # For file copy operations
import sys

# Add module directories to Python path
sys.path.append('./WriteBlocker')
sys.path.append('./JohnRipper')
sys.path.append('./RAID')
sys.path.append('./Ransomware')

# Import modules from their respective directories
import write_blocker_gui  # Import the write blocker GUI module
import john_ripper_gui  # Import the John the Ripper GUI module

# Import psutil for system resource monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("psutil module not found. System resource monitoring will be disabled.")
    PSUTIL_AVAILABLE = False

# Configuration section
USB_IMAGE_CONFIG = {
    "sample_image_name": "Demo_USB_image.img",  # Name of the sample USB image file
    "sample_image_path": "./Assets/",           # Path to the sample USB image (in Assets directory)
    "user_images_dir": "Assets/user_images/",   # Directory to store user-specified images
    "autopsy_import_dir": "/tmp/autopsy_import/" # Directory where Autopsy looks for images (Linux)
}

# Import modules with error handling
try:
    from RAID import raid
    from Ransomware import ransom
except ImportError as e:
    print(f"Error importing module: {e}")
except Exception as e:
    print(f"Unexpected error during import: {e}")
class DigitalForensicsDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Forensics Demo")
        # Track fullscreen state
        self.is_fullscreen = True
        # Set window to fullscreen mode
        if platform.system() == 'Windows':
            self.state('zoomed')  # Windows fullscreen
        else:
            self.attributes('-fullscreen', True)  # Linux/Mac fullscreen
        self.configure(bg="#000000")  # Black background
        self.image_label = None  # Will store the image widget when needed
        self.tooltip_windows = {}  # Dictionary to store tooltip windows
        self.current_status = "Ready"  # Current status message
        self.operation_start_time = None  # For tracking operation timing
        self.active_progress_tasks = {}  # Track active progress tasks
        # Define theme colors
        self.themes = {
            "dark": {
                "bg": "#000000",              # Black background
                "fg": "#00FF00",              # Bright green text
                "active_bg": "#333333",       # Dark gray for active elements
                "active_fg": "#FFFFFF",       # White for active text
                "disabled_fg": "#005500",     # Dark green for disabled text
                "button_bg": "#000000",       # Black button background
                "button_hover": "#111111",    # Slightly lighter black for hover
                "accent": "#00FF00",          # Green accent color
                "warning": "#FF0000",         # Red for warnings
                "tooltip_bg": "#333333",      # Tooltip background
                "entry_bg": "#000000",        # Text entry background
                "progress_fg": "#00FF00",     # Progress bar foreground
                "panel_bg": "#111111"         # Slightly lighter background for panels
            },
            "light": {
                "bg": "#F5F5F5",              # Light gray background
                "fg": "#006600",              # Dark green text
                "active_bg": "#CCFFCC",       # Light green for active elements
                "active_fg": "#000000",       # Black for active text
                "disabled_fg": "#AAAAAA",     # Gray for disabled text
                "button_bg": "#FFFFFF",       # White button background
                "button_hover": "#E6E6E6",    # Light gray for hover
                "accent": "#008800",          # Darker green accent color
                "warning": "#CC0000",         # Darker red for warnings
                "tooltip_bg": "#EEEEEE",      # Tooltip background
                "entry_bg": "#FFFFFF",        # Text entry background
                "progress_fg": "#008800",     # Progress bar foreground
                "panel_bg": "#E6E6E6"         # Slightly darker background for panels
            }
        }
        
        # Set initial theme
        self.current_theme = "dark"  # Default to dark theme
        self.load_theme_preference()  # Load saved preference if available
        
        # Create the menu bar
        self.create_menu_bar()
        # Define summary texts for each demo
        self.autopsy_summary = "Autopsy is a powerful open-source digital forensics platform used by law enforcement, military, and corporate examiners to investigate what happened on a computer. It provides a comprehensive, graphical interface to analyze disk images, perform file recovery, browse file systems, and search for specific content. Autopsy can recover deleted files, extract metadata, analyze browser history, detect malware, create timelines of events, and index files for keyword searches. This demo allows you to launch Autopsy directly and provides access to sample USB disk images for forensic analysis. You can download a pre-configured sample image or specify your own image path for investigation. It's an essential tool for digital evidence collection, incident response, and legal investigations."
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
        # Create the main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Create and setup widgets
        self.setup_widgets()
        
        # Bind the Return/Enter key to process commands
        # Bind the Return/Enter key to process commands
        self.cmd_entry.bind('<Return>', lambda e: self.process_command())
        
        # Set up keyboard shortcuts for common operations
        self.bind('<F1>', lambda e: self.show_help_overview())
        self.bind('<Control-a>', lambda e: self.handle_autopsy())
        self.bind('<Control-r>', lambda e: self.handle_raid())
        self.bind('<Control-w>', lambda e: self.handle_writeblocker())
        self.bind('<Control-s>', lambda e: self.handle_ransomware())
        # Add fullscreen toggle bindings
        self.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.bind('<Escape>', lambda e: self.toggle_fullscreen())
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
    
    def create_menu_bar(self):
        """Create the menu bar with help options"""
        # Create a menu with custom styling
        self.menu_bar = Menu(self, bg="#000000", fg="#00FF00", activebackground="#333333", 
                           activeforeground="#00FF00", relief="flat", bd=0)
        self.config(menu=self.menu_bar)
        
        # Create Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0, bg="#000000", fg="#00FF00", 
                            activebackground="#333333", activeforeground="#00FF00", 
                            relief="flat", bd=0)
        
        # Add menu items
        self.help_menu.add_command(label="Help Overview (F1)", command=self.show_help_overview)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="Autopsy Help (Ctrl+A)", command=self.show_autopsy_help)
        self.help_menu.add_command(label="RAID Help (Ctrl+R)", command=self.show_raid_help)
        self.help_menu.add_command(label="Write Blocker Help (Ctrl+W)", command=self.show_writeblocker_help)
        self.help_menu.add_command(label="Ransomware Help (Ctrl+S)", command=self.show_ransomware_help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="Quick Reference", command=self.show_quick_reference)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=self.show_about)
        
        # Add the Help menu to the menu bar
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a given widget
        
        Args:
            widget: The widget to add the tooltip to
            text: The text to display in the tooltip
        """
        def enter(event):
            # Get the widget that triggered the event
            widget = event.widget
            
            # Create a new toplevel window for the tooltip
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            
            # Withdraw the window to position it without showing
            tip = tk.Toplevel(widget)
            tip.withdraw()
            tip.wm_overrideredirect(True)  # Remove window decorations
            
            # Create the tooltip label
            label = tk.Label(tip, text=text, justify=tk.LEFT,
                           background="#333333", foreground="#00FF00",
                           relief=tk.SOLID, borderwidth=1,
                           font=("Courier", 10, "normal"),
                           padx=5, pady=5)
            label.pack(side=tk.TOP, fill=tk.BOTH)
            
            # Show the tooltip
            tip.geometry(f"+{x}+{y}")
            tip.deiconify()
            
            # Store the tooltip window
            self.tooltip_windows[widget] = tip
            
        def leave(event):
            # Remove the tooltip when mouse leaves the widget
            widget = event.widget
            if widget in self.tooltip_windows:
                self.tooltip_windows[widget].destroy()
                del self.tooltip_windows[widget]
                
        # Bind events to the widget
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
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
        self.autopsy_btn = self.create_styled_button(self.button_frame, text="Autopsy", command=self.handle_autopsy)
        self.autopsy_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.create_tooltip(self.autopsy_btn, "Autopsy: A powerful digital forensics platform\nfor investigating disk images, file systems,\nand recovering deleted data.")
        
        self.raid_btn = self.create_styled_button(self.button_frame, text="RAID", command=self.handle_raid)
        self.raid_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.create_tooltip(self.raid_btn, "RAID: Tools for recovering data from\nRedundant Array of Independent Disks\nsystems with damaged components.")
        
        self.writeblocker_btn = self.create_styled_button(self.button_frame, text="Write Blocker", command=self.handle_writeblocker)
        self.writeblocker_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.create_tooltip(self.writeblocker_btn, "Write Blocker: Hardware/software tools that\nprevent writing to storage devices during\nforensic acquisition to preserve evidence.")
        
        self.ransomware_btn = self.create_styled_button(self.button_frame, text="Ransomware", command=self.handle_ransomware)
        self.ransomware_btn.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)
        self.create_tooltip(self.ransomware_btn, "Ransomware: Educational demonstration of\nransomware attacks, encryption techniques,\nand recovery strategies.")
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
        # self.kali_button = self.create_styled_button(autopsy_button_frame, 
        #                             text="Launch Kali Autopsy", 
        #                             command=self.launch_autopsy)
        # self.kali_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        # USB Image Download button
        self.usb_image_button = self.create_styled_button(autopsy_button_frame, 
                                    text="Download Demo USB Image", 
                                    command=self.download_usb_image)
        self.usb_image_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        # Show Kali Autopsy Image button
        self.show_autopsy_image_button = self.create_styled_button(autopsy_button_frame, 
                                    text="Show Kali Autopsy Image", 
                                    command=self.show_kali_autopsy_image)
        self.show_autopsy_image_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
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
        # Button frame for RAID options
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
                                    command=lambda: self.launch_raid_gui())
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
                                   text="John Ripper GUI", 
                                   command=self.launch_john_ripper_gui)
        self.writeblocker_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        # Launch Write Blocker GUI button
        self.writeblocker_gui_button = self.create_styled_button(writeblocker_button_frame, 
                                    text="Write Blocker GUI", 
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
        # View Documentation button - commented out as no documentation exists yet
        # self.ransomware_doc_button = self.create_styled_button(ransomware_button_frame, 
        #                           text="View Documentation", 
        #                           command=self.view_ransomware_documentation)
        # self.ransomware_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
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
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(20, 10))
        self.output_text.config(state=tk.DISABLED)
        
        # Add status bar at the bottom
        self.status_bar = tk.Frame(self, bg="#000000", bd=1, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message on the left
        self.status_label = tk.Label(self.status_bar, 
                                   text="Ready", 
                                   bg="#000000", 
                                   fg="#00FF00", 
                                   font=("Courier", 10),
                                   anchor=tk.W,
                                   bd=0,
                                   padx=10,
                                   pady=2)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Resource monitor display in the middle
        self.resource_label = tk.Label(self.status_bar,
                                     text="CPU: -- | MEM: --", 
                                     bg="#000000", 
                                     fg="#00FF00", 
                                     font=("Courier", 10),
                                     anchor=tk.E,
                                     bd=0,
                                     padx=10,
                                     pady=2)
        self.resource_label.pack(side=tk.RIGHT)
        
        # Clock display on the right
        self.clock_label = tk.Label(self.status_bar, 
                                  text="", 
                                  bg="#000000", 
                                  fg="#00FF00", 
                                  font=("Courier", 10),
                                  anchor=tk.E,
                                  bd=0,
                                  padx=10,
                                  pady=2)
        self.clock_label.pack(side=tk.RIGHT)
        # Theme toggle button
        self.theme_button = tk.Label(self.status_bar,
                                   text="☀️", 
                                   bg="#000000",
                                   fg="#00FF00",
                                   font=("Courier", 10),
                                   anchor=tk.E,
                                   bd=0,
                                   padx=10,
                                   pady=2,
                                   cursor="hand2")
        self.theme_button.pack(side=tk.RIGHT)
        self.theme_button.bind("<Button-1>", lambda e: self.toggle_theme())
        # Start the clock update
        self.update_clock()
    
    def update_clock(self):
        """Update the clock display in the status bar"""
        try:
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            # Check if widget still exists before updating
            if self.clock_label.winfo_exists():
                self.clock_label.config(text=current_time)
            
                # Update resource monitor along with clock
                self.update_resource_monitor()
            
                # Update every second
                self.after(1000, self.update_clock)
        except Exception as e:
            # Silently handle errors during shutdown
            print(f"Error updating clock: {e}")
    
    def update_resource_monitor(self):
        """Update the system resource monitor in the status bar"""
        if not PSUTIL_AVAILABLE:
            if self.resource_label.winfo_exists():
                self.resource_label.config(text="CPU: N/A | MEM: N/A")
            return
        
        try:
            # Get CPU usage (average across all cores)
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Get memory information
            memory = psutil.virtual_memory()
            mem_percent = memory.percent
            
            # Format memory usage to show in a more readable format (GB)
            mem_used = memory.used / (1024 * 1024 * 1024)  # Convert to GB
            mem_total = memory.total / (1024 * 1024 * 1024)  # Convert to GB
            
            # Format the text
            resource_text = f"CPU: {cpu_percent:.1f}% | MEM: {mem_percent:.1f}% ({mem_used:.1f}/{mem_total:.1f} GB)"
            
            # Determine color based on usage (green for normal, yellow for moderate, red for high)
            if cpu_percent > 80 or mem_percent > 80:
                color = "#FF0000"  # Red
            elif cpu_percent > 50 or mem_percent > 50:
                color = "#FFFF00"  # Yellow
            else:
                color = "#00FF00"  # Green
                
            # Update the label if it still exists
            if self.resource_label.winfo_exists():
                self.resource_label.config(text=resource_text, fg=color)
            
        except Exception as e:
            print(f"Error updating resource monitor: {e}")
            if self.resource_label.winfo_exists():
                self.resource_label.config(text="CPU: ERR | MEM: ERR")
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode
        
        Switches the application between fullscreen and windowed mode based on current state.
        Uses platform-specific methods for Windows vs other operating systems.
        """
        try:
            if self.is_fullscreen:
                # Switch to windowed mode
                if platform.system() == 'Windows':
                    self.state('normal')
                else:
                    self.attributes('-fullscreen', False)
                self.geometry('1024x768')  # Default windowed size
                self.is_fullscreen = False
                self.display_output("Exited fullscreen mode. Press F11 to restore.")
            else:
                # Switch to fullscreen
                if platform.system() == 'Windows':
                    self.state('zoomed')
                else:
                    self.attributes('-fullscreen', True)
                self.is_fullscreen = True
                self.display_output("Entered fullscreen mode. Press ESC or F11 to exit.")
        except Exception as e:
            print(f"Error toggling fullscreen mode: {e}")
            # Attempt to reset to a safe state
            if platform.system() == 'Windows':
                self.state('normal')
            else:
                self.attributes('-fullscreen', False)
            self.geometry('1024x768')
            self.is_fullscreen = False
    
    def update_status(self, message):
        """Update the status bar message"""
        self.current_status = message
        self.status_label.config(text=message)
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        # Switch theme
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        
        # Update theme button text
        self.theme_button.config(text="☀️" if self.current_theme == "dark" else "🌙")
        
        # Apply the new theme
        self.apply_theme()
        
        # Save preference
        self.save_theme_preference()
        
        # Show notification
        self.display_output(f"Switched to {self.current_theme} theme")
    
    def display_image(self, image_path):
        """Display an image in the GUI"""
        try:
            # Generate unique task ID for image loading
            task_id = f"image_load_{os.path.basename(image_path)}"
            self.progress_tracker(task_id, f"Loading image: {os.path.basename(image_path)}", 10)
            
            # First, ensure any existing image is removed
            self.remove_displayed_image()
            
            # Check if the file exists
            if not os.path.exists(image_path):
                self.progress_tracker(task_id, f"Image file not found: {image_path}", complete=True)
                raise FileNotFoundError(f"Image file '{image_path}' not found")
                
            self.progress_tracker(task_id, f"Processing image: {os.path.basename(image_path)}", 30)
            
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
            
            # Mark image loading as complete
            self.progress_tracker(task_id, f"Image displayed: {os.path.basename(image_path)}", 100, complete=True)
            
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error displaying image: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def save_theme_preference(self):
        """Save theme preference to a file"""
        try:
            os.makedirs("Shared", exist_ok=True)
            with open("Shared/theme_preference.txt", "w") as f:
                f.write(self.current_theme)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    def load_theme_preference(self):
        """Load theme preference from file"""
        try:
            if os.path.exists("Shared/theme_preference.txt"):
                with open("Shared/theme_preference.txt", "r") as f:
                    theme = f.read().strip()
                    if theme in self.themes:
                        self.current_theme = theme
                        # Set theme button text based on current theme
                        if hasattr(self, 'theme_button'):
                            self.theme_button.config(text="☀️" if self.current_theme == "dark" else "🌙")
        except Exception as e:
            print(f"Error loading theme preference: {e}")
    
    def start_operation_timer(self):
        """Start timing an operation"""
        import datetime
        self.operation_start_time = datetime.datetime.now()
        return self.operation_start_time
    
    def get_elapsed_time(self):
        """Get elapsed time since operation started"""
        import datetime
        if self.operation_start_time:
            elapsed = datetime.datetime.now() - self.operation_start_time
            return elapsed
        return None
    
    def format_elapsed_time(self, elapsed=None):
        """Format elapsed time as a readable string"""
        if elapsed is None:
            elapsed = self.get_elapsed_time()
            
        if elapsed:
            total_seconds = elapsed.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.1f} seconds"
            elif total_seconds < 3600:
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                return f"{minutes}m {seconds}s"
            else:
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        return "unknown time"
    
    def progress_tracker(self, task_id, message, percentage=None, complete=False):
        """Track progress of operations and update both status bar and output area
        
        Args:
            task_id: Unique identifier for the task being tracked
            message: Progress message
            percentage: Optional percentage complete (0-100)
            complete: Whether the task is complete
        """
        # Initialize task if it's new
        if task_id not in self.active_progress_tasks and not complete:
            self.active_progress_tasks[task_id] = {
                'start_time': self.start_operation_timer(),
                'last_update': 0,
                'message': message
            }
            # Initial message
            self.display_output(f"▶ Started: {message}")
            self.update_status(f"▶ {message}")
            return
            
        # Update existing task
        if task_id in self.active_progress_tasks:
            task = self.active_progress_tasks[task_id]
            
            # Only update output text if percentage has changed significantly or message changed
            significant_change = False
            if percentage is not None:
                # Update if percentage has increased by at least 10%
                if percentage - task['last_update'] >= 10 or percentage >= 100:
                    significant_change = True
                    task['last_update'] = percentage
            
            # For status bar, always update
            status_message = message
            if percentage is not None:
                status_message = f"{message} ({percentage}%)"
                
            # Add timing information
            elapsed = self.get_elapsed_time()
            if elapsed:
                elapsed_str = self.format_elapsed_time(elapsed)
                status_message = f"{status_message} - {elapsed_str}"
                
            self.update_status(status_message)
            
            # Only update output area if significant change or complete
            if significant_change and not complete:
                progress_bar = '█' * int(percentage/10) + '░' * (10-int(percentage/10))
                self.display_output(f"◯ Progress: {progress_bar} {percentage}% - {message}")
                
            # Mark task as complete
            if complete:
                elapsed_str = self.format_elapsed_time()
                self.display_output(f"✓ Completed: {message} (took {elapsed_str})")
                self.update_status(f"✓ {message} - Complete")
                # Get a final resource snapshot
                self.update_resource_monitor()
                # Remove from active tasks
                del self.active_progress_tasks[task_id]
        
    def handle_autopsy(self):
        self.update_summary(self.autopsy_summary)
        self.display_output("Preparing Autopsy digital forensics options...")
        self.update_status("Working with Autopsy tools")
        self.update_resource_monitor()  # Get baseline resource usage
        
        # Hide all option frames and then show only Autopsy options
        # hide_all_option_frames also removes any displayed image
        self.hide_all_option_frames()
        self.autopsy_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    def view_autopsy_documentation(self):
        """Open the Autopsy documentation PDF file"""
        self.display_output("Opening Autopsy documentation PDF...")
        
        # Get current working directory for absolute path construction
        current_dir = os.getcwd()
        self.display_output(f"Current working directory: {current_dir}")
        
        # Construct the PDF path using os.path.join
        rel_pdf_path = os.path.join("Assets", "Step-by-Step Guide_ Using Autopsy.pdf")
        abs_pdf_path = os.path.abspath(rel_pdf_path)
        self.display_output(f"Full PDF path: {abs_pdf_path}")
        
        try:
            # Verify file exists and is readable
            if not os.path.exists(abs_pdf_path):
                self.display_output(f"File not found at: {abs_pdf_path}")
                raise FileNotFoundError(f"PDF file not found at: {abs_pdf_path}")
                
            if not os.path.isfile(abs_pdf_path):
                self.display_output(f"Path exists but is not a file: {abs_pdf_path}")
                raise FileNotFoundError(f"Path is not a valid file: {abs_pdf_path}")
                
            file_size = os.path.getsize(abs_pdf_path)
            self.display_output(f"File size: {file_size} bytes")
            
            # Open the file using the appropriate method based on OS
            self.display_output(f"Opening PDF file using platform: {platform.system()}")
            
            if platform.system() == 'Windows':
                # Use subprocess.run with 'start' command for more robust file opening on Windows
                self.display_output("Using Windows 'start' command to open PDF...")
                try:
                    # First try with shell=False (more secure)
                    result = subprocess.run(['cmd', '/c', 'start', '', abs_pdf_path], 
                                          shell=False, 
                                          check=True,
                                          capture_output=True)
                    self.display_output(f"Command executed successfully with return code: {result.returncode}")
                except subprocess.SubprocessError as se:
                    # If that fails, try with shell=True (less secure but more compatible)
                    self.display_output(f"First attempt failed: {se}, trying with shell=True...")
                    result = subprocess.run(f'start "" "{abs_pdf_path}"', 
                                          shell=True, 
                                          check=True,
                                          capture_output=True)
                    self.display_output(f"Second attempt completed with return code: {result.returncode}")
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', abs_pdf_path], check=True)
            else:  # Linux/Unix
                subprocess.run(['xdg-open', abs_pdf_path], check=True)
                
            self.display_output("Documentation file opened successfully")
                
        except FileNotFoundError as fnf:
            self.display_output(f"Error: PDF file not found: {fnf}")
            
            # Check file extension alternatives
            alt_extensions = ['.PDF', '.txt', '.TXT', '.md', '.MD']
            for ext in alt_extensions:
                alt_path = os.path.splitext(abs_pdf_path)[0] + ext
                if os.path.isfile(alt_path):
                    self.display_output(f"Found alternative file: {alt_path}")
                    alt_response = messagebox.askyesno(
                        "Alternative File Found", 
                        f"Found alternative file:\n{alt_path}\n\nWould you like to open it instead?"
                    )
                    if alt_response:
                        try:
                            if platform.system() == 'Windows':
                                subprocess.run(['cmd', '/c', 'start', '', alt_path], shell=False)
                            elif platform.system() == 'Darwin':  # macOS
                                subprocess.run(['open', alt_path])
                            else:  # Linux/Unix
                                subprocess.run(['xdg-open', alt_path])
                            return
                        except Exception as alt_e:
                            self.display_output(f"Error opening alternative file: {alt_e}")
                    break
            
            # Show error message with option to create sample file
            create_response = messagebox.askyesno(
                "File Not Found", 
                f"Could not find the documentation file at:\n{abs_pdf_path}\n\nWould you like to create a sample documentation file?"
            )
            if create_response:
                self.create_sample_autopsy_doc()
                
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", error_msg)
            
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def create_sample_autopsy_doc(self):
        """Create a sample Autopsy documentation file if it doesn't exist"""
        try:
            # Make sure Assets directory exists
            os.makedirs("Assets", exist_ok=True)
            
            # Create a sample documentation file path - simple and direct
            txt_filename = "Assets/Step-by-Step Guide_ Using Autopsy.txt"
            
            self.display_output(f"Creating sample documentation at: {txt_filename}")
            
            # Create a simple text file with instructions
            with open(txt_filename, "w") as f:
                f.write("""Step-by-Step Guide: Using Autopsy
This is a placeholder for the Autopsy documentation.

The actual documentation would include instructions on:
1. Installing Autopsy
2. Creating a new case
3. Adding disk images
4. Analyzing data
5. Generating reports

For the full Autopsy documentation, please visit:
https://www.autopsy.com/documentation/
""")
            
            # Check if file was successfully created
            if os.path.exists(txt_filename):
                self.display_output(f"Sample documentation created successfully")
                
                # Open the text file - simple direct approach
                if platform.system() == 'Windows':
                    os.startfile(os.path.abspath(txt_filename))
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', txt_filename])
                else:  # Linux/Unix
                    subprocess.run(['xdg-open', txt_filename])
            else:
                raise FileNotFoundError(f"Failed to create documentation file at {txt_filename}")
                
        except Exception as e:
            error_msg = f"Error creating sample documentation: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    def check_file_with_extensions(self, base_filename, extensions):
        """Check if a file exists with any of the provided extensions
        
        Args:
            base_filename: The base filename without extension
            extensions: List of extensions to try
            
        Returns:
            tuple: (found_path, found) - path to the found file and whether it was found
        """
        if os.path.exists(base_filename):
            return base_filename, True
            
        found = False
        found_path = base_filename
        
        for ext in extensions:
            alt_path = base_filename + ext
            if os.path.exists(alt_path):
                found_path = alt_path
                found = True
                break
                
        return found_path, found
    
    def launch_autopsy(self):
        """Show instructions and image on how to open Autopsy in Kali Linux"""
        self.display_output("Opening Kali Autopsy image and instructions...")
        
        try:
            # Display the Kali open autopsy image
            base_filename = "Assets/Kali open autopsy"
            image_path, found = self.check_file_with_extensions(
                base_filename + ".png", 
                [".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
            )
            if not found:
                raise FileNotFoundError("Could not find 'Kali open autopsy' image with any standard extension")
                
            # Display the image
            self.display_image(image_path)
            
            # Display instructions text
            self.display_output("To open Autopsy in Kali Linux:")
            self.display_output("1. Open a terminal window in Kali")
            self.display_output("2. Type 'autopsy' and press Enter")
            self.display_output("3. Follow the URL provided in the terminal to access Autopsy in your browser")
            
        except Exception as e:
            error_msg = f"Error launching Autopsy: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    def show_kali_autopsy_image(self):
        """Show only the Kali Autopsy image without instructions"""
        try:
            base_filename = "Assets/Kali open autopsy"
            image_path, found = self.check_file_with_extensions(
                base_filename + ".png", 
                [".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
            )
            
            if not found:
                raise FileNotFoundError("Could not find 'Kali open autopsy' image with any standard extension")
                
            self.display_output("Displaying Kali Autopsy image...")
            self.display_image(image_path)
        except Exception as e:
            error_msg = f"Error displaying Kali Autopsy image: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def download_usb_image(self):
        """Download or provide a USB image for Autopsy analysis"""
        self.display_output("Preparing USB image for forensic analysis...")
        self.display_output(f"Found image: {USB_IMAGE_CONFIG['sample_image_name']} ready to be used")
        try:
            # Create a dialog window for USB image options
            usb_dialog = tk.Toplevel(self)
            usb_dialog.title("Download USB Image")
            usb_dialog.geometry("500x300")
            usb_dialog.configure(bg="#000000")
            
            # Make dialog modal
            usb_dialog.transient(self)
            usb_dialog.grab_set()
            
            # Center on screen
            usb_dialog.update_idletasks()
            width = usb_dialog.winfo_width()
            height = usb_dialog.winfo_height()
            x = (usb_dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (usb_dialog.winfo_screenheight() // 2) - (height // 2)
            usb_dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            # Dialog title
            title_label = tk.Label(usb_dialog, 
                                  text="USB Image Download",
                                  bg="#000000", 
                                  fg="#00FF00",
                                  font=('Courier', 16, 'bold'))
            title_label.pack(pady=20)
            
            # Description
            desc_label = tk.Label(usb_dialog, 
                                 text="Select an option below to obtain a USB image\n" +
                                      "for analysis in Autopsy.",
                                 bg="#000000", 
                                 fg="#00FF00",
                                 font=('Courier', 12))
            desc_label.pack(pady=10)
            
            # Buttons frame
            buttons_frame = ttk.Frame(usb_dialog, style='TopLeft.TFrame')
            buttons_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # Sample image button
            sample_button = self.create_styled_button(buttons_frame, 
                                    text="Download Sample Image", 
                                    command=lambda: self.process_sample_image_download(usb_dialog))
            sample_button.pack(fill=tk.X, pady=5)
            
            # Update the button text to be more descriptive
            button = sample_button.winfo_children()[0]  # Get the actual button from the frame
            button.config(text=f"Download Demo USB Image ({USB_IMAGE_CONFIG['sample_image_name']})")
            
            # Custom image path button
            path_button = self.create_styled_button(buttons_frame, 
                                    text="Specify Image Location", 
                                    command=lambda: self.specify_image_path(usb_dialog))
            path_button.pack(fill=tk.X, pady=5)
        
        except Exception as e:
            error_msg = f"Error setting up USB image download: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def process_sample_image_download(self, parent_dialog):
        """Download a sample USB image for forensic analysis"""
        try:
            # Generate unique task ID for tracking progress
            task_id = f"image_download_{id(parent_dialog)}"
            self.progress_tracker(task_id, "Preparing USB image download", 0)
            
            # First verify the sample image exists
            source_path = os.path.join(USB_IMAGE_CONFIG["sample_image_path"], 
                                     USB_IMAGE_CONFIG["sample_image_name"])
            
            if not os.path.exists(source_path):
                messagebox.showerror("Error", f"Sample image not found at: {source_path}")
                self.display_output(f"Error: Sample image file not found at {source_path}")
                self.progress_tracker(task_id, "Image download failed - file not found", complete=True)
                return
            
            self.progress_tracker(task_id, "USB image located, preparing download", 10)
            
            # Create target directory if it doesn't exist
            if platform.system() == 'Windows':
                target_dir = os.path.join(os.path.expanduser("~"), "Documents", "Autopsy")
            else:
                target_dir = USB_IMAGE_CONFIG["autopsy_import_dir"]
                
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, USB_IMAGE_CONFIG["sample_image_name"])
            
            # Get file size for accurate progress reporting
            file_size = os.path.getsize(source_path)
            
            # Create progress dialog
            progress_dialog = tk.Toplevel(parent_dialog)
            progress_dialog.title("Copying Image File")
            progress_dialog.geometry("400x150")
            progress_dialog.configure(bg="#000000")
            progress_dialog.transient(parent_dialog)
            
            # Center on parent
            progress_dialog.update_idletasks()
            width = progress_dialog.winfo_width()
            height = progress_dialog.winfo_height()
            x = (parent_dialog.winfo_rootx() + parent_dialog.winfo_width() // 2) - (width // 2)
            y = (parent_dialog.winfo_rooty() + parent_dialog.winfo_height() // 2) - (height // 2)
            progress_dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            # Progress message
            message_label = tk.Label(progress_dialog, 
                                    text=f"Copying USB image ({int(file_size/1024/1024/1024)} GB)...",
                                    bg="#000000", 
                                    fg="#00FF00",
                                    font=('Courier', 12))
            message_label.pack(pady=10)
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_dialog, 
                                          orient="horizontal",
                                          length=300, 
                                          mode="determinate")
            progress_bar.pack(pady=10)
            
            # Status label
            status_label = tk.Label(progress_dialog,
                                   text="Starting copy operation...",
                                   bg="#000000",
                                   fg="#00FF00",
                                   font=('Courier', 10))
            status_label.pack(pady=5)
            
            # Function to perform the actual file copy in a separate thread
            def copy_file():
                try:
                    # Get file size for progress reporting
                    total_size = os.path.getsize(source_path)
                    copied_size = 0
                    
                    # Open source and target files
                    with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                        # Use a buffer for copying
                        buffer_size = 1024 * 1024  # 1MB buffer
                        buffer = src.read(buffer_size)
                        
                        while buffer:
                            dst.write(buffer)
                            copied_size += len(buffer)
                            
                            # Calculate and report progress
                            progress = int((copied_size / total_size) * 100)
                            # Update status in main thread
                            self.after(0, lambda p=progress: 
                                      self.progress_tracker(task_id, f"Copying USB image", p))
                            
                            # Read next chunk
                            buffer = src.read(buffer_size)
                    
                    return True, "File copied successfully"
                except Exception as e:
                    return False, str(e)
            
            # Update progress and perform copy
            def perform_copy_with_progress():
                # Set some incremental progress to show activity
                progress_bar["value"] = 10
                progress_dialog.update()
                status_label.config(text="Initializing copy operation...")
                
                # Update progress tracker
                self.progress_tracker(task_id, "Initializing copy operation", 20)
                
                # Perform the actual copy
                import threading
                copy_thread = threading.Thread(target=lambda: copy_file())
                copy_thread.start()
                
                # Initial progress update
                progress_bar["value"] = 30
                progress_dialog.update()
                
                def check_copy_status():
                    progress_dialog.update()
                    status_label.config(text=f"Copying file... ({progress_bar['value']}%)")
                    
                    if copy_thread.is_alive():
                        # Still copying, keep checking
                        progress_dialog.after(100, check_copy_status)
                    else:
                        # Copy is done, show 100%
                        status_label.config(text="Copy complete!")
                        
                        # Final update and delay before closing
                        progress_dialog.update()
                        progress_dialog.after(500, finish_copy)
                
                # Start checking copy status
                progress_dialog.after(100, check_copy_status)
                
                def finish_copy():
                    progress_dialog.destroy()
                    parent_dialog.destroy()
                    
                    # Verify the file exists
                    if os.path.exists(target_path):
                        # Mark task as complete
                        self.progress_tracker(task_id, f"USB image copied successfully to: {target_path}", 100, complete=True)
                        self.display_output(f"Copy completed successfully! The USB image has been copied to:\n{target_path}\n\nThis image is now ready for analysis in Autopsy.")
                    else:
                        raise FileNotFoundError("Failed to copy image file")
            
            # Start the copy process
            perform_copy_with_progress()
            
        except Exception as e:
            error_msg = f"Error during USB image operation: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    def specify_image_path(self, parent_dialog):
        """Allow the user to specify the path to a USB image"""
        try:
            # Create path dialog
            path_dialog = tk.Toplevel(parent_dialog)
            path_dialog.title("Specify Image Path")
            path_dialog.geometry("450x200")
            path_dialog.configure(bg="#000000")
            path_dialog.transient(parent_dialog)
            
            # Center on parent
            path_dialog.update_idletasks()
            width = path_dialog.winfo_width()
            height = path_dialog.winfo_height()
            x = (parent_dialog.winfo_rootx() + parent_dialog.winfo_width() // 2) - (width // 2)
            y = (parent_dialog.winfo_rooty() + parent_dialog.winfo_height() // 2) - (height // 2)
            path_dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            # Instruction
            instruction_label = tk.Label(path_dialog, 
                                        text="Enter the full path to the USB image file:",
                                        bg="#000000", 
                                        fg="#00FF00",
                                        font=('Courier', 12))
            instruction_label.pack(pady=10)
            
            # Path entry
            path_entry = ttk.Entry(path_dialog, width=50)
            path_entry.pack(pady=10, padx=20)
            
            # Button frame
            button_frame = ttk.Frame(path_dialog, style='TopLeft.TFrame')
            button_frame.pack(padx=20, pady=10)
            
            # Browse button
            browse_button = self.create_styled_button(button_frame, 
                                    text="Browse...", 
                                    command=lambda: self.browse_for_image(path_entry))
            browse_button.pack(side=tk.LEFT, padx=5)
            
            # Submit button
            submit_button = self.create_styled_button(button_frame, 
                                    text="Submit", 
                                    command=lambda: self.process_image_path(path_entry.get(), 
                                                                          path_dialog, 
                                                                          parent_dialog))
            submit_button.pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            error_msg = f"Error creating path dialog: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def browse_for_image(self, entry_widget):
        """Open file browser to select an image file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select USB Image File",
            filetypes=[
                ("Disk Image Files", "*.dd *.raw *.img *.E01 *.001"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
    
    def process_image_path(self, image_path, path_dialog, parent_dialog):
        """Process the provided image path"""
        if not image_path.strip():
            messagebox.showerror("Error", "Please enter a valid path")
            return
            
        try:
            # Check if file exists
            if os.path.exists(image_path):
                # Store the path for use when launching Autopsy
                if not hasattr(self, 'current_image_path'):
                    self.current_image_path = image_path
                else:
                    self.current_image_path = image_path
                    
                # If on Linux, create a symbolic link in the Autopsy import directory
                if platform.system() != 'Windows':
                    try:
                        # Create the directory if it doesn't exist
                        os.makedirs(USB_IMAGE_CONFIG["autopsy_import_dir"], exist_ok=True)
                        
                        # Create symlink (or copy if symlink fails)
                        symlink_path = os.path.join(USB_IMAGE_CONFIG["autopsy_import_dir"], 
                                                  os.path.basename(image_path))
                        
                        try:
                            # Try to create a symlink first
                            if os.path.exists(symlink_path):
                                os.unlink(symlink_path)  # Remove existing link
                            os.symlink(image_path, symlink_path)
                        except Exception as sym_err:
                            # If symlink fails, copy the file
                            self.display_output(f"Symlink failed, copying file: {str(sym_err)}")
                            shutil.copy2(image_path, symlink_path)
                            
                        self.display_output(f"Image is now available at: {symlink_path}")
                    except Exception as e:
                        self.display_output(f"Warning: Could not create link in Autopsy directory: {str(e)}")
                
                # Close dialogs
                path_dialog.destroy()
                parent_dialog.destroy()
                
                self.display_output(f"Image path set to: {image_path}")
                messagebox.showinfo("Success", f"The USB image at {image_path} is ready for analysis in Autopsy.")
            else:
                messagebox.showerror("File Not Found", f"The file does not exist: {image_path}")
        except Exception as e:
            error_msg = f"Error processing image path: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
        
    def view_raid_documentation(self):
        """Open the RAID documentation Markdown file"""
        self.display_output("Opening RAID documentation...")
        md_filename = "RAID/README.md"
        
        try:
            # Get absolute path for reliable file opening
            abs_md_path = os.path.abspath(md_filename)
            self.display_output(f"Looking for documentation at: {abs_md_path}")
            
            # Check if the file exists
            if not os.path.exists(abs_md_path):
                raise FileNotFoundError(f"Markdown file '{abs_md_path}' not found")
            
            # Open Markdown file with the appropriate method based on platform
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            
            if platform.system() == 'Windows':
                # Use PowerShell command which we know works reliably
                powershell_cmd = f'Start-Process "{abs_md_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
                self.display_output("Documentation opened with PowerShell command")
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', abs_md_path], check=True)
                self.display_output("Documentation opened with 'open' command")
            else:  # Linux/Unix
                subprocess.run(['xdg-open', abs_md_path], check=True)
                self.display_output("Documentation opened with 'xdg-open' command")
                
            self.display_output(f"Successfully opened RAID documentation")
            
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            
            # Offer to create the README.md file if it doesn't exist
            create_response = messagebox.askyesno(
                "File Not Found", 
                f"The RAID documentation file was not found at: {abs_md_path}\n\nWould you like to create a sample documentation file?"
            )
            if create_response:
                self.create_raid_documentation()
                
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", error_msg)
            
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def create_raid_documentation(self):
        """Create a sample RAID documentation file if it doesn't exist"""
        try:
            # Make sure RAID directory exists
            os.makedirs("RAID", exist_ok=True)
            
            # Path for the README.md file
            md_filename = "RAID/README.md"
            
            self.display_output(f"Creating RAID documentation at: {md_filename}")
            
            # Create the documentation file
            with open(md_filename, "w") as f:
                f.write("""# RAID Visualization Tool

## Overview
The RAID Visualization Tool provides an interactive way to understand, visualize, and simulate Redundant Array of Independent Disks (RAID) technology. This educational tool demonstrates how data is stored across multiple disks in various RAID configurations and how the system handles disk failures and data recovery.

## Features and Capabilities
- **Interactive Visualization**: See how data is distributed across multiple disks in real-time
- **RAID Level Simulation**: Visualize different RAID configurations and their operations
- **Failure Simulation**: Demonstrate how RAID systems handle disk failures
- **Recovery Visualization**: Show the recovery process when replacing failed drives
- **Performance Metrics**: Display theoretical read/write performance for different RAID levels
- **Storage Efficiency**: Calculate and display storage efficiency for different configurations

## How to Use the Tool
1. **Launch the Tool**: Click the "Launch RAID GUI" button in the main interface
2. **Select RAID Level**: Choose the RAID level you want to visualize from the dropdown menu
3. **Configure Parameters**: Set the number of disks, stripe size, and other parameters
4. **Visualize Data Distribution**: Use the visualization panel to see how data blocks are distributed
5. **Simulate Failures**: Click on disks to simulate failures and see how the system responds
6. **Demonstrate Recovery**: Follow the recovery steps to restore the array to full functionality

## RAID Levels Supported
- **RAID 0 (Striping)**: Data striped across multiple disks for improved performance, no redundancy
- **RAID 1 (Mirroring)**: Data mirrored across disks for redundancy, reduced storage efficiency
- **RAID 5 (Striping with Parity)**: Data and parity information striped across disks, can survive one disk failure
- **RAID 6 (Striping with Double Parity)**: Similar to RAID 5 but with two parity blocks, can survive two disk failures
- **RAID 10 (1+0)**: Combination of mirroring and striping for both performance and redundancy

## Common Use Cases
- **Educational Demonstrations**: Teaching students about RAID technology and principles
- **Forensic Analysis Planning**: Understanding how to recover data from failed RAID systems
- **Decision Support**: Helping system administrators choose the appropriate RAID level for their needs
- **Recovery Practice**: Practicing RAID recovery techniques in a simulated environment
- **Performance Comparison**: Comparing the theoretical performance of different RAID configurations

For more detailed information about RAID technology and forensic analysis of RAID systems, refer to the Digital Forensics Documentation section in the main application.
""")
            
            # Check if file was successfully created
            if os.path.exists(md_filename):
                self.display_output(f"RAID documentation created successfully")
                
                # Open the documentation file
                if platform.system() == 'Windows':
                    powershell_cmd = f'Start-Process "{os.path.abspath(md_filename)}"'
                    subprocess.run(['powershell', '-command', powershell_cmd], check=True)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', md_filename])
                else:  # Linux/Unix
                    subprocess.run(['xdg-open', md_filename])
            else:
                raise FileNotFoundError(f"Failed to create documentation file at {md_filename}")
                
        except Exception as e:
            error_msg = f"Error creating RAID documentation: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    def launch_raid_gui(self):
        """Launch RAID Visualization GUI"""
        self.display_output("Launching RAID visualization GUI...")
        self.update_status("Running RAID visualization")
        
        try:
            # Create the Toplevel window for RAID visualization
            raid_toplevel = tk.Toplevel(self)
            raid_toplevel.title("RAID Visualization")
            raid_toplevel.geometry("1000x700")
            
            # Create the RAID visualization app with the Toplevel window
            raid_window = raid.RAIDVisualizationApp(raid_toplevel)
            
            # Handle window close properly
            raid_toplevel.protocol("WM_DELETE_WINDOW", lambda: self.on_raid_window_close(raid_toplevel))
            
            # Force focus on the new window
            raid_toplevel.focus_force()
            
            self.display_output("RAID visualization GUI launched successfully")
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
        self.update_status("Working with RAID recovery tools")
        self.update_resource_monitor()  # Get baseline resource usage
        
        # Hide all option frames and then show only RAID options
        # hide_all_option_frames also removes any displayed image
        self.hide_all_option_frames()
        self.raid_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    def handle_writeblocker(self):
        self.update_summary(self.writeblocker_summary)
        self.display_output("Preparing Write Blocker options...")
        self.update_status("Working with Write Blocker tools")
        self.update_resource_monitor()  # Get baseline resource usage
        
        # Hide all option frames and then show only Write Blocker options
        # hide_all_option_frames also removes any displayed image
        self.hide_all_option_frames()
        
        # Display the lock image
        # Display the lock image
        self.display_image("Assets/Image of lock.png")
        # Show Write Blocker options
        self.writeblocker_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    def view_writeblocker_documentation(self):
        """Open the Write Blocker documentation PDF file"""
        self.display_output("Opening Write Blocker documentation PDF...")
        pdf_filename = "WriteBlocker/Write_Blocker_Documentation.pdf"
        
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
        """Launch Write Blocker GUI"""
        self.display_output("Launching Write Blocker GUI...")
        
        try:
            # Create a toplevel window for the Write Blocker GUI
            blocker_toplevel = tk.Toplevel(self)
            blocker_toplevel.title("🔒 Write Blocker Demo")
            blocker_toplevel.geometry("1280x720")
            blocker_toplevel.configure(bg=write_blocker_gui.BACKGROUND_COLOR)
            
            # Define the switch_to_main function that will be passed to WriteBlockerIntro
            def switch_to_main():
                for widget in blocker_toplevel.winfo_children():
                    widget.destroy()
                write_blocker_gui.WriteBlockerDemo(blocker_toplevel)
            
            # Initialize the WriteBlockerIntro with the switch_to_main function
            write_blocker_gui.WriteBlockerIntro(blocker_toplevel, switch_to_main)
            
            # Handle window close properly
            blocker_toplevel.protocol("WM_DELETE_WINDOW", lambda: self.on_writeblocker_window_close(blocker_toplevel))
            
            # Force focus on the new window
            blocker_toplevel.focus_force()
            
            self.display_output("Write Blocker GUI launched successfully")
        except Exception as e:
            error_msg = f"Error launching Write Blocker GUI: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def on_writeblocker_window_close(self, window):
        """Handle proper cleanup when the Write Blocker window is closed"""
        try:
            self.display_output("Write Blocker GUI window closed")
            window.destroy()
        except Exception as e:
            pass  # Silently handle any errors during window cleanup
    
    def launch_john_ripper_gui(self):
        """Launch John the Ripper GUI"""
        self.display_output("Launching John the Ripper GUI...")
        
        try:
            # Create a toplevel window for the John the Ripper GUI
            john_toplevel = tk.Toplevel(self)
            john_toplevel.title("🔐 John the Ripper Password Cracking Demo")
            john_toplevel.geometry("1280x720")
            john_toplevel.configure(bg=john_ripper_gui.BACKGROUND_COLOR)
            
            # Define the switch_to_demo function that will be passed to IntroScreen
            def switch_to_demo():
                for widget in john_toplevel.winfo_children():
                    widget.destroy()
                john_ripper_gui.JohnDemo(john_toplevel)
            
            # Initialize the IntroScreen with the switch_to_demo function
            john_ripper_gui.IntroScreen(john_toplevel, switch_to_demo)
            
            # Handle window close properly
            john_toplevel.protocol("WM_DELETE_WINDOW", lambda: self.on_john_ripper_window_close(john_toplevel))
            
            # Force focus on the new window
            john_toplevel.focus_force()
            
            self.display_output("John the Ripper GUI launched successfully")
        except Exception as e:
            error_msg = f"Error launching John the Ripper GUI: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def on_john_ripper_window_close(self, window):
        """Handle proper cleanup when the John the Ripper window is closed"""
        try:
            self.display_output("John the Ripper GUI window closed")
            window.destroy()
        except Exception as e:
            pass  # Silently handle any errors during window cleanup
        
    def handle_ransomware(self):
        self.update_summary(self.ransomware_summary)
        self.display_output("Preparing Ransomware demonstration options...")
        self.update_status("Working with Ransomware demo tools")
        self.update_resource_monitor()  # Get baseline resource usage
        
        # Hide all option frames and then show only Ransomware options
        self.hide_all_option_frames()
        self.ransomware_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame)
    
    # def view_ransomware_documentation(self):
    #     """Open the Ransomware documentation PDF file"""
    #     self.display_output("Opening Ransomware documentation PDF...")
    #     pdf_filename = "Ransomware/Ransomware_Documentation.pdf"
    #     
    #     try:
    #         # Check if the file exists
    #         if not os.path.exists(pdf_filename):
    #             raise FileNotFoundError(f"PDF file '{pdf_filename}' not found")
    #         
    #         # Open PDF file with the default system viewer
    #         if platform.system() == 'Windows':
    #             os.startfile(pdf_filename)
    #         elif platform.system() == 'Darwin':  # macOS
    #             subprocess.run(['open', pdf_filename])
    #         else:  # Linux/Unix
    #             subprocess.run(['xdg-open', pdf_filename])
    #             
    #         self.display_output(f"Successfully opened {pdf_filename}")
    #     except FileNotFoundError as e:
    #         error_msg = f"Error: {str(e)}"
    #         self.display_output(error_msg)
    #         messagebox.showerror("File Not Found", error_msg)
    #     except Exception as e:
    #         error_msg = f"Error opening PDF: {str(e)}"
    #         self.display_output(error_msg)
    #         messagebox.showerror("Error", error_msg)
    
    def manage_ransomware_buttons(self, state='normal'):
        """Enable or disable all ransomware launch buttons
        Args:
            state: The state to set the buttons to ('normal' or 'disabled')
        """
        if hasattr(self, 'ransomware_demo_button'):
            button = self.ransomware_demo_button.winfo_children()[0]
            button.config(state=state)
            
    def initialize_ransomware_files(self):
        """Initialize the required files for the ransomware demo"""
        try:
            # Create Ransomware/demo_files directory if it doesn't exist
            demo_files_dir = "Ransomware/demo_files"
            os.makedirs(demo_files_dir, exist_ok=True)
            
            self.display_output("Initializing ransomware demo files...")
            test_files = {
                f"{demo_files_dir}/business_letter.txt": "Dear Client,\nWe are pleased to offer you a contract worth $500,000 for Q3 2025.\nRegards,\nBusiness Inc.",
                f"{demo_files_dir}/invoice.txt": "Invoice #1234\n50 units of Product X at $200 each\nTotal: $10,000\nDue: 04/01/2025"
            }
            
            created_files = []
            for filename, content in test_files.items():
                if not os.path.exists(filename):
                    created_files.append(os.path.basename(filename))
                    with open(filename, 'w') as f:
                        f.write(content)
                    with open(f"{filename}.bak", 'w') as f:
                        f.write(content)
            
            if created_files:
                self.display_output(f"Created demo files: {', '.join(created_files)}")
            else:
                self.display_output("Demo files already exist")
                
            return True, "Files initialized successfully"
        except Exception as e:
            return False, str(e)
    def launch_ransomware_demo(self, source_button=None):
        """Launch Ransomware Demo visualization.
        Args:
            source_button: The button that triggered the demo (for state management)
        """
        self.update_status("Running Ransomware demonstration")
        self.update_resource_monitor()  # Monitor resources before intensive operation
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
            self.update_status("Ready")
            
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
        
    def handle_eggs(self):
        """Display a list of all available Easter eggs"""
        self.display_output("🥚 Easter Eggs List 🥚")
        self.display_output("1. Click the title \"Welcome to the Digital Forensics Demo\" to see the Cyber Ring image")
        self.display_output("2. Type \"meow\" in the command box to see an ASCII cat")
        self.display_output("3. Type \"hakercat\" to see a special image")
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
            self.display_image("Assets/Meow-Frame.webp")
        elif command == "eggs":
            self.handle_eggs()
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
        # Update status bar with a shortened version of the message
        short_message = message[:50] + "..." if len(message) > 50 else message
        self.update_status(short_message)
        
            
    def remove_displayed_image(self):
        """Remove any currently displayed image"""
        if self.image_label is not None:
            self.image_label.destroy()
            self.image_label = None

    def hide_all_option_frames(self):
        self.autopsy_options_frame.pack_forget()
        self.raid_options_frame.pack_forget()
        self.writeblocker_options_frame.pack_forget()
        self.ransomware_options_frame.pack_forget()
        # Also remove any displayed image for a clean UI state
        self.remove_displayed_image()
        
    def handle_title_click(self):
        """Display the Cyber Ring image when the title is clicked"""
        self.display_output("The one GUI to rule them all!")
        self.update_status("Secret Cyber Ring Activated!")
        self.display_image("Assets/Cyber Rring Edited 2.PNG")
    # Help menu functions
    def show_help_dialog(self, title, content):
        """Show a help dialog with the given title and content"""
        help_dialog = tk.Toplevel(self)
        help_dialog.title(title)
        help_dialog.geometry("650x500")
        help_dialog.configure(bg="#000000")
        help_dialog.transient(self)
        help_dialog.grab_set()
        
        # Center on parent
        help_dialog.update_idletasks()
        width = help_dialog.winfo_width()
        height = help_dialog.winfo_height()
        x = (self.winfo_rootx() + self.winfo_width() // 2) - (width // 2)
        y = (self.winfo_rooty() + self.winfo_height() // 2) - (height // 2)
        help_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Title
        title_label = tk.Label(help_dialog, text=title, bg="#000000", fg="#00FF00",
                             font=('Courier', 16, 'bold'))
        title_label.pack(pady=(20, 10))
        
        # Content frame with scrollbar
        content_frame = tk.Frame(help_dialog, bg="#000000")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget for content
        content_text = tk.Text(content_frame, bg="#000000", fg="#00FF00", 
                              font=('Courier', 12), wrap=tk.WORD,
                              yscrollcommand=scrollbar.set, bd=0, padx=10, pady=10)
        content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=content_text.yview)
        
        # Insert content
        content_text.insert(tk.END, content)
        content_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = self.create_styled_button(help_dialog, text="Close", 
                                 command=help_dialog.destroy)
        close_button.pack(pady=(0, 20))
    
    def show_help_overview(self, event=None):
        """Show the help overview dialog"""
        content = """Digital Forensics Demo Help

This application provides demonstrations of various digital forensic tools and techniques:

• Autopsy - Forensic analysis of disk images
• RAID - Recovery of data from RAID arrays
• Write Blocker - Demonstration of write blocking techniques
• Ransomware - Educational demonstration of ransomware attacks

Keyboard Shortcuts:
• F1: Show this help overview
• Ctrl+A: Autopsy tools
• Ctrl+R: RAID recovery tools
• Ctrl+W: Write Blocker tools
• Ctrl+S: Ransomware demonstration

You can access tool-specific help from the Help menu or by clicking the corresponding options in this dialog.
"""
        self.show_help_dialog("Help Overview", content)
    
    def show_autopsy_help(self):
        """Show the Autopsy help dialog"""
        content = """Autopsy Help

Autopsy is a powerful digital forensics platform used for investigating what happened on a computer. It provides a graphical interface to analyze disk images, perform file recovery, browse file systems, and search for specific content.

Features:
• Disk image analysis
• File recovery
• Browser history analysis
• Keyword searching
• Timeline creation

This demo allows you to:
• View documentation about Autopsy
• Download a sample USB image for analysis
• Specify your own image for analysis
• View a screenshot of the Autopsy interface in Kali Linux

Getting Started:
1. Click the "Autopsy" button in the main interface
2. Select "Download Demo USB Image" to obtain a sample for analysis
3. Use the "View Documentation" button to learn how to use Autopsy
"""
        self.show_help_dialog("Autopsy Help", content)
    
    def show_raid_help(self):
        """Show the RAID help dialog"""
        content = """RAID Help

RAID (Redundant Array of Independent Disks) recovery is a critical process for retrieving data from damaged or failed RAID arrays. This demo showcases methods for recovering data from compromised RAID systems.

Features:
• RAID parameter identification (level, stripe size, disk order)
• Virtual array rebuilding
• Handling partial failures
• Data extraction from compromised systems

This demo allows you to:
• View documentation about RAID recovery
• Launch a RAID visualization tool
• Explore different RAID configurations and failure scenarios

Getting Started:
1. Click the "RAID" button in the main interface
2. Select "View Documentation" to learn about RAID recovery techniques
3. Use "Launch RAID GUI" to explore the visualization tool
"""
        self.show_help_dialog("RAID Help", content)
    
    def show_writeblocker_help(self):
        """Show the Write Blocker help dialog"""
        content = """Write Blocker Help

Write Blockers are specialized hardware or software tools that create a read-only connection between a storage device and a forensic workstation. They prevent any write commands from reaching the target storage device during forensic acquisition and analysis.

Features:
• Maintaining evidence integrity
• Preventing media contamination
• Ensuring chain of custody
• Supporting legal admissibility of evidence

This demo includes:
• Write Blocker GUI demonstration
• John the Ripper password cracking demonstration

Getting Started:
1. Click the "Write Blocker" button in the main interface
2. Select "Write Blocker GUI" to explore the write blocking demonstration
3. Select "John Ripper GUI" to explore password cracking techniques
"""
        self.show_help_dialog("Write Blocker Help", content)
    
    def show_ransomware_help(self):
        """Show the Ransomware help dialog"""
        content = """Ransomware Help

This demonstration explores ransomware attack vectors, encryption techniques, file system impacts, and defense strategies. It also covers digital forensic approaches to ransomware incident response.

NOTE: This is an educational demonstration only. No actual malicious code is used, and no files are permanently encrypted.

Features:
• Ransomware attack demonstration
• Encryption visualization
• Recovery techniques
• Preventative measures

Getting Started:
1. Click the "Ransomware" button in the main interface
2. Select "Launch Ransomware Demo" to start the demonstration
3. Follow the on-screen instructions to learn about ransomware attack and defense
"""
        self.show_help_dialog("Ransomware Help", content)
    
    def show_quick_reference(self):
        """Show the Quick Reference guide"""
        content = """Quick Reference Guide

Main Buttons:
• Autopsy - Digital forensics platform for disk analysis
• RAID - Recovery tools for RAID arrays
• Write Blocker - Tools for write-protected device access
• Ransomware - Educational demonstration of ransomware attacks

Command Box:
Type commands and press Enter to execute. Try these commands:
• meow - Display ASCII cat art
• hakercat - Display a special hacker cat image
• eggs - List all Easter eggs

Keyboard Shortcuts:
• F1 - Show help overview
• Ctrl+A - Autopsy tools
• Ctrl+R - RAID recovery tools
• Ctrl+W - Write Blocker tools
• Ctrl+S - Ransomware demonstration

Status Bar:
The status bar at the bottom displays:
• Current operation status on the left
• Current time on the right

Easter Eggs:
• Click the title to see the Cyber Ring image
• Type "meow" to see a text cat
• Type "hakercat" to see a hacker cat image
"""
        self.show_help_dialog("Quick Reference Guide", content)
    
    def show_about(self):
        """Show the About dialog"""
        content = """Digital Forensics Demo

A comprehensive educational tool for demonstrating digital forensics concepts and techniques.

Features:
• Autopsy digital forensics platform demonstration
• RAID recovery visualization
• Write blocker and password cracking tools
• Ransomware education and demonstration

Version: 1.0.0

© 2025 NCREPT Lab
"""
        self.show_help_dialog("About Digital Forensics Demo", content)

if __name__ == "__main__":
    app = DigitalForensicsDemo()
    app.mainloop()

