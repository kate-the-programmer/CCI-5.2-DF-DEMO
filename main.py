import tkinter as tk
from tkinter import ttk, font, messagebox, Menu
import subprocess
import os
import platform
from PIL import Image, ImageTk
import shutil
import sys

# Add module directories to Python path
sys.path.append('./WriteBlocker')
sys.path.append('./JohnRipper')
sys.path.append('./RAID')
sys.path.append('./Ransomware')
sys.path.append('./MemoryForensics')
sys.path.append('./NetworkForensics')
sys.path.append('./MetaDataForensics')
sys.path.append('./SteganographyDetection')
sys.path.append('./MalwareStaticAnalysis')
sys.path.append('./Autopsy')
sys.path.append('./CTFDemo')

# Import modules from their respective directories
from WriteBlocker import write_blocker_gui
from JohnRipper import john_ripper_gui
from MemoryForensics import memory_demo
from NetworkForensics import network_demo
from MetaDataForensics import metadata_demo
from Autopsy import autopsy_demo
from SteganographyDetection import steganography_detection
from MalwareStaticAnalysis import malware_analysis
from CTFDemo import ctf
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("psutil module not found. System resource monitoring will be disabled.")
    PSUTIL_AVAILABLE = False

# Configuration section
USB_IMAGE_CONFIG = {
    "sample_image_name": "Demo_USB_image.img",
    "sample_image_path": "./Assets/",
    "user_images_dir": "Assets/user_images/",
    "autopsy_import_dir": "/tmp/autopsy_import/"
}

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
        self.is_fullscreen = True
        if platform.system() == 'Windows':
            self.state('zoomed')
        else:
            self.attributes('-fullscreen', True)
        self.configure(bg="#000000")

        # Define default summary
        self.default_summary = """Digital Forensics Demo: Explore various forensic analysis tools.
            Available demos: Autopsy, Write Blocker, Password Cracking, RAID, Ransomware, Memory Forensics,
            Network Forensics, Metadata Forensics, Steganography Detection, and Malware Static Analysis.
            Type a command or use the buttons below to begin."""
        self.image_label = None
        self.tooltip_windows = {}
        self.current_status = "Ready"
        self.operation_start_time = None
        self.active_progress_tasks = {}
        # Track open demo windows
        self.open_demo_windows = {}  # Dictionary to store demo windows and their apps

        self.autopsy_summary = "Autopsy Demo: Analyze disk images, recover files, and investigate digital evidence."
        self.writeblocker_summary = "Write Blocker Demo: Prevent writes to storage devices during forensic analysis."
        self.password_cracking_summary = "Password Cracking Demo: Recover passwords using tools like John the Ripper and Hashcat."
        self.raid_summary = "RAID Demo: Recover data from damaged or failed RAID arrays."
        self.ransomware_summary = "Ransomware Demo: Learn about ransomware attacks and defense strategies."
        self.memory_forensics_summary = "Memory Forensics: Analyze RAM to uncover evidence of malicious activity."
        self.network_forensics_summary = "Network Forensics: Investigate network traffic to trace cyber incidents."
        self.metadata_forensics_summary = "Metadata Forensics: Extract hidden information from file metadata."
        self.steganography_detection_summary = "Steganography Detection: Identify and extract hidden messages in files."
        self.malware_static_analysis_summary = "Malware Static Analysis: Examine malware without execution to understand its behavior."
        self.ctf_summary = "CTF Demo: Participate in a Capture The Flag challenge to test your forensic skills."

        self.themes = {
            "dark": {
                "bg": "#000000",
                "fg": "#00FF00",
                "active_bg": "#333333",
                "active_fg": "#FFFFFF",
                "disabled_fg": "#005500",
                "button_bg": "#000000",
                "button_fg": "#00FF00",
                "button_hover": "#111111",
                "accent": "#00FF00",
                "warning": "#FF0000",
                "tooltip_bg": "#333333",
                "entry_bg": "#000000",
                "progress_fg": "#00FF00",
                "panel_bg": "#111111",
                "terminal_bg": "#1C2526",
                "terminal_fg": "#00FF00",
                "block_outline": "#B0B0B0",
                "block_text": "#00FF00",
                "block_colors": ["#FF6B6B", "#4ECDC4"],
                "parity_color": "#7D7D9C",
                "button_active_bg": "#333333",
                "canvas_bg": "#23272A",
                "card_bg": "#252525",
                "border": "#005500",
                "highlight_bg": "#FFFF99",
                "highlight_fg": "#000000",
                "highlight" :"#FFFF99"
            },
            "light": {
                "bg": "#F5F5F5",
                "fg": "#006600",
                "active_bg": "#CCFFCC",
                "active_fg": "#000000",
                "disabled_fg": "#AAAAAA",
                "button_bg": "#FFFFFF",
                "button_fg": "#000000",
                "button_hover": "#E6E6E6",
                "accent": "#008850",
                "warning": "#CC0000",
                "tooltip_bg": "#EEEEEE",
                "entry_bg": "#FFFFFF",
                "progress_fg": "#008850",
                "panel_bg": "#E6E6E6",
                "terminal_bg": "#E6E6E6",
                "terminal_fg": "#006600",
                "block_outline": "#B0B0B0",
                "block_text": "#FFFFFF",
                "block_colors": ["#FF6B6B", "#4ECDC4"],
                "parity_color": "#7D7D9C",
                "button_active_bg": "#7289DA",
                "canvas_bg": "#23272A",
                "card_bg": "#D9D9D9",
                "border": "#88AA88",
                "highlight_bg": "#FFEB3B",
                "highlight_fg": "#000000",
                "highlight": "#FFFF99"
            },
            "blue": {
                "bg": "#001F3F",
                "fg": "#7FDBFF",
                "active_bg": "#0074D9",
                "active_fg": "#FFFFFF",
                "disabled_fg": "#AAAAAA",
                "button_bg": "#001F3F",
                "button_fg": "#7FDBFF",
                "button_hover": "#005F8A",
                "accent": "#39CCCC",
                "warning": "#FF4136",
                "tooltip_bg": "#001F3F",
                "entry_bg": "#001F3F",
                "progress_fg": "#7FDBFF",
                "panel_bg": "#001F3F",
                "terminal_bg": "#001F3F",
                "terminal_fg": "#7FDBFF",
                "block_outline": "#B0B0B0",
                "block_text": "#7FDBFF",
                "block_colors": ["#FF6B6B", "#4ECDC4"],
                "parity_color": "#7D7D9C",
                "button_active_bg": "#7289DA",
                "canvas_bg": "#23272A",
                "card_bg": "#1A3855",
                "border": "#4A90E2",
                "highlight_bg": "#FFF9C4",
                "highlight_fg": "#000000",
                "highlight": "#FFFF99"
            },
            "red": {
                "bg": "#000000",
                "fg": "#FF3333",
                "active_bg": "#000000",
                "active_fg": "#FFFFFF",
                "disabled_fg": "#AAAAAA",
                "button_bg": "#000000",
                "button_fg": "#FF3333",
                "button_hover": "#550000",
                "accent": "#FF5733",
                "warning": "#FF0000",
                "tooltip_bg": "#000000",
                "entry_bg": "#000000",
                "progress_fg": "#FF3333",
                "panel_bg": "#000000",
                "terminal_bg": "#000000",
                "terminal_fg": "#FF3333",
                "block_outline": "#B0B0B0",
                "block_text": "#FF3333",
                "block_colors": ["#FF6B6B", "#4ECDC4"],
                "parity_color": "#7D7D9C",
                "button_active_bg": "#7289DA",
                "canvas_bg": "#23272A",
                "card_bg": "#2A0A0A",
                "border": "#660000",
                "highlight_bg": "#E0E0E0",
                "highlight_fg": "#000000",
                "highlight": "#FFFF99"
            },
            "purple": {
                "bg": "#2B092E",
                "fg": "#BF33C9",
                "button_bg": "#4A154B",
                "button_fg": "#FFFFFF",
                "terminal_bg": "#1E1E1E",
                "terminal_fg": "#BF33C9",
                "active_bg":'#2B092E',
                "active_fg": "#FFFFFF",
                "disabled_fg": "#666666",
                "button_hover": "#3A1F5C",
                "accent": "#9370DB",
                "warning": "#FF00FF",
                "tooltip_bg": "#2E1A47",
                "entry_bg": "#2E1A47",
                "progress_fg": "#D8BFD8",
                "panel_bg": "#2E1A47",
                "block_outline": "#B0B0B0",
                "block_text": "#BF33C9",
                "block_colors": ["#FF6B6B", "#4ECDC4"],
                "parity_color": "#7D7D9C",
                "button_active_bg": "#7289DA",
                "canvas_bg": "#23272A",
                "card_bg": "#3D1A5C",
                "border": "#6A2E7A",
                "highlight_bg": "#FCE4EC",
                "highlight_fg": "#000000",
                "highlight": "#FFFF99"
            }
        }

        self.current_theme = "dark"
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TFrame', background='#000000')
        self.style.configure('TLabel', background='#000000', foreground='#00FF00', font=('Courier', 14))
        self.style.configure('TButton', background='#000000', foreground='#00FF00', font=('Courier', 14), borderwidth=0, relief='flat')
        self.style.map('TButton', background=[('active', '#003300')], foreground=[('active', '#00FF00')])
        self.style.configure('Custom.TButton', background='#000000', foreground='#00FF00', font=('Courier', 14), borderwidth=1, relief='ridge')
        self.style.map('Custom.TButton', background=[('active', '#111111')], foreground=[('active', '#FFFFFF')], relief=[('active', 'ridge'), ('pressed', 'groove')])
        self.style.configure('TopLeft.TFrame', background='#000000')
        self.style.configure('Custom.TButton', padding=(6, 6, 4, 4))
        self.style.map('Custom.TButton', background=[('active', '#111111'), ('disabled', '#1a1a1a')], foreground=[('active', '#FFFFFF'), ('disabled', '#005500')], relief=[('active', 'ridge'), ('pressed', 'groove')])
        self.original_button = ttk.Button
        self.style.configure('TEntry', fieldbackground='#000000', foreground='#00FF00', insertcolor='#00FF00', font=('Courier', 14))

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.setup_widgets()
        self.cmd_entry.bind('<Return>', lambda e: self.process_command())
        self.bind('<F1>', lambda e: self.show_help_overview())
        self.bind('<Control-a>', lambda e: self.handle_autopsy())
        self.bind('<Control-r>', lambda e: self.handle_raid())
        self.bind('<Control-w>', lambda e: self.handle_writeblocker())
        self.bind('<Control-p>', lambda e: self.handle_password_cracking())
        self.bind('<Control-s>', lambda e: self.handle_ransomware())
        self.bind('<Control-m>', lambda e: self.handle_memory_forensics())
        self.bind('<Control-n>', lambda e: self.handle_network_forensics())
        self.bind('<Control-t>', lambda e: self.handle_metadata_forensics())
        self.bind('<Control-g>', lambda e: self.handle_steganography_detection())
        self.bind('<Control-l>', lambda e: self.handle_malware_static_analysis())
        self.bind('<Control-c>', lambda e: self.handle_ctf())  # Add CTF keybinding
        self.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.create_menu_bar()

    def create_styled_button(self, parent, text, command=None, **kwargs):
        button_frame = ttk.Frame(parent, style='TopLeft.TFrame')
        button_frame.pack(fill=tk.BOTH, expand=True)
        if 'style' not in kwargs:
            kwargs['style'] = 'Custom.TButton'
        button = ttk.Button(button_frame, text=text, command=command, **kwargs)
        button.pack(fill=tk.BOTH, expand=True)
        button._frame = button_frame
        return button
    
    def center_window(self, window, width, height):
        """Center a Toplevel window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_menu_bar(self):
        theme = self.themes[self.current_theme]
        self.menu_bar = Menu(self, bg=theme["bg"], fg=theme["fg"], activebackground=theme["active_bg"], activeforeground=theme["active_fg"], relief="flat", bd=0)
        self.config(menu=self.menu_bar)
        self.help_menu = Menu(self.menu_bar, tearoff=0, bg=theme["bg"], fg=theme["fg"], activebackground=theme["active_bg"], activeforeground=theme["active_fg"], relief="flat", bd=0)
        self.help_menu.add_command(label="Help Overview (F1)", command=self.show_help_overview)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="Autopsy Demo Help (Ctrl+A)", command=self.show_autopsy_help)
        self.help_menu.add_command(label="Write Blocker Demo Help (Ctrl+W)", command=self.show_writeblocker_help)
        self.help_menu.add_command(label="Password Cracking Demo Help (Ctrl+P)", command=self.show_password_cracking_help)
        self.help_menu.add_command(label="RAID Demo Help (Ctrl+R)", command=self.show_raid_help)
        self.help_menu.add_command(label="Ransomware Demo Help (Ctrl+S)", command=self.show_ransomware_help)
        self.help_menu.add_command(label="Memory Forensics Help (Ctrl+M)", command=self.show_memory_forensics_help)
        self.help_menu.add_command(label="Network Forensics Help (Ctrl+N)", command=self.show_network_forensics_help)
        self.help_menu.add_command(label="Metadata Forensics Help (Ctrl+T)", command=self.show_metadata_forensics_help)
        self.help_menu.add_command(label="Steganography Detection Help (Ctrl+G)", command=self.show_steganography_detection_help)
        self.help_menu.add_command(label="Malware Static Analysis Help (Ctrl+L)", command=self.show_malware_static_analysis_help)
        self.help_menu.add_command(label="CTF Demo Help (Ctrl+C)", command=self.show_ctf_help)  # Add CTF help
        self.help_menu.add_separator()
        self.help_menu.add_command(label="Quick Reference", command=self.show_quick_reference)
        self.help_menu.add_separator()
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
    def create_tooltip(self, widget, text):
        def enter(event):
            theme = self.themes[self.current_theme]
            widget = event.widget
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            label = tk.Label(tip, text=text, justify=tk.LEFT, background=theme["tooltip_bg"], foreground=theme["fg"], relief=tk.SOLID, borderwidth=1, font=("Courier", 11, "normal"), padx=5, pady=5)
            label.pack(side=tk.TOP, fill=tk.BOTH)
            tip.geometry(f"+{x}+{y}")
            self.tooltip_windows[widget] = tip
        def leave(event):
            widget = event.widget
            if widget in self.tooltip_windows:
                self.tooltip_windows[widget].destroy()
                del self.tooltip_windows[widget]
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def setup_widgets(self):
        title_font = font.Font(family='Courier', size=20, weight='bold')
        self.title_label = tk.Label(self.main_frame, text="Welcome to the Digital Forensics Demo", bg="#000000", fg="#00FF00", font=title_font, cursor="hand2")
        self.title_label.pack(pady=(0, 30))
        self.title_label.bind("<Button-1>", lambda e: self.handle_title_click())
        self.theme_selector_frame = ttk.Frame(self.main_frame)
        self.theme_selector_frame.place(relx=1.0, rely=0.0, anchor='ne')
        theme_label = ttk.Label(self.theme_selector_frame, text="Theme:")
        theme_label.pack(side=tk.LEFT, padx=(0, 5))
        self.theme_combobox = ttk.Combobox(self.theme_selector_frame, values=[name.capitalize() for name in self.themes.keys()], state="readonly", width=10)
        self.theme_combobox.set(self.current_theme.capitalize())
        self.theme_combobox.pack(side=tk.LEFT)
        self.theme_combobox.bind("<<ComboboxSelected>>", lambda e: self.set_theme(self.theme_combobox.get().lower()))
        cmd_label = ttk.Label(self.main_frame, text="Type a command to begin:")
        cmd_label.pack(anchor='w', pady=(0, 5))
        self.cmd_entry = ttk.Entry(self.main_frame, width=50)
        self.cmd_entry.pack(fill=tk.X, pady=(0, 20))
        self.cmd_entry.focus_set()
        summary_frame = ttk.Frame(self.main_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        summary_label = ttk.Label(summary_frame, text="Demo Summary:")
        summary_label.pack(anchor='w', pady=(0, 5))
        self.summary_text = tk.Text(summary_frame, height=4, bg="#000000", fg="#00FF00", font=('Courier', 14), wrap=tk.WORD, bd=1, relief=tk.SOLID)
        self.summary_text.pack(fill=tk.X, expand=True)
        self.summary_text.insert(tk.END, self.default_summary)
        self.summary_text.config(state=tk.DISABLED)
        self.button_frame_row1 = ttk.Frame(self.main_frame)
        self.button_frame_row1.pack(fill=tk.X, pady=5)
        self.button_frame_row2 = ttk.Frame(self.main_frame)
        self.button_frame_row2.pack(fill=tk.X, pady=5)
        self.autopsy_btn = self.create_styled_button(self.button_frame_row1, text="Autopsy Demo", command=self.handle_autopsy)
        self.autopsy_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.autopsy_btn, "Autopsy Demo: Analyze disk images, recover files, and investigate digital evidence.")
        self.writeblocker_btn = self.create_styled_button(self.button_frame_row1, text="Write Blocker Demo", command=self.handle_writeblocker)
        self.writeblocker_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.writeblocker_btn, "Write Blocker Demo: Prevent writes to storage devices during forensic analysis.")
        self.password_cracking_btn = self.create_styled_button(self.button_frame_row1, text="Password Cracking Demo", command=self.handle_password_cracking)
        self.password_cracking_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.password_cracking_btn, "Password Cracking Demo: Recover passwords using tools like John the Ripper and Hashcat.")
        self.raid_btn = self.create_styled_button(self.button_frame_row1, text="RAID Demo", command=self.handle_raid)
        self.raid_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.raid_btn, "RAID Demo: Recover data from damaged or failed RAID arrays.")
        self.ransomware_btn = self.create_styled_button(self.button_frame_row1, text="Ransomware Demo", command=self.handle_ransomware)
        self.ransomware_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.ransomware_btn, "Ransomware Demo: Learn about ransomware attacks and defense strategies.")
        self.memory_forensics_btn = self.create_styled_button(self.button_frame_row2, text="Memory Forensics", command=self.handle_memory_forensics)
        self.memory_forensics_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.memory_forensics_btn, "Memory Forensics: Analyze RAM to uncover evidence of malicious activity.")
        self.network_forensics_btn = self.create_styled_button(self.button_frame_row2, text="Network Forensics", command=self.handle_network_forensics)
        self.network_forensics_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.network_forensics_btn, "Network Forensics: Investigate network traffic to trace cyber incidents.")
        self.metadata_forensics_btn = self.create_styled_button(self.button_frame_row2, text="Metadata Forensics", command=self.handle_metadata_forensics)
        self.metadata_forensics_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.metadata_forensics_btn, "Metadata Forensics: Extract hidden information from file metadata.")
        self.steganography_detection_btn = self.create_styled_button(self.button_frame_row2, text="Steganography Detection", command=self.handle_steganography_detection)
        self.steganography_detection_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.steganography_detection_btn, "Steganography Detection: Identify and extract hidden messages in files.")
        self.malware_static_analysis_btn = self.create_styled_button(self.button_frame_row2, text="Malware Static Analysis", command=self.handle_malware_static_analysis)
        self.malware_static_analysis_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.malware_static_analysis_btn, "Malware Static Analysis: Examine malware without execution to understand its behavior.")
        self.ctf_btn = self.create_styled_button(self.button_frame_row2, text="CTF Demo", command=self.handle_ctf)  # Add CTF button
        self.ctf_btn._frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.create_tooltip(self.ctf_btn, "CTF Demo: Participate in a Capture The Flag challenge to test your forensic skills.")

        self.autopsy_options_frame = ttk.Frame(self.main_frame)
        self.autopsy_options_frame.pack(fill=tk.X, pady=10)
        self.autopsy_options_frame.pack_forget()
        instructions_label = ttk.Label(self.autopsy_options_frame, text="Select an Autopsy option to continue:", font=('Courier', 14))
        instructions_label.pack(pady=(0, 10))
        autopsy_button_frame = ttk.Frame(self.autopsy_options_frame)
        autopsy_button_frame.pack(fill=tk.X)
        self.doc_button = self.create_styled_button(autopsy_button_frame, text="View Documentation", command=self.view_autopsy_documentation)
        self.doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.usb_image_button = self.create_styled_button(autopsy_button_frame, text="Download Demo USB Image", command=self.download_usb_image)
        self.usb_image_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.show_autopsy_image_button = self.create_styled_button(autopsy_button_frame, text="Show Kali Autopsy Image", command=self.show_kali_autopsy_image)
        self.show_autopsy_image_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.autopsy_start_button = self.create_styled_button(autopsy_button_frame, text="Start Demo", command=self.launch_autopsy_gui)
        self.autopsy_start_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.raid_options_frame = ttk.Frame(self.main_frame)
        self.raid_options_frame.pack(fill=tk.X, pady=10)
        self.raid_options_frame.pack_forget()
        raid_instructions_label = ttk.Label(self.raid_options_frame, text="Select a RAID option to continue:", font=('Courier', 14))
        raid_instructions_label.pack(pady=(0, 10))
        raid_button_frame = ttk.Frame(self.raid_options_frame)
        raid_button_frame.pack(fill=tk.X)
        self.raid_doc_button = self.create_styled_button(raid_button_frame, text="View Documentation", command=self.view_raid_documentation)
        self.raid_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.raid_gui_button = self.create_styled_button(raid_button_frame, text="Start Demo", command=self.launch_raid_gui)
        self.raid_gui_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.writeblocker_options_frame = ttk.Frame(self.main_frame)
        self.writeblocker_options_frame.pack(fill=tk.X, pady=10)
        self.writeblocker_options_frame.pack_forget()
        writeblocker_instructions_label = ttk.Label(self.writeblocker_options_frame, text="Select a Write Blocker option to continue:", font=('Courier', 14))
        writeblocker_instructions_label.pack(pady=(0, 10))
        writeblocker_button_frame = ttk.Frame(self.writeblocker_options_frame)
        writeblocker_button_frame.pack(fill=tk.X)
        self.writeblocker_doc_button = self.create_styled_button(writeblocker_button_frame, text="View Documentation", command=self.view_writeblocker_documentation)
        self.writeblocker_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.writeblocker_start_button = self.create_styled_button(writeblocker_button_frame, text="Start Demo", command=self.launch_writeblocker_gui)
        self.writeblocker_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.password_cracking_options_frame = ttk.Frame(self.main_frame)
        self.password_cracking_options_frame.pack(fill=tk.X, pady=10)
        self.password_cracking_options_frame.pack_forget()
        password_cracking_instructions_label = ttk.Label(self.password_cracking_options_frame, text="Select a Password Cracking option to continue:", font=('Courier', 14))
        password_cracking_instructions_label.pack(pady=(0, 10))
        password_cracking_button_frame = ttk.Frame(self.password_cracking_options_frame)
        password_cracking_button_frame.pack(fill=tk.X)
        self.password_cracking_doc_button = self.create_styled_button(password_cracking_button_frame, text="View Hashcat Documentation", command=self.view_password_cracking_documentation)
        self.password_cracking_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.password_cracking_doc2_button = self.create_styled_button(password_cracking_button_frame, text="View John the Ripper Documentation", command=self.view_john_ripper_documentation)
        self.password_cracking_doc2_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.password_cracking_start_button = self.create_styled_button(password_cracking_button_frame, text="Start Demo", command=self.launch_john_ripper_gui)
        self.password_cracking_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.ransomware_options_frame = ttk.Frame(self.main_frame)
        self.ransomware_options_frame.pack(fill=tk.X, pady=10)
        self.ransomware_options_frame.pack_forget()
        ransomware_instructions_label = ttk.Label(self.ransomware_options_frame, text="Select a Ransomware option to continue:", font=('Courier', 14))
        ransomware_instructions_label.pack(pady=(0, 10))
        ransomware_button_frame = ttk.Frame(self.ransomware_options_frame)
        ransomware_button_frame.pack(fill=tk.X)
        self.ransomware_doc_button = self.create_styled_button(ransomware_button_frame, text="View Documentation", command=self.view_ransomware_documentation)
        self.ransomware_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.ransomware_start_button = self.create_styled_button(ransomware_button_frame, text="Start Demo", command=self.launch_ransomware_demo)
        self.ransomware_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.memory_forensics_options_frame = ttk.Frame(self.main_frame)
        self.memory_forensics_options_frame.pack(fill=tk.X, pady=10)
        self.memory_forensics_options_frame.pack_forget()
        memory_forensics_instructions_label = ttk.Label(self.memory_forensics_options_frame, text="Select a Memory Forensics option to continue:", font=('Courier', 14))
        memory_forensics_instructions_label.pack(pady=(0, 10))
        memory_forensics_button_frame = ttk.Frame(self.memory_forensics_options_frame)
        memory_forensics_button_frame.pack(fill=tk.X)
        self.memory_forensics_doc_button = self.create_styled_button(memory_forensics_button_frame, text="View Documentation", command=self.view_memory_forensics_documentation)
        self.memory_forensics_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.memory_forensics_start_button = self.create_styled_button(memory_forensics_button_frame, text="Start Demo", command=self.launch_memory_forensics_demo)
        self.memory_forensics_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.network_forensics_options_frame = ttk.Frame(self.main_frame)
        self.network_forensics_options_frame.pack(fill=tk.X, pady=10)
        self.network_forensics_options_frame.pack_forget()
        network_forensics_instructions_label = ttk.Label(self.network_forensics_options_frame, text="Select a Network Forensics option to continue:", font=('Courier', 14))
        network_forensics_instructions_label.pack(pady=(0, 10))
        network_forensics_button_frame = ttk.Frame(self.network_forensics_options_frame)
        network_forensics_button_frame.pack(fill=tk.X)
        self.network_forensics_doc_button = self.create_styled_button(network_forensics_button_frame, text="View Documentation", command=self.view_network_forensics_documentation)
        self.network_forensics_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.network_forensics_start_button = self.create_styled_button(network_forensics_button_frame, text="Start Demo", command=self.launch_network_forensics_demo)
        self.network_forensics_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.metadata_forensics_options_frame = ttk.Frame(self.main_frame)
        self.metadata_forensics_options_frame.pack(fill=tk.X, pady=10)
        self.metadata_forensics_options_frame.pack_forget()
        metadata_forensics_instructions_label = ttk.Label(self.metadata_forensics_options_frame, text="Select a Metadata Forensics option to continue:", font=('Courier', 14))
        metadata_forensics_instructions_label.pack(pady=(0, 10))
        metadata_forensics_button_frame = ttk.Frame(self.metadata_forensics_options_frame)
        metadata_forensics_button_frame.pack(fill=tk.X)
        self.metadata_forensics_doc_button = self.create_styled_button(metadata_forensics_button_frame, text="View Documentation", command=self.view_metadata_forensics_documentation)
        self.metadata_forensics_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.metadata_forensics_start_button = self.create_styled_button(metadata_forensics_button_frame, text="Start Demo", command=self.launch_metadata_forensics_demo)
        self.metadata_forensics_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.steganography_detection_options_frame = ttk.Frame(self.main_frame)
        self.steganography_detection_options_frame.pack(fill=tk.X, pady=10)
        self.steganography_detection_options_frame.pack_forget()
        steganography_detection_instructions_label = ttk.Label(self.steganography_detection_options_frame, text="Select a Steganography Detection option to continue:", font=('Courier', 14))
        steganography_detection_instructions_label.pack(pady=(0, 10))
        steganography_detection_button_frame = ttk.Frame(self.steganography_detection_options_frame)
        steganography_detection_button_frame.pack(fill=tk.X)
        self.steganography_doc_button = self.create_styled_button(steganography_detection_button_frame, text="View Documentation", command=self.view_steganography_documentation)
        self.steganography_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.steganography_start_button = self.create_styled_button(steganography_detection_button_frame, text="Start Demo", command=self.launch_steganography_detection_demo)
        self.steganography_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.malware_static_analysis_options_frame = ttk.Frame(self.main_frame)
        self.malware_static_analysis_options_frame.pack(fill=tk.X, pady=10)
        self.malware_static_analysis_options_frame.pack_forget()
        malware_static_analysis_instructions_label = ttk.Label(self.malware_static_analysis_options_frame, text="Select a Malware Static Analysis option to continue:", font=('Courier', 14))
        malware_static_analysis_instructions_label.pack(pady=(0, 10))
        malware_static_analysis_button_frame = ttk.Frame(self.malware_static_analysis_options_frame)
        malware_static_analysis_button_frame.pack(fill=tk.X)
        self.malware_doc_button = self.create_styled_button(malware_static_analysis_button_frame, text="View Documentation", command=self.view_malware_documentation)
        self.malware_doc_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        self.malware_start_button = self.create_styled_button(malware_static_analysis_button_frame, text="Start Demo", command=self.launch_malware_static_analysis_demo)
        self.malware_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.ctf_options_frame = ttk.Frame(self.main_frame)  # Add CTF options frame
        self.ctf_options_frame.pack(fill=tk.X, pady=5)
        self.ctf_options_frame.pack_forget()
        ctf_instructions_label = ttk.Label(self.ctf_options_frame, text="Select a CTF option to continue:", font=('Courier', 14))
        ctf_instructions_label.pack(pady=(0, 10))
        ctf_button_frame = ttk.Frame(self.ctf_options_frame)
        ctf_button_frame.pack(fill=tk.X)
        self.ctf_start_button = self.create_styled_button(ctf_button_frame, text="Start Demo", command=self.launch_ctf_demo)
        self.ctf_start_button.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X)

        self.output_text = tk.Text(self.main_frame, height=15, bg="#000000", fg="#00FF00", insertbackground="#00FF00")
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(20, 10))
        self.output_text.config(state=tk.DISABLED)
        self.status_bar = tk.Frame(self, bg="#000000", bd=1, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_bar, text="Ready", bg="#000000", fg="#00FF00", font=("Courier", 10), anchor=tk.W, bd=0, padx=10, pady=2)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.resource_label = tk.Label(self.status_bar, text="CPU: -- | MEM: --", bg="#000000", fg="#00FF00", font=("Courier", 10), anchor=tk.E, bd=0, padx=10, pady=2)
        self.resource_label.pack(side=tk.RIGHT)
        self.clock_label = tk.Label(self.status_bar, text="", bg="#000000", fg="#00FF00", font=("Courier", 10), anchor=tk.E, bd=0, padx=10, pady=2)
        self.clock_label.pack(side=tk.RIGHT)
        self.update_clock()

    def update_clock(self):
        try:
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            if self.clock_label.winfo_exists():
                self.clock_label.config(text=current_time)
                self.update_resource_monitor()
                self.after(1000, self.update_clock)
        except Exception as e:
            print(f"Error updating clock: {e}")

    def update_resource_monitor(self):
        if not PSUTIL_AVAILABLE:
            if self.resource_label.winfo_exists():
                self.resource_label.config(text="CPU: N/A | MEM: N/A")
            return
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            mem_percent = memory.percent
            mem_used = memory.used / (1024 * 1024 * 1024)
            mem_total = memory.total / (1024 * 1024 * 1024)
            resource_text = f"CPU: {cpu_percent:.1f}% | MEM: {mem_percent:.1f}% ({mem_used:.1f}/{mem_total:.1f} GB)"
            if cpu_percent > 80 or mem_percent > 80:
                color = "#FF0000"
            elif cpu_percent > 50 or mem_percent > 50:
                color = "#FFFF00"
            else:
                color = "#00FF00"
            if self.resource_label.winfo_exists():
                self.resource_label.config(text=resource_text, fg=color)
        except Exception as e:
            print(f"Error updating resource monitor: {e}")
            if self.resource_label.winfo_exists():
                self.resource_label.config(text="CPU: ERR | MEM: ERR")

    def toggle_fullscreen(self):
        try:
            if self.is_fullscreen:
                if platform.system() == 'Windows':
                    self.state('normal')
                else:
                    self.attributes('-fullscreen', False)
                self.geometry('1024x768')
                self.is_fullscreen = False
                self.display_output("Exited fullscreen mode. Press F11 to restore.")
            else:
                if platform.system() == 'Windows':
                    self.state('zoomed')
                else:
                    self.attributes('-fullscreen', True)
                self.is_fullscreen = True
                self.display_output("Entered fullscreen mode. Press ESC or F11 to exit.")
        except Exception as e:
            print(f"Error toggling fullscreen mode: {e}")
            if platform.system() == 'Windows':
                self.state('normal')
            else:
                self.attributes('-fullscreen', False)
            self.geometry('1024x768')
            self.is_fullscreen = False

    def update_status(self, message):
        self.current_status = message
        self.status_label.config(text=message)

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme()
            self.display_output(f"Switched to {theme_name} theme")
        else:
            self.display_output(f"Theme '{theme_name}' not found")

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.configure(bg=theme["bg"])
        self.main_frame.configure(style='TFrame')
        self.style.configure('TFrame', background=theme["bg"])
        self.style.configure('TLabel', background=theme["bg"], foreground=theme["fg"])
        self.style.configure('TButton', background=theme["button_bg"], foreground=theme["fg"])
        self.style.map('TButton', background=[('active', theme["active_bg"])], foreground=[('active', theme["active_fg"])])
        self.style.configure('Custom.TButton', background=theme["button_bg"], foreground=theme["fg"])
        self.style.map('Custom.TButton', background=[('active', theme["button_hover"]), ('disabled', theme["disabled_fg"])], foreground=[('active', theme["active_fg"]), ('disabled', theme["disabled_fg"])])
        self.style.configure('TEntry', fieldbackground=theme["entry_bg"], foreground=theme["fg"], insertcolor=theme["fg"])
        self.title_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.summary_text.configure(bg=theme["bg"], fg=theme["fg"])
        self.output_text.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
        self.status_bar.configure(bg=theme["bg"])
        self.status_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.resource_label.configure(bg=theme["bg"])
        self.clock_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.menu_bar.configure(bg=theme["bg"], fg=theme["fg"], activebackground=theme["active_bg"], activeforeground=theme["active_fg"])
        self.help_menu.configure(bg=theme["bg"], fg=theme["fg"], activebackground=theme["active_bg"], activeforeground=theme["active_fg"])
        # Update all open demo windows with the new theme
        for window, app in list(self.open_demo_windows.items()):
            if window.winfo_exists() and hasattr(app, 'set_theme'):
                app.set_theme(self.current_theme)

    def display_image(self, image_path):
        try:
            task_id = f"image_load_{os.path.basename(image_path)}"
            self.progress_tracker(task_id, f"Loading image: {os.path.basename(image_path)}", 10)
            self.remove_displayed_image()
            if not os.path.exists(image_path):
                self.progress_tracker(task_id, f"Image file not found: {image_path}", complete=True)
                raise FileNotFoundError(f"Image file '{image_path}' not found")
            self.progress_tracker(task_id, f"Processing image: {os.path.basename(image_path)}", 30)
            img = Image.open(image_path)
            width, height = img.size
            max_width = 500
            max_height = 400
            if width > max_width or height > max_height:
                ratio = min(max_width/width, max_height/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label = tk.Label(self.main_frame, image=photo, bg="#000000")
            self.image_label.image = photo
            self.image_label.pack(pady=10, before=self.output_text)
            self.progress_tracker(task_id, f"Image displayed: {os.path.basename(image_path)}", 100, complete=True)
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", error_msg)
        except Exception as e:
            error_msg = f"Error displaying image: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def get_elapsed_time(self):
        import datetime
        if self.operation_start_time:
            elapsed = datetime.datetime.now() - self.operation_start_time
            return elapsed
        return None

    def format_elapsed_time(self, elapsed=None):
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

    def progress_tracker(self, task_id, message, share=None, complete=False):
        if task_id not in self.active_progress_tasks and not complete:
            self.active_progress_tasks[task_id] = {'start_time': self.start_operation_timer(), 'last_update': 0, 'message': message}
            self.display_output(f"▶ Started: {message}")
            self.update_status(f"▶ {message}")
            return
        if task_id in self.active_progress_tasks:
            task = self.active_progress_tasks[task_id]
            significant_change = False
            if share is not None:
                if share - task['last_update'] >= 10 or share >= 100:
                    significant_change = True
                    task['last_update'] = share
            status_message = message
            if share is not None:
                status_message = f"{message} ({share}%)"
            elapsed = self.get_elapsed_time()
            if elapsed:
                elapsed_str = self.format_elapsed_time(elapsed)
                status_message = f"{status_message} - {elapsed_str}"
            self.update_status(status_message)
            if significant_change and not complete:
                progress_bar = '█' * int(share/10) + '░' * (10-int(share/10))
                self.display_output(f"◯ Progress: {progress_bar} {share}% - {message}")
            if complete:
                elapsed_str = self.format_elapsed_time()
                self.display_output(f"✓ Completed: {message} (took {elapsed_str})")
                self.update_status(f"✓ {message} - Complete")
                self.update_resource_monitor()
                del self.active_progress_tasks[task_id]

    def view_autopsy_documentation(self):
        self.display_output("Opening Autopsy documentation...")
        current_dir = os.getcwd()
        self.display_output(f"Current working directory: {current_dir}")
        rel_pdf_path = os.path.join("Assets", "Step-by-Step Guide_ Using Autopsy.pdf")
        abs_pdf_path = os.path.abspath(rel_pdf_path)
        self.display_output(f"Full PDF path: {abs_pdf_path}")
        try:
            if not os.path.exists(abs_pdf_path):
                self.display_output(f"File not found at: {abs_pdf_path}")
                raise FileNotFoundError(f"PDF file not found at: {abs_pdf_path}")
            if not os.path.isfile(abs_pdf_path):
                self.display_output(f"Path exists but is not a file: {abs_pdf_path}")
                raise FileNotFoundError(f"Path is not a valid file: {abs_pdf_path}")
            file_size = os.path.getsize(abs_pdf_path)
            self.display_output(f"File size: {file_size} bytes")
            self.display_output(f"Opening PDF file using platform: {platform.system()}")
            if platform.system() == 'Windows':
                self.display_output("Using Windows 'start' command to open PDF...")
                try:
                    result = subprocess.run(['cmd', '/c', 'start', '', abs_pdf_path], shell=False, check=True, capture_output=True)
                    self.display_output(f"Command executed successfully with return code: {result.returncode}")
                except subprocess.SubprocessError as se:
                    self.display_output(f"First attempt failed: {se}, trying with shell=True...")
                    result = subprocess.run(f'start "" "{abs_pdf_path}"', shell=True, check=True, capture_output=True)
                    self.display_output(f"Second attempt completed with return code: {result.returncode}")
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_pdf_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_pdf_path], check=True)
            self.display_output("Documentation file opened successfully")
        except FileNotFoundError as fnf:
            self.display_output(f"Error: PDF file not found: {str(fnf)}")
            messagebox.showerror("File Not Found", f"Failed to open Autopsy documentation: {str(fnf)}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Autopsy documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Autopsy documentation: {error_msg}")

    def view_writeblocker_documentation(self):
        self.display_output("Opening Write Blocker documentation...")
        doc_filename = "Assets/WriteBlockerDoc.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Write Blocker documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Write Blocker documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Write Blocker documentation: {error_msg}")

    def view_password_cracking_documentation(self):
        self.display_output("Opening Password Cracking documentation...")
        doc_filename = "Assets/hashcat_user_manual.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Password Cracking documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Password Cracking documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Password Cracking documentation: {error_msg}")

    def view_john_ripper_documentation(self):
        self.display_output("Opening Password Cracking documentation...")
        doc_filename = "Assets/JohnReadme.md"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Password Cracking documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Password Cracking documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Password Cracking documentation: {error_msg}")

    def view_raid_documentation(self):
        self.display_output("Opening RAID documentation...")
        doc_filename = "Assets/RAID_Configuration.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open RAID documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open RAID documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open RAID documentation: {error_msg}")

    def view_ransomware_documentation(self):
        self.display_output("Opening Ransomware documentation...")
        doc_filename = "Assets/Ransomware_Documentation_CISA.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Ransomware documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Ransomware documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Ransomware documentation: {error_msg}")

    def view_memory_forensics_documentation(self):
        self.display_output("Opening Memory Forensics documentation...")
        doc_filename = "Assets/Volatility3Readme.md"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Memory Forensics documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Memory Forensics documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Memory Forensics documentation: {error_msg}")

    def view_network_forensics_documentation(self):
        self.display_output("Opening Network Forensics documentation...")
        doc_filename = "Assets/Wireshark User's Guide.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Network Forensics documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Network Forensics documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Network Forensics documentation: {error_msg}")

    def view_metadata_forensics_documentation(self):
        self.display_output("Opening Metadata Forensics documentation...")
        doc_filename = "Assets/index.rst.txt"  # Placeholder; adjust if a specific file exists
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Metadata Forensics documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Metadata Forensics documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Metadata Forensics documentation: {error_msg}")

    def view_steganography_documentation(self):
        self.display_output("Opening Steganography Detection documentation...")
        doc_filename = "Assets/stegosuite.md"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Steganography Detection documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Steganography Detection documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Steganography Detection documentation: {error_msg}")

    def view_malware_documentation(self):
        self.display_output("Opening Malware Static Analysis documentation...")
        doc_filename = "Assets/r2book.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("File Not Found", f"Failed to open Malware Static Analysis documentation: {error_msg}")
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", f"Failed to open Malware Static Analysis documentation: {error_msg}")
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", f"Failed to open Malware Static Analysis documentation: {error_msg}")

    def show_kali_autopsy_image(self):
        try:
            base_filename = "Assets/Kali open autopsy"
            image_path, found = self.check_file_with_extensions(base_filename + ".png", [".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"])
            if not found:
                raise FileNotFoundError("Could not find 'Kali open autopsy' image with any standard extension")
            self.display_output("Displaying Kali Autopsy image...")
            self.display_image(image_path)
        except Exception as e:
            error_msg = f"Error displaying Kali Autopsy image: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def download_usb_image(self):
        self.display_output("Preparing USB image for forensic analysis...")
        self.display_output(f"Found image: {USB_IMAGE_CONFIG['sample_image_name']} ready to be used")
        try:
            usb_dialog = tk.Toplevel(self)
            usb_dialog.title("Download USB Image")
            usb_dialog.geometry("500x300")
            usb_dialog.configure(bg=self.themes[self.current_theme]["bg"])
            usb_dialog.transient(self)
            usb_dialog.grab_set()
            usb_dialog.update_idletasks()
            width = usb_dialog.winfo_width()
            height = usb_dialog.winfo_height()
            x = (usb_dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (usb_dialog.winfo_screenheight() // 2) - (height // 2)
            usb_dialog.geometry(f'{width}x{height}+{x}+{y}')
            title_label = ttk.Label(usb_dialog, text="USB Image Download", font=('Courier', 16, 'bold'))
            title_label.pack(pady=20)
            desc_label = ttk.Label(usb_dialog, text="Select an option below to obtain a USB image\nfor analysis in Autopsy.", font=('Courier', 14))
            desc_label.pack(pady=10)
            buttons_frame = ttk.Frame(usb_dialog, style='TopLeft.TFrame')
            buttons_frame.pack(fill=tk.X, padx=20, pady=10)
            sample_button = self.create_styled_button(buttons_frame, text="Download Sample Image", command=lambda: self.process_sample_image_download(usb_dialog))
            sample_button.pack(fill=tk.X, pady=5)
            button = sample_button.winfo_children()[0]
            button.config(text=f"Download Demo USB Image ({USB_IMAGE_CONFIG['sample_image_name']})")
            path_button = self.create_styled_button(buttons_frame, text="Specify Image Location", command=lambda: self.specify_image_path(usb_dialog))
            path_button.pack(fill=tk.X, pady=5)
        except Exception as e:
            error_msg = f"Error setting up USB image download: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def process_sample_image_download(self, parent_dialog):
        try:
            task_id = f"image_download_{id(parent_dialog)}"
            self.progress_tracker(task_id, "Preparing USB image download", 0)
            source_path = os.path.join(USB_IMAGE_CONFIG["sample_image_path"], USB_IMAGE_CONFIG["sample_image_name"])
            if not os.path.exists(source_path):
                messagebox.showerror("Error", f"Sample image not found at: {source_path}")
                self.display_output(f"Error: Sample image file not found at {source_path}")
                self.progress_tracker(task_id, "Image download failed - file not found", complete=True)
                return
            self.progress_tracker(task_id, "USB image located, preparing download", 10)
            if platform.system() == 'Windows':
                target_dir = os.path.join(os.path.expanduser("~"), "Documents", "Autopsy")
            else:
                target_dir = USB_IMAGE_CONFIG["autopsy_import_dir"]
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, USB_IMAGE_CONFIG["sample_image_name"])
            file_size = os.path.getsize(source_path)
            progress_dialog = tk.Toplevel(parent_dialog)
            progress_dialog.title("Copying Image File")
            progress_dialog.geometry("400x150")
            progress_dialog.configure(bg=self.themes[self.current_theme]["bg"])
            progress_dialog.transient(parent_dialog)
            progress_dialog.update_idletasks()
            width = progress_dialog.winfo_width()
            height = progress_dialog.winfo_height()
            x = (parent_dialog.winfo_rootx() + parent_dialog.winfo_width() // 2) - (width // 2)
            y = (parent_dialog.winfo_rooty() + parent_dialog.winfo_height() // 2) - (height // 2)
            progress_dialog.geometry(f'{width}x{height}+{x}+{y}')
            message_label = ttk.Label(progress_dialog, text=f"Copying USB image ({int(file_size/1024/1024/1024)} GB)...", font=('Courier', 14))
            message_label.pack(pady=10)
            progress_bar = ttk.Progressbar(progress_dialog, orient="horizontal", length=300, mode="determinate")
            progress_bar.pack(pady=10)
            status_label = ttk.Label(progress_dialog, text="Starting copy operation...", font=('Courier', 10))
            status_label.pack(pady=5)
            def copy_file():
                try:
                    total_size = os.path.getsize(source_path)
                    copied_size = 0
                    with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                        buffer_size = 1024 * 1024
                        buffer = src.read(buffer_size)
                        while buffer:
                            dst.write(buffer)
                            copied_size += len(buffer)
                            progress = int((copied_size / total_size) * 100)
                            self.after(0, lambda p=progress: self.progress_tracker(task_id, f"Copying USB image", p))
                            buffer = src.read(buffer_size)
                    return True, "File copied successfully"
                except Exception as e:
                    return False, str(e)
            def perform_copy_with_progress():
                progress_bar["value"] = 10
                progress_dialog.update()
                status_label.config(text="Initializing copy operation...")
                self.progress_tracker(task_id, "Initializing copy operation", 20)
                progress_bar["value"] = 30
                progress_dialog.update()
                import threading
                copy_thread = threading.Thread(target=lambda: copy_file())
                copy_thread.start()
                def check_copy_status():
                    progress_dialog.update()
                    status_label.config(text=f"Copying file... ({progress_bar['value']}%)")
                    if copy_thread.is_alive():
                        progress_dialog.after(100, check_copy_status)
                    else:
                        status_label.config(text="Copy complete!")
                        progress_dialog.update()
                        progress_dialog.after(500, finish_copy)
                progress_dialog.after(100, check_copy_status)
                def finish_copy():
                    progress_dialog.destroy()
                    parent_dialog.destroy()
                    if os.path.exists(target_path):
                        self.progress_tracker(task_id, f"USB image copied successfully to: {target_path}", 100, complete=True)
                        self.display_output(f"Copy completed successfully! The USB image has been copied to:\n{target_path}\n\nThis image is now ready for analysis in Autopsy.")
                    else:
                        raise FileNotFoundError("Failed to copy image file")
            perform_copy_with_progress()
        except Exception as e:
            error_msg = f"Error during USB image operation: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def specify_image_path(self, parent_dialog):
        try:
            path_dialog = tk.Toplevel(parent_dialog)
            path_dialog.title("Specify Image Path")
            path_dialog.geometry("450x200")
            path_dialog.configure(bg=self.themes[self.current_theme]["bg"])
            path_dialog.transient(parent_dialog)
            path_dialog.update_idletasks()
            width = path_dialog.winfo_width()
            height = path_dialog.winfo_height()
            x = (parent_dialog.winfo_rootx() + parent_dialog.winfo_width() // 2) - (width // 2)
            y = (parent_dialog.winfo_rooty() + parent_dialog.winfo_height() // 2) - (height // 2)
            path_dialog.geometry(f'{width}x{height}+{x}+{y}')
            instruction_label = ttk.Label(path_dialog, text="Enter the full path to the USB image file:", font=('Courier', 14))
            instruction_label.pack(pady=10)
            path_entry = ttk.Entry(path_dialog, width=50)
            path_entry.pack(pady=10, padx=20)
            button_frame = ttk.Frame(path_dialog, style='TopLeft.TFrame')
            button_frame.pack(padx=20, pady=10)
            browse_button = self.create_styled_button(button_frame, text="Browse...", command=lambda: self.browse_for_image(path_entry))
            browse_button.pack(side=tk.LEFT, padx=5)
            submit_button = self.create_styled_button(button_frame, text="Submit", command=lambda: self.process_image_path(path_entry.get(), path_dialog, parent_dialog))
            submit_button.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            error_msg = f"Error creating path dialog: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def browse_for_image(self, entry_widget):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(title="Select USB Image File", filetypes=[("Disk Image Files", "*.dd *.raw *.img *.E01 *.001"), ("All Files", "*.*")])
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def process_image_path(self, image_path, path_dialog, parent_dialog):
        if not image_path.strip():
            messagebox.showerror("Error", "Please enter a valid path")
            return
        try:
            if os.path.exists(image_path):
                if not hasattr(self, 'current_image_path'):
                    self.current_image_path = image_path
                else:
                    self.current_image_path = image_path
                if platform.system() != 'Windows':
                    try:
                        os.makedirs(USB_IMAGE_CONFIG["autopsy_import_dir"], exist_ok=True)
                        symlink_path = os.path.join(USB_IMAGE_CONFIG["autopsy_import_dir"], os.path.basename(image_path))
                        if os.path.exists(symlink_path):
                            os.unlink(symlink_path)
                        os.symlink(image_path, symlink_path)
                    except Exception as sym_err:
                        self.display_output(f"Symlink failed, copying file: {str(sym_err)}")
                        shutil.copy2(image_path, symlink_path)
                    self.display_output(f"Image is now available at: {symlink_path}")
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

    def view_writeblocker_documentation(self):
        self.display_output("Opening Write Blocker documentation...")
        doc_filename = "Assets/WriteBlockerDoc.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            create_response = messagebox.askyesno("File Not Found", f"The Write Blocker documentation file was not found at: {abs_doc_path}\n\nWould you like to create a sample documentation file?")
            if create_response:
                self.create_writeblocker_documentation()
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", error_msg)
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def view_password_cracking_documentation(self):
        self.display_output("Opening Password Cracking documentation...")
        doc_filename = "Assets/hashcat_user_manual.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            create_response = messagebox.askyesno("File Not Found", f"The Password Cracking documentation file was not found at: {abs_doc_path}\n\nWould you like to create a sample documentation file?")
            if create_response:
                self.create_password_cracking_documentation()
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", error_msg)
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def view_john_ripper_documentation(self):
        self.display_output("Opening Password Cracking documentation...")
        doc_filename = "Assets/JohnReadme.md"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            create_response = messagebox.askyesno("File Not Found", f"The Password Cracking documentation file was not found at: {abs_doc_path}\n\nWould you like to create a sample documentation file?")
            if create_response:
                self.create_password_cracking_documentation()
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", error_msg)
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def view_ransomware_documentation(self):
        self.display_output("Opening Ransomware documentation...")
        doc_filename = "Assets/Ransomware_Documentation_CISA.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            create_response = messagebox.askyesno("File Not Found", f"The Ransomware documentation file was not found at: {abs_doc_path}\n\nWould you like to create a sample documentation file?")
            if create_response:
                self.create_ransomware_documentation()
        except subprocess.SubprocessError as spe:
            error_msg = f"Error executing file open command: {str(spe)}"
            self.display_output(error_msg)
            messagebox.showerror("Command Error", error_msg)
        except Exception as e:
            error_msg = f"Error opening documentation file: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def view_raid_documentation(self):
        self.display_output("Opening RAID documentation...")
        doc_filename = "Assets/RAID_Configuration.pdf"
        try:
            abs_doc_path = os.path.abspath(doc_filename)
            self.display_output(f"Looking for documentation at: {abs_doc_path}")
            if not os.path.exists(abs_doc_path):
                raise FileNotFoundError(f"Documentation file '{abs_doc_path}' not found")
            self.display_output(f"Opening documentation using platform: {platform.system()}")
            if platform.system() == 'Windows':
                powershell_cmd = f'Start-Process "{abs_doc_path}"'
                subprocess.run(['powershell', '-command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', abs_doc_path], check=True)
            else:
                subprocess.run(['xdg-open', abs_doc_path], check=True)
            self.display_output("Documentation opened successfully")
        except FileNotFoundError as e:
            error_msg = f"Documentation file not found: {str(e)}"
            self.display_output(error_msg)
            create_response = messagebox.askyesno("File Not Found", f"The RAID documentation file was not found at: {abs_doc_path}\n\nWould you like to create a sample documentation file?")
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

    # def on_raid_window_close(self, window):
    #     try:
    #         self.display_output("RAID visualization window closed")
    #         window.destroy()
    #     except Exception as e:
    #         pass

    def handle_ctf(self):
        self.update_summary(self.ctf_summary)
        self.display_output("Preparing CTF Demo options...")
        self.update_status("Working with CTF tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.ctf_options_frame.pack(fill=tk.X, pady=5, after=self.button_frame_row2)

    def launch_ctf_demo(self):
        try:
            self.display_output("Launching CTF Demo...")
            for window, app in list(self.open_demo_windows.items()):
                if window.title() == "CTF Demo" and window.winfo_exists():
                    self.display_output("CTF Demo is already running.")
                    return

            # Create external Toplevel
            ctf_window = tk.Toplevel(self)
            ctf_window.title("CTF Demo")
            ctf_window.geometry("1280x850")
            self.center_window(ctf_window, 1280, 850)

            # Embed MainApp Frame in that window
            app = ctf.MainApp(
                master=ctf_window,
                theme=self.themes[self.current_theme],
                next_callback=lambda: None,
                app=self,
                apply_theme_callback=self.apply_theme_to_demo
            )

            # Register window/app
            self.open_demo_windows[ctf_window] = app

            # Handle close
            ctf_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(ctf_window, "CTF Demo"))

            self.display_output("CTF Demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching CTF Demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)


    def handle_raid(self):
        self.update_summary(self.raid_summary)
        self.display_output("Initializing RAID recovery tools...")
        self.update_status("Working with RAID recovery tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.raid_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    # def on_writeblocker_window_close(self, window):
    #     try:
    #         self.display_output("Write Blocker GUI window closed")
    #         window.destroy()
    #     except Exception as e:
    #         pass

    # def on_john_ripper_window_close(self, window):
    #     try:
    #         self.display_output("Password Cracking GUI window closed")
    #         window.destroy()
    #     except Exception as e:
    #         pass

    def initialize_ransomware_files(self):
        try:
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

    # def on_ransomware_window_close(self, window):
    #     try:
    #         self.display_output("Ransomware demo window closed")
    #         self.update_status("Ready")
    #         window.destroy()
    #     except Exception as e:
    #         print(f"Error during window cleanup: {str(e)}")

    def handle_autopsy(self):
        self.update_summary(self.autopsy_summary)
        self.display_output("Preparing Autopsy digital forensics options...")
        self.update_status("Working with Autopsy tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.autopsy_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_writeblocker(self):
        self.update_summary(self.writeblocker_summary)
        self.display_output("Preparing Write Blocker demo options...")
        self.update_status("Working with Write Blocker tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.writeblocker_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_password_cracking(self):
        self.update_summary(self.password_cracking_summary)
        self.display_output("Preparing Password Cracking demo options...")
        self.update_status("Working with Password Cracking tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.password_cracking_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_ransomware(self):
        self.update_summary(self.ransomware_summary)
        self.display_output("Preparing Ransomware demo options...")
        self.update_status("Working with Ransomware tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.ransomware_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_memory_forensics(self):
        self.update_summary(self.memory_forensics_summary)
        self.display_output("Preparing Memory Forensics demo options...")
        self.update_status("Working with Memory Forensics tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.memory_forensics_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_network_forensics(self):
        self.update_summary(self.network_forensics_summary)
        self.display_output("Preparing Network Forensics demo options...")
        self.update_status("Working with Network Forensics tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.network_forensics_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_metadata_forensics(self):
        self.update_summary(self.metadata_forensics_summary)
        self.display_output("Preparing Metadata Forensics demo options...")
        self.update_status("Working with Metadata Forensics tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.metadata_forensics_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_steganography_detection(self):
        self.update_summary(self.steganography_detection_summary)
        self.display_output("Preparing Steganography Detection demo options...")
        self.update_status("Working with Steganography Detection tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.steganography_detection_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)

    def handle_malware_static_analysis(self):
        self.update_summary(self.malware_static_analysis_summary)
        self.display_output("Preparing Malware Static Analysis demo options...")
        self.update_status("Working with Malware Static Analysis tools")
        self.update_resource_monitor()
        self.hide_all_option_frames()
        self.malware_static_analysis_options_frame.pack(fill=tk.X, pady=10, after=self.button_frame_row2)


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
        self.display_output("🥚 Easter Eggs List 🥚")
        self.display_output("1. Click the title \"Welcome to the Digital Forensics Demo\" to see the Cyber Ring image")
        self.display_output("2. Type \"meow\" in the command box to see an ASCII cat")
        self.display_output("3. Type \"hakercat\" to see a special image")
        self.cmd_entry.delete(0, tk.END)

    def process_command(self):
        command = self.cmd_entry.get().strip().lower()
        self.hide_all_option_frames()
        if command != "hakercat":
            self.remove_displayed_image()
        if command == "meow":
            self.handle_meow()
        elif command == "hakercat":
            self.display_output("HakerCat activated! Displaying Meow-Frame...")
            self.display_image("Assets/Meow-Frame.webp")
        elif command == "eggs":
            self.handle_eggs()
        elif command == "autopsy":
            self.handle_autopsy()
        elif command == "writeblocker":
            self.handle_writeblocker()
        elif command == "password cracking":
            self.handle_password_cracking()
        elif command == "raid":
            self.handle_raid()
        elif command == "ransomware":
            self.handle_ransomware()
        elif command == "memory forensics":
            self.handle_memory_forensics()
        elif command == "network forensics":
            self.handle_network_forensics()
        elif command == "metadata forensics":
            self.handle_metadata_forensics()
        elif command == "steganography detection":
            self.handle_steganography_detection()
        elif command == "malware static analysis":
            self.handle_malware_static_analysis()
        elif command == "ctf":  # Add CTF command
            self.handle_ctf()
        elif command == "exit":
            self.quit()
        else:
            self.display_output(f"Unknown command: {command}. Type 'help' for available commands.")
        self.cmd_entry.delete(0, tk.END)

    def update_summary(self, summary_text):
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
        self.summary_text.config(state=tk.DISABLED)

    def hide_all_option_frames(self):
        for frame in [self.autopsy_options_frame, self.raid_options_frame,
                      self.writeblocker_options_frame, self.password_cracking_options_frame,
                      self.ransomware_options_frame, self.memory_forensics_options_frame,
                      self.network_forensics_options_frame, self.metadata_forensics_options_frame,
                      self.steganography_detection_options_frame, self.malware_static_analysis_options_frame, self.ctf_options_frame]:
            frame.pack_forget()

    def display_output(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def remove_displayed_image(self):
        if self.image_label:
            self.image_label.destroy()
            self.image_label = None

    def launch_autopsy_gui(self):
        try:
            self.display_output("Launching Autopsy demo...")
            autopsy_window = tk.Toplevel(self)
            autopsy_window.title("Autopsy Digital Forensics Demo")
            autopsy_window.geometry("1280x850")
            self.center_window(autopsy_window, 1280, 720)
            app = autopsy_demo.AutopsyDemo(autopsy_window, next_callback=lambda: None, app=self, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            autopsy_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(autopsy_window, "Autopsy"))
            self.open_demo_windows[autopsy_window] = app
            self.display_output("Autopsy demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Autopsy demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_memory_forensics_demo(self):
        try:
            self.display_output("Launching Memory Forensics demo...")
            memory_window = tk.Toplevel(self)
            memory_window.title("Memory Forensics Demo")
            memory_window.geometry("1280x850")
            self.center_window(memory_window, 1280, 720)
            app = memory_demo.MainApp(memory_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            memory_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(memory_window, "Memory Forensics"))
            self.open_demo_windows[memory_window] = app
            self.display_output("Memory Forensics demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Memory Forensics demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_network_forensics_demo(self):
        try:
            self.display_output("Launching Network Forensics demo...")
            network_window = tk.Toplevel(self)
            network_window.title("Network Forensics Demo")
            network_window.geometry("1280x850")
            self.center_window(network_window, 1280, 850)
            app = network_demo.MainApp(network_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            network_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(network_window, "Network Forensics"))
            self.open_demo_windows[network_window] = app
            self.display_output("Network Forensics demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Network Forensics demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_metadata_forensics_demo(self):
        try:
            self.display_output("Launching Metadata Forensics demo...")
            metadata_window = tk.Toplevel(self)
            metadata_window.title("Metadata Forensics Demo")
            metadata_window.geometry("1280x850")
            self.center_window(metadata_window, 1280, 720)
            app = metadata_demo.MainApp(metadata_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            metadata_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(metadata_window, "Metadata Forensics"))
            self.open_demo_windows[metadata_window] = app
            self.display_output("Metadata Forensics demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Metadata Forensics demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_raid_gui(self):
        try:
            self.display_output("Launching RAID demo...")
            raid_window = tk.Toplevel(self)
            raid_window.title("RAID Demo")
            raid_window.geometry("1280x850")
            self.center_window(raid_window, 1280, 720)
            app = raid.MainApp(raid_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            raid_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(raid_window, "RAID"))
            self.open_demo_windows[raid_window] = app
            self.display_output("RAID demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching RAID demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_writeblocker_gui(self):
        try:
            self.display_output("Launching Write Blocker demo...")
            writeblocker_window = tk.Toplevel(self)
            writeblocker_window.title("Write Blocker Demo")
            writeblocker_window.geometry("1280x850")
            self.center_window(writeblocker_window, 1280, 720)
            app = write_blocker_gui.MainApp(writeblocker_window, theme=self.themes[self.current_theme], apply_theme_callback=lambda theme: self.apply_theme_to_demo(app, theme))
            writeblocker_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(writeblocker_window, "Write Blocker"))
            self.open_demo_windows[writeblocker_window] = app
            self.display_output("Write Blocker demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Write Blocker demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_john_ripper_gui(self):
        try:
            self.display_output("Launching Password Cracking demo...")
            john_window = tk.Toplevel(self)
            john_window.title("Password Cracking Demo")
            john_window.geometry("1280x850")
            self.center_window(john_window, 1280, 720)
            app = john_ripper_gui.MainApp(john_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            john_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(john_window, "Password Cracking"))
            self.open_demo_windows[john_window] = app
            self.display_output("Password Cracking demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Password Cracking demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_ransomware_demo(self):
        try:
            self.display_output("Launching Ransomware demo...")
            ransomware_window = tk.Toplevel(self)
            ransomware_window.title("Ransomware Demo")
            ransomware_window.geometry("1280x850")
            self.center_window(ransomware_window, 1280, 720)
            app = ransom.MainApp(ransomware_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            ransomware_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(ransomware_window, "Ransomware"))
            self.open_demo_windows[ransomware_window] = app
            self.display_output("Ransomware demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Ransomware demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_steganography_detection_demo(self):
        try:
            self.display_output("Launching Steganography Detection demo...")
            steganography_window = tk.Toplevel(self)
            steganography_window.title("Steganography Detection Demo")
            steganography_window.geometry("1280x850")
            self.center_window(steganography_window, 1280, 720)
            # Assuming SteganographyDetection has a MainApp class similar to others
            from SteganographyDetection import steganography_detection  # Adjust import based on actual module name
            app = steganography_detection.MainApp(steganography_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            steganography_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(steganography_window, "Steganography Detection"))
            self.open_demo_windows[steganography_window] = app
            self.display_output("Steganography Detection demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Steganography Detection demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def launch_malware_static_analysis_demo(self):
        try:
            self.display_output("Launching Malware Static Analysis demo...")
            malware_window = tk.Toplevel(self)
            malware_window.title("Malware Static Analysis Demo")
            malware_window.geometry("1280x850")
            self.center_window(malware_window, 1280, 720)
            # Assuming MalwareStaticAnalysis has a MainApp class similar to others
            from MalwareStaticAnalysis import malware_analysis  # Adjust import based on actual module name
            app = malware_analysis.MainApp(malware_window, theme=self.themes[self.current_theme], apply_theme_callback=self.apply_theme_to_demo)
            malware_window.protocol("WM_DELETE_WINDOW", lambda: self.on_demo_close(malware_window, "Malware Static Analysis"))
            self.open_demo_windows[malware_window] = app
            self.display_output("Malware Static Analysis demo launched successfully")
        except Exception as e:
            error_msg = f"Error launching Malware Static Analysis demo: {str(e)}"
            self.display_output(error_msg)
            messagebox.showerror("Error", error_msg)

    def apply_theme_to_demo(self, demo_app, theme):
        demo_app.apply_theme(theme)

    def on_demo_close(self, window, name):
        try:
            if window in self.open_demo_windows:
                app = self.open_demo_windows[window]
                if hasattr(app, 'close_demo'):
                    app.close_demo()  # Let MainApp handle its own cleanup
                del self.open_demo_windows[window]
            window.destroy()
            self.display_output(f"{name} closed.")
        except Exception as e:
            self.display_output(f"Error closing {name}: {str(e)}")
            messagebox.showerror("Error", f"Error closing {name}: {str(e)}")

    def create_sample_autopsy_doc(self):
        pass  # Implementation remains as placeholder

    def create_writeblocker_documentation(self):
        pass  # Implementation remains as placeholder

    def create_password_cracking_documentation(self):
        pass  # Implementation remains as placeholder

    def create_ransomware_documentation(self):
        pass  # Implementation remains as placeholder

    def create_raid_documentation(self):
        pass  # Implementation remains as placeholder

    def create_memory_forensics_documentation(self):
        pass  # Implementation remains as placeholder

    def create_network_forensics_documentation(self):
        pass  # Implementation remains as placeholder

    def create_metadata_forensics_documentation(self):
        pass  # Implementation remains as placeholder

    def create_steganography_documentation(self):
        pass  # New placeholder for steganography documentation

    def create_malware_documentation(self):
        pass  # New placeholder for malware documentation

    def show_help_overview(self):
        help_text = """Digital Forensics Demo Help Overview
Available Commands:
- autopsy: Launch the Autopsy demo (Ctrl+A)
- writeblocker: Launch the Write Blocker demo (Ctrl+W)
- password cracking: Launch the Password Cracking demo (Ctrl+P)
- raid: Launch the RAID demo (Ctrl+R)
- ransomware: Launch the Ransomware demo (Ctrl+S)
- memory forensics: Launch the Memory Forensics demo (Ctrl+M)
- network forensics: Launch the Network Forensics demo (Ctrl+N)
- metadata forensics: Launch the Metadata Forensics demo (Ctrl+T)
- steganography detection: Launch the Steganography Detection demo (Ctrl+G)
- malware static analysis: Launch the Malware Static Analysis demo (Ctrl+L)
- exit: Close the application
Keyboard Shortcuts:
- F1: Show this help overview
- F11/Esc: Toggle fullscreen mode
- Ctrl+A: Autopsy demo
- Ctrl+W: Write Blocker demo
- Ctrl+P: Password Cracking demo
- Ctrl+R: RAID demo
- Ctrl+S: Ransomware demo
- Ctrl+M: Memory Forensics demo
- Ctrl+N: Network Forensics demo
- Ctrl+T: Metadata Forensics demo
- Ctrl+G: Steganography Detection demo
- Ctrl+L: Malware Static Analysis demo
Use the menu bar at the top for more help options."""
        self.display_output("\n" + help_text + "\n")

    def show_autopsy_help(self):
        self.display_output("Autopsy Help: Use the Autopsy demo to analyze disk images, recover files, and investigate digital evidence. Select 'View Documentation' for a detailed guide or 'Start Demo' to begin.")

    def show_writeblocker_help(self):
        self.display_output("Write Blocker Help: Learn how to prevent writes to storage devices during forensic analysis. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_password_cracking_help(self):
        self.display_output("Password Cracking Help: Recover passwords using tools like John the Ripper. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_raid_help(self):
        self.display_output("RAID Help: Recover data from damaged or failed RAID arrays. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_ransomware_help(self):
        self.display_output("Ransomware Help: Learn about ransomware attacks and defense strategies. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_memory_forensics_help(self):
        self.display_output("Memory Forensics Help: Analyze RAM to uncover evidence of malicious activity. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_network_forensics_help(self):
        self.display_output("Network Forensics Help: Investigate network traffic to trace cyber incidents. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_metadata_forensics_help(self):
        self.display_output("Metadata Forensics Help: Extract hidden information from file metadata. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_steganography_detection_help(self):
        self.display_output("Steganography Detection Help: Identify and extract hidden messages in files. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_malware_static_analysis_help(self):
        self.display_output("Malware Static Analysis Help: Examine malware without execution to understand its behavior. Select 'View Documentation' for more details or 'Start Demo' to begin.")

    def show_ctf_help(self):
        self.display_output("CTF Demo Help: Participate in a Capture The Flag challenge to test your forensic skills. Select 'Start Demo' to begin.")

    def show_quick_reference(self):
        quick_ref = """Quick Reference Guide
Commands:
- autopsy (Ctrl+A)
- writeblocker (Ctrl+W)
- password cracking (Ctrl+P)
- raid (Ctrl+R)
- ransomware (Ctrl+S)
- memory forensics (Ctrl+M)
- network forensics (Ctrl+N)
- metadata forensics (Ctrl+T)
- steganography detection (Ctrl+G)
- malware static analysis (Ctrl+L)
- exit
Shortcuts:
- F1: Help Overview
- F11/Esc: Toggle Fullscreen"""
        self.display_output("\n" + quick_ref + "\n")

if __name__ == "__main__":
    app = DigitalForensicsDemo()
    app.mainloop()