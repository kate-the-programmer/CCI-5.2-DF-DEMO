import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw, ImageTk, ImageFont
import random
import os
import json
import threading
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --- Configuration ---
FONT = 'Courier'
WINDOW_SIZE = '1280x800'

# Default theme matching Password Cracking Demo
DEFAULT_THEME = {
    "bg": "#2B092E",
    "fg": "#BF33C9",
    "button_bg": "#4A154B",
    "button_fg": "#FFFFFF",
    "terminal_bg": "#1E1E1E",
    "terminal_fg": "#BF33C9",
    "active_fg": "#FFFFFF",
    "disabled_fg": "#666666"
}

# File paths
SCRIPT_DIR = Path(__file__).parent
volatility_dir = SCRIPT_DIR.parent / 'MemoryForensics' / 'volatility3'
VOLATILITY_PATH = volatility_dir / 'vol.py'
OUTPUT_DIR = SCRIPT_DIR / 'output_dir'
OUTPUT_DIR.mkdir(exist_ok=True)

DEMO_FILES_DIR = SCRIPT_DIR / "CTFFiles"
SCORES_FILE = DEMO_FILES_DIR / "scores.txt"
RAID_FILES = [DEMO_FILES_DIR / f"raid_file_{i}.txt" for i in range(1, 5)]
MEMORY_DUMP_PATH = DEMO_FILES_DIR / "sample.mem"
PCAP_FILE = DEMO_FILES_DIR / "new_sample3.pcap"
ZIP_FILE_PATH = DEMO_FILES_DIR / "secret.zip"
HASH_FILE_PATH = DEMO_FILES_DIR / "zip_hash.txt"
WORDLIST_PATH = DEMO_FILES_DIR / "john.lst"
MD5_HASH_FILE = DEMO_FILES_DIR / "md5_hash.txt"
KEYWORD_SEARCH = DEMO_FILES_DIR / "keyword_search.txt"
TIMELINE_FILE = DEMO_FILES_DIR / "timeline.txt"
EXPORT_EVIDENCE_FILE = DEMO_FILES_DIR / "export_evidence.txt"
FILE_LIST_FILE = DEMO_FILES_DIR / "file_list.txt"


META_FILES = {
    'Photo 1 (JPG)': DEMO_FILES_DIR / 'ad000001.jpg',
    'PDF 1 (PDF)': DEMO_FILES_DIR / 'ESC_0001.pdf',
    'PDF 2 (PDF)': DEMO_FILES_DIR / 'HAR_0001.pdf',
    'Powerpoint Presentation (PPTX)': DEMO_FILES_DIR / 'CISA.pptx',
    'PDF 3 (PDF)': DEMO_FILES_DIR / 'HAR_0005.pdf',
    'Photo 2 (JPG)': DEMO_FILES_DIR / 'DSCN0010.jpg',
    'Photo 3 (JPG)': DEMO_FILES_DIR / 'BlueSquare.jpg',
    'AI Generated Image (JPG)': DEMO_FILES_DIR / 'AIImage.jpg',
    'Steganography Image (PNG)': DEMO_FILES_DIR / 'stegopicmsg.png',
}

# --- Utility Functions ---
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

def verify_required_images():
    missing_images = []
    image_file = "CTF.jpg"
    full_path = DEMO_FILES_DIR / image_file
    if not os.path.exists(full_path):
        missing_images.append(full_path)
    return len(missing_images) == 0, missing_images

def typewriter_effect(text_id, canvas, full_text, current_text="", index=0):
    if index < len(full_text):
        current_text += full_text[index]
        canvas.itemconfig(text_id, text=current_text + "_")
        canvas.after(50, lambda: typewriter_effect(text_id, canvas, full_text, current_text, index + 1))
    else:
        canvas.itemconfig(text_id, text=full_text)

def decrypt_animation(widget, original_text, step=0):
    if not widget.winfo_exists():
        return
    total_steps = 30
    if step >= total_steps:
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", original_text)
        widget.config(state="disabled")
        return
    fraction = step / total_steps
    display_text = list(original_text)
    for i in range(len(original_text)):
        if i < int(fraction * len(original_text)):
            pass
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", ''.join(display_text))
    widget.config(state="disabled")
    widget.after(100, lambda: decrypt_animation(widget, original_text, step + 1))

def encrypt(text, shift=3):
    return "".join(chr((ord(c) - 97 + shift) % 26 + 97) if c.islower() else chr((ord(c) - 65 + shift) % 26 + 65) if c.isupper() else c for c in text)

def decrypt(text, shift=3):
    return encrypt(text, -shift)

# --- Page Content Definitions ---
class PageContent:
    @staticmethod
    def instructions():
        return (
            "Welcome to the Capture The Flag (CTF) Demo!\n"
            "This demo simulates a series of digital forensics challenges.\n\n"
            "How it works:\n"
            "- Enter a username to begin.\n"
            "- Select a challenge to attempt (e.g., RAID, Steganography).\n"
            "- Use terminal commands within challenges to analyze files and find flags.\n"
            "- Submit flags to earn points, tracked on the scoreboard.\n\n"
            "Next, proceed to username entry."
        )

    @staticmethod
    def username():
        return (
            "Enter Username\n"
            "Please enter your username to start the CTF.\n"
            "Click 'Start CTF' to begin."
        )

    @staticmethod
    def dashboard():
        return (
            "Welcome!\n"
            "Select a challenge to start. Each challenge has a score value."
        )

    @staticmethod
    def raid():
        return (
            "Analyze the files, the flag is the RAID configuration for these files, Flag{RAID#}\n"
            "Click on a file block to view details and determine the RAID configuration."
        )

    @staticmethod
    def ransomware():
        return (
            "Identify phishing emails to uncover the flag, find the first three capital letters in the message of the Phishing emails, ex: Flag{CAPITALLETTERS}\n"
            "Click on an email to view its content and identify phishing emails."
        )

    @staticmethod
    def memory_forensics():
        return (
            "Analyze a memory dump to find hidden data.\n"
            "Use Volatility3 commands to discover the flag, check the results in the terminal. Format: Flag{flag}"
        )

    @staticmethod
    def network_forensics():
        return (
            "Investigate network traffic for suspicious activity.\n"
            "Use Wireshark/tshark to examine 'new_sample3.pcap'. Investigate IPs, ports, protocols, and flag exfiltration."
        )

    @staticmethod
    def autopsy():
        return (
            "Analyze a disk image for evidence of a crime.\n"
            "Use Autopsy commands to uncover evidence and find the flag."
        )

    @staticmethod
    def steganography():
        return (
            "Find hidden messages in images or audio files.\n"
            "Select an image and use Stegosuite to check capacity and extract hidden messages. The flag (Format: Flag{flag}) may be embedded."
        )

    @staticmethod
    def password_cracking():
        return (
            "Crack a password hash using various techniques.\n"
            "Crack passwords from a ZIP file and MD5 hash using John the Ripper and Hashcat. The flag (Format: Flag{flag}) is the cracked password."
        )

    @staticmethod
    def metadata_forensics():
        return (
            "Extract metadata from files to find hidden information.\n"
            "Select a file and use Exiftool to extract metadata. The flag (Format: Flag{META_FLAG987}) is hidden in the metadata."
        )

    @staticmethod
    def malware_static_analysis():
        return (
            "Analyze a malware sample without executing it.\n"
            "Use Strings and PEfile to analyze a malware sample and find the flag."
        )

    @staticmethod
    def score_graph():
        return (
            "User Scores (Top Score Highlighted)\n"
            "View the total scores of all users."
        )

# --- Main Application ---
class MainApp(tk.Frame):
    def __init__(self, master, theme, next_callback, app, apply_theme_callback):
        super().__init__(master)
        self.master = master
        self.theme = theme
        self.next_callback = next_callback
        self.app = app
        self.apply_theme_callback = apply_theme_callback
        self.current_user = None
        self.scores = {}
        self.challenges = {
            "RAID": {"description": "Analyze the files, the flag is the RAID configuration for these files, Flag{RAID#}", "score": 100},
            "Ransomware": {"description": "Identify phishing emails to uncover the flag, find the first three capital letters in the message of the Phishing emails, ex: Flag{CAPITALLETTERS}", "score": 100},
            "Memory Forensics": {"description": "Analyze a memory dump to find hidden data.", "score": 100},
            "Network Forensics": {"description": "Investigate network traffic for suspicious activity.", "score": 100},
            "Autopsy": {"description": "Analyze a disk image for evidence of a crime.", "score": 100},
            "Steganography": {"description": "Find hidden messages in images or audio files.", "score": 100},
            "Password Cracking": {"description": "Crack a password hash using various techniques.", "score": 100},
            "Metadata Forensics": {"description": "Extract metadata from files to find hidden information.", "score": 100},
            "Malware Static Analysis": {"description": "Analyze a malware sample without executing it.", "score": 100},
        }
        self.ZIP_FILE_PATH = ZIP_FILE_PATH
        self.HASH_FILE_PATH = HASH_FILE_PATH
        self.WORDLIST_PATH = WORDLIST_PATH
        self.MD5_HASH_FILE = MD5_HASH_FILE
        self.TITLE_FONT = ("Courier New", 26)
        self.TEXT_FONT = ("Courier New", 17)
        self.BUTTON_FONT = ("Courier New", 14)
        self.current_page = "Instructions"
        self.canvas = None
        self.bg_image_id = None
        self.bg_photo = None
        self.canvas_width = 1200
        self.canvas_height = 760
        self.demo_frame = None
        self.flag_frame = None
        self.terminal_challenge = None

        self.pack(fill=tk.BOTH, expand=True)
        # Delay canvas creation to ensure master is ready
        self.master.after(100, self.initialize_ui)

    def initialize_ui(self):
        self.create_canvas()
        self.bind("<Configure>", self.on_window_resize)
        self.initialize_raid_files()
        self.show_page()

    
    def animate_instruction_decrypt(self, label, original_text, step=0):
        if not label.winfo_exists():
            return
        total_steps = 30
        if step >= total_steps:
            label.config(text=original_text)
            return
        fraction = step / total_steps
        display_text = list(original_text)
        for i in range(len(original_text)):
            if i >= int(fraction * len(original_text)):
                if display_text[i] not in '\n ':
                    display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
        label.config(text=''.join(display_text))
        label.after(100, lambda: self.animate_instruction_decrypt(label, original_text, step + 1))

    def on_window_resize(self, event):
        if event.widget == self:
            self.after(100, self.update_layout)

    def update_layout(self):
        self.update_idletasks()
        actual_width = self.winfo_width()
        actual_height = self.winfo_height()
        if (hasattr(self, 'last_width') and hasattr(self, 'last_height') and
            abs(actual_width - self.last_width) < 50 and 
            abs(actual_height - self.last_height) < 50):
            return
        self.last_width = actual_width
        self.last_height = actual_height
        canvas_width = max(1200, actual_width - 40)
        canvas_height = max(760, actual_height - 40)
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.show_page()
        if self.current_page == "Dashboard":
            self.show_dashboard()

    def create_background(self):
        width = self.canvas_width
        height = self.canvas_height
        img = Image.new("RGB", (width, height), self.theme["bg"])
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        chars = '0 1 █ ▓ ▒ ░'.split()
        for x in range(0, width, 20):
            for y in range(0, height, 20):
                if random.random() > 0.9:
                    draw.text((x, y), random.choice(chars), font=font, fill=self.theme["fg"])
        self.bg_photo = ImageTk.PhotoImage(img)
        if self.bg_image_id:
            self.canvas.delete(self.bg_image_id)
        self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        self.canvas.tag_lower(self.bg_image_id)

    def apply_theme(self, theme=None):
        theme = theme if theme else self.theme
        self.configure(bg=theme["bg"])
        self.canvas.configure(bg=theme["bg"])
        self.create_background()
        if self.apply_theme_callback:
            self.apply_theme_callback(theme)

    def create_canvas(self):
        self.update_idletasks()
        window_width = max(1200, self.winfo_width() - 40)
        window_height = max(760, self.winfo_height() - 40)
        self.canvas = tk.Canvas(self, width=window_width, height=window_height, bg=self.theme["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_width = window_width
        self.canvas_height = window_height
        self.create_background()

    def show_page(self):
        # Close any open Toplevel windows before destroying frames
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()

        # Destroy demo_frame if it exists to clear challenge content
        if hasattr(self, 'demo_frame') and self.demo_frame and self.demo_frame.winfo_exists():
            self.demo_frame.destroy()
        if hasattr(self, 'flag_frame') and self.flag_frame and self.flag_frame.winfo_exists():
            self.flag_frame.destroy()
        if hasattr(self, 'terminal_challenge') and self.terminal_challenge:
            if hasattr(self.terminal_challenge, 'frame') and self.terminal_challenge.frame.winfo_exists():
                self.terminal_challenge.frame.destroy()
            self.terminal_challenge = None

        self.canvas.delete("all")
        self.create_background()

        if self.current_page == "Instructions":
            self.show_instructions()
        elif self.current_page == "Username":
            self.show_username()
        elif self.current_page == "Dashboard":
            self.show_dashboard()
        elif self.current_page in self.challenges:
            self.show_challenge(self.current_page)

    def show_instructions(self):
        title_id = self.canvas.create_text(50, 30, text="CTF Demo Instructions", font=self.TITLE_FONT, fill=self.theme["fg"], anchor="nw")
        text_id = self.canvas.create_text(50, 80, text="", font=self.TEXT_FONT, fill=self.theme["fg"], anchor="nw")
        typewriter_effect(text_id, self.canvas, PageContent.instructions())
        next_button = tk.Button(self, text="Next", font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                            command=lambda: self.set_page("Username"))
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 50, window=next_button)

    def show_username(self):
        self.canvas.delete("all")
        self.create_background()

        title_id = self.canvas.create_text(50, 30, text="Username Entry", font=self.TITLE_FONT, fill=self.theme["fg"], anchor="nw")
        text_id = self.canvas.create_text(50, 80, text="", font=self.TEXT_FONT, fill=self.theme["fg"], anchor="nw")
        typewriter_effect(text_id, self.canvas, PageContent.username())

        if not self.current_user:
            content_width = max(800, self.canvas_width - 100)
            content_height = 200  # Increased height to accommodate all elements

            input_frame = tk.Frame(self, bg=self.theme["bg"])
            self.canvas.create_window(50, 150, anchor="nw", window=input_frame, width=content_width, height=content_height)

            # Username label
            username_label = tk.Label(input_frame, text="Enter Username:", font=self.TEXT_FONT, bg=self.theme["bg"], fg=self.theme["fg"])
            username_label.pack(pady=10)

            # Username entry
            self.username_entry = tk.Entry(input_frame, font=self.TEXT_FONT, bg="#333333", fg=self.theme["fg"], insertbackground=self.theme["fg"])
            self.username_entry.pack(pady=5)

            # Start CTF button
            start_button = tk.Button(input_frame, text="Start CTF", font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                    command=self.start_ctf)
            start_button.pack(pady=10)
        else:
            self.set_page("Dashboard")

    def logout(self):
        self.current_user = None
        self.set_page("Username")

    def show_dashboard(self):
        self.canvas.delete("all")
        self.create_background()

        title_id = self.canvas.create_text(50, 30, text="Dashboard", font=self.TITLE_FONT, fill=self.theme["fg"], anchor="nw")
        text_id = self.canvas.create_text(50, 80, text="", font=self.TEXT_FONT, fill=self.theme["fg"], anchor="nw")
        typewriter_effect(text_id, self.canvas, PageContent.dashboard())

        # Exit, Scoreboard, and Logout buttons at top right
        exit_button = tk.Button(self, text="Exit", font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                               command=self.master.quit)
        self.canvas.create_window(self.canvas_width - 100, 50, window=exit_button)

        scoreboard_button = tk.Button(self, text="Scoreboard", font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                     command=self.show_scoreboard)
        self.canvas.create_window(self.canvas_width - 200, 50, window=scoreboard_button)

        logout_button = tk.Button(self, text="Logout", font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                 command=self.logout)
        self.canvas.create_window(self.canvas_width - 300, 50, window=logout_button)

        # Frame to hold challenge buttons, centered on canvas
        button_frame = tk.Frame(self, bg=self.theme["bg"])
        self.canvas.create_window(self.canvas_width // 2, self.canvas_height // 2, window=button_frame, anchor="center")

        # Use grid to arrange buttons in a centered layout
        num_challenges = len(self.challenges)
        cols = 3  # Number of columns for the grid
        rows = (num_challenges + cols - 1) // cols  # Calculate rows needed

        # Calculate padding to center the grid vertically
        button_height = 40  # Approximate height of each button
        total_height = rows * button_height + (rows - 1) * 10  # Height with padding
        vertical_padding = max(0, (self.canvas_height // 2 - total_height // 2))

        for i, challenge in enumerate(self.challenges):
            row = i // cols
            col = i % cols
            btn = tk.Button(button_frame, text=challenge, font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                           command=lambda c=challenge: self.set_page(c))
            btn.grid(row=row, column=col, padx=10, pady=(vertical_padding if row == 0 else 10, 10 if row == rows - 1 else 0))

        # Ensure the frame adjusts to fit all buttons
        button_frame.update_idletasks()

    def show_scoreboard(self):
        self.canvas.delete("all")
        self.create_background()

        title_id = self.canvas.create_text(50, 30, text="Scoreboard", font=self.TITLE_FONT, fill=self.theme["fg"], anchor="nw")
        text_id = self.canvas.create_text(50, 80, text="", font=self.TEXT_FONT, fill=self.theme["fg"], anchor="nw")
        instructions = "View the total scores of all users.\nNo flag submission required on this page."
        typewriter_effect(text_id, self.canvas, instructions)

        # Load scores
        scores = self.load_scores()
        score_text = "User Scores:\n\n"
        for user, challenges in scores.items():
            total = sum(challenges.get(challenge, 0) for challenge in self.challenges)
            score_text += f"{user}: {total} points\n"

        score_id = self.canvas.create_text(50, 150, text=score_text, font=self.TEXT_FONT, fill=self.theme["fg"], anchor="nw")

        back_button = tk.Button(self, text="Back to Dashboard", font=self.BUTTON_FONT, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                            command=lambda: self.set_page("Dashboard"))
        self.canvas.create_window(self.canvas_width - 100, self.canvas_height - 50, window=back_button)

    
    def show_challenge(self, challenge_name):
        self.canvas.delete("all")
        self.create_background()

        title_id = self.canvas.create_text(self.canvas_width // 2, 60, text=challenge_name, font=self.TITLE_FONT, fill=self.theme["fg"], anchor="n")
        text_id = self.canvas.create_text(self.canvas_width // 2, 110, text="", font=self.TEXT_FONT, fill=self.theme["fg"], anchor="n", width=self.canvas_width - 100, justify="center")
        instructions = getattr(PageContent, challenge_name.lower().replace(" ", "_"))()
        typewriter_effect(text_id, self.canvas, instructions)

        content_offset = 200  # Fixed offset below instructions

        if challenge_name == "RAID":
            self.demo_frame = tk.Frame(self, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=self.canvas_width // 2 - 400, y=content_offset)
            canvas_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(canvas_frame, bg=self.theme["bg"], highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.RAIDChallenge(canvas, self)
            self.create_flag_submission_frame(challenge_name)

        elif challenge_name == "Ransomware":
            self.demo_frame = tk.Frame(self, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=self.canvas_width // 2 - 400, y=content_offset)
            canvas_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(canvas_frame, bg=self.theme["bg"], height=100, width=900)
            canvas.pack(fill=tk.BOTH, expand=True)
            emails = [
                ("Email 1", "To: John Doe\nFrom: support@securelogin.com\nSubject: Urgent Account Verification Required\nPlease act now: your account will be suspended unless you verify your login details immediately. click this link to proceed: http://verify-login.exe. this is a critical security update, and failure to act will result in permanent account lockout."),
                ("Email 2", "To: Team Members\nFrom: manager@company.org\nSubject: Team Meeting Tomorrow\nTeam meeting scheduled for tomorrow at 10 AM in Conference Room A. Please come prepared with your project updates. The agenda will include a review of last quarter's performance and planning for the next phase."),
                ("Email 3", "To: Employee List\nFrom: hr@company.org\nSubject: High Priority Task\nHelp needed: we are behind deadline on the quarterly report. complete this document now and submit It to the hr department by end of day. this is essential for our compliance audit.\naccess the form here: http://complete-report.doc."),
                ("Email 4", "To: Friends\nFrom: jane.smith@gmail.com\nSubject: Birthday Party Invite\nYou're invited to my birthday party! Please RSVP by Friday. The event will be at my place, 123 Happy St, starting at 7 PM. Bring a dish to share if you can."),
                ("Email 5", "To: Purchasing Dept\nFrom: logistics@supplychain.com\nSubject: Shipment Delay Notification\nSecure shipment: your recent order has been held up due to customs issues. approve this document immediately to avoid penalties. click Here to sign: http://approve-shipment.xls."),
                ("Email 6", "To: All Stakeholders\nFrom: projectlead@company.org\nSubject: Project Status Update\nProject status update sent to all stakeholders. We've made significant progress on the backend integration, with 75% completion. The next milestone is scheduled for next week."),
                ("Email 7", "To: Accounting Team\nFrom: boss@company.org\nSubject: Urgent Invoice Approval\nInform Now: the boss needs parts ordered for the production line. send your card info now to process the payment. use this link to submit: http://payment-portal.pdf."),
                ("Email 8", "To: Cardholder\nFrom: banksecurity@trustedbank.com\nSubject: Card Access Issue\nGuard access: your purchase card access is locked due to a security review. share details urgently to unlock it: http://unlock-card.exe. this is a standard procedure.")
            ]
            self.RansomwareChallenge(canvas, self, emails)
            self.create_flag_submission_frame(challenge_name)

        elif challenge_name in ["Memory Forensics", "Network Forensics", "Autopsy", "Steganography", "Password Cracking", "Metadata Forensics", "Malware Static Analysis"]:
            self.demo_frame = tk.Frame(self, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=0, y=content_offset)
            canvas_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            canvas_frame.pack(pady=(0, 5), fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(canvas_frame, bg=self.theme["bg"], highlightthickness=0, width=self.canvas_width, height=self.canvas_height - content_offset - 100)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.terminal_challenge = self.TerminalChallengeView(canvas, self, challenge_name)
            canvas.create_window((0, 0), window=self.terminal_challenge.frame, anchor="nw")
            self.create_flag_submission_frame(challenge_name)

    def start_ctf(self):
        username = self.username_entry.get().strip()
        if username:
            self.current_user = username
            self.set_page("Dashboard")
        else:
            messagebox.showwarning("Input Error", "Please enter a username!")

    def create_flag_submission_frame(self, challenge_name):
        if hasattr(self, 'flag_frame') and self.flag_frame and self.flag_frame.winfo_exists():
            self.flag_frame.destroy()

        self.flag_frame = tk.Frame(self, bg=self.theme["bg"])

        # Label
        label = tk.Label(self.flag_frame, text="Enter flag:", font=("Courier", 14),
                        bg=self.theme["bg"], fg=self.theme["fg"])
        label.pack(side=tk.LEFT, padx=(0, 10))

        # Entry
        self.flag_entry = tk.Entry(self.flag_frame, font=("Courier", 14), width=40,
                                bg=self.theme["terminal_bg"], fg=self.theme["fg"],
                                insertbackground=self.theme["fg"])
        self.flag_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Submit
        submit_button = tk.Button(self.flag_frame, text="Submit Flag", font=("Courier", 14),
                                bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                command=lambda: self.submit_flag(challenge_name, self.flag_entry.get()))
        submit_button.pack(side=tk.LEFT, padx=(0, 10))

        # Back
        back_button = tk.Button(self.flag_frame, text="Back to Dashboard", font=("Courier", 14),
                                bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                command=lambda: self.set_page("Dashboard"))
        back_button.pack(side=tk.LEFT)

        # Place the frame at the bottom center
        self.flag_frame.update_idletasks()
        frame_width = self.flag_frame.winfo_reqwidth()
        x = (self.canvas_width - frame_width) // 2
        y = self.canvas_height - 80
        self.flag_frame.place(x=x, y=y)

    def set_page(self, page):
        self.current_page = page
        self.show_page()

    def initialize_raid_files(self):
        os.makedirs(DEMO_FILES_DIR, exist_ok=True)
        raid_data = {
            RAID_FILES[0]: "RAID 0 - RAID 0: Striping - Data is split across multiple disks to increase read/write speeds.",
            RAID_FILES[1]: "RAID 0 - RAID 0: Striping - Data is split across multiple disks to increase read/write speeds.",
            RAID_FILES[2]: "RAID 1: Mirroring - Identical data is written to two disks for redundancy.",
            RAID_FILES[3]: "RAID 1: Mirroring - Identical data is written to two disks for redundancy.",
        }
        for file_path, data in raid_data.items():
            if not os.path.exists(file_path):
                writefile(data, file_path)

    def append_terminal_text(self, message):
        if self.terminal_challenge and self.terminal_challenge.terminal_output.winfo_exists():
            self.terminal_challenge.append_terminal_text(self.terminal_challenge.terminal_output, message)

    def load_scores(self):
        try:
            if os.path.exists(SCORES_FILE):
                return json.loads(readfile(SCORES_FILE))
            return {}
        except Exception:
            return {}

    def save_scores(self):
        try:
            writefile(json.dumps(self.scores, indent=2), SCORES_FILE)
        except Exception:
            pass
    
    def show_popup(self, title, message, error=False):
        popup = tk.Toplevel(self.master)
        popup.title(title)
        popup.geometry("400x200")
        popup.configure(bg=self.theme["bg"])
        popup.transient(self.master)   # ✅ Keep it attached to CTF window
        popup.grab_set()               # ✅ Makes it modal
        popup.focus_force()            # ✅ Focus on this popup
        popup.lift()                   # ✅ Bring above other windows

        label = tk.Label(popup, text=message, font=("Courier", 14), bg=self.theme["bg"], fg=self.theme["fg"], wraplength=350)
        label.pack(pady=20, padx=20)

        button = tk.Button(popup, text="OK", command=popup.destroy,
                            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                            font=("Courier", 12), width=10)
        button.pack(pady=10)


    def submit_flag(self, challenge_name, flag):
        correct_flags = {
            "Memory Forensics": "Flag{v0lat1lity}",
            "Network Forensics": "Flag{w1r3sh4rk}",
            "Autopsy": "Flag{AU70P5Y}",
            "Steganography": "Flag{STEGO_FLAG123}",
            "RAID": "Flag{RAID1}",
            "Ransomware": "Flag{PHISHING}",
            "Password Cracking": "Flag{j0hnth3h4shc4t}",
            "Metadata Forensics": "Flag{M3t4D474}",
            "Malware Static Analysis": "Flag{M4LW4R3.3X3}"
        }

        if flag == correct_flags.get(challenge_name):
            if self.current_user:
                score = self.challenges[challenge_name]["score"]
                self.scores.setdefault(self.current_user, {})[challenge_name] = score
                self.save_scores()
                self.show_popup("Success", f"Correct flag! You earned {score} points!")
            else:
                self.show_popup("Session Error", "Correct flag, but no active user session detected!")
        else:
            self.show_popup("Error", "Incorrect flag. Try again!", error=True)

    def get_challenge_commands(self, challenge_name):
        commands = {
            "Memory Forensics": [
                f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.pslist',
                f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.malfind',
                f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.pstree',
                f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.netscan',
                f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.dlllist',
                f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" -o "{OUTPUT_DIR}" windows.malfind --dump'
            ],
            "Network Forensics": [
                f'tshark -r "{PCAP_FILE}" -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e frame.len',
                f'tshark -r "{PCAP_FILE}" -T fields -e ip.src -e ip.dst | sort | uniq -c',
                f'tshark -r "{PCAP_FILE}" -T fields -e ip.src -e ip.dst -e ip.proto -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport',
                f'tshark -r "{PCAP_FILE}" -T fields -e frame.number -e ip.src -e ip.dst -e tcp.flags -e frame.len | sort -k 5 -nr',
                'curl ipinfo.io/199.201.110.204'
            ],
            "Password Cracking": [
                f'zip2john "{ZIP_FILE_PATH}" > "{HASH_FILE_PATH}"',
                f'john --wordlist="{WORDLIST_PATH}" "{HASH_FILE_PATH}"',
                f'john --show "{HASH_FILE_PATH}"',
                'hashcat --help',
                f'hashcat -m 0 -a 0 "{MD5_HASH_FILE}" "{WORDLIST_PATH}" --force'
            ],
            "Autopsy": [
                f'autopsy --analyze "{MEMORY_DUMP_PATH}" --keyword-search',
                f'autopsy --analyze "{MEMORY_DUMP_PATH}" --file-list',
                f'autopsy --analyze "{MEMORY_DUMP_PATH}" --timeline',
                f'autopsy --analyze "{MEMORY_DUMP_PATH}" --export-evidence'
            ],
            "Metadata Forensics": [
                'exiftool "{selected_file}"'  # Placeholder, will be replaced dynamically
            ],
            "Malware Static Analysis": [
                'strings "{malware_file}"',
                'pefile "{malware_file}"'  # Placeholder for pefile command
            ]
        }
        return commands.get(challenge_name, [])

    def handle_ransomware_decrypt(self, key):
        if key == "key123":
            self.append_terminal_text("Decrypting file... [OUTPUT] Decrypted: RANSOM_FLAG321")
        else:
            self.append_terminal_text("Decryption failed. Use correct key: key123")

    def run_command(self, command, callback, text_widget):
        def execute():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                callback(result.stdout.strip(), result.stderr.strip())
            except subprocess.CalledProcessError as e:
                callback(None, f'[ERROR] {e.stderr.strip()}')
            except FileNotFoundError:
                callback(None, f'[ERROR] Command not found: {command}')
            except Exception as e:
                callback(None, f'[ERROR] Unexpected error: {str(e)}')
        threading.Thread(target=execute, daemon=True).start()

    # --- Challenge Classes ---
    class RAIDChallenge:
        def __init__(self, canvas, parent):
            self.canvas = canvas
            self.parent = parent
            self.theme = parent.theme
            self.block_coords = {}
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.canvas.after(200, self.create_raid_image)

        def draw_simple_block(self, draw, x, y, width, height, color, text, raid_type, disk, segment):
            draw.rounded_rectangle([x, y, x + width, y + height], radius=10, fill=color, outline=self.theme["fg"], width=2)
            text_bbox = draw.textbbox((0, 0), text, font=ImageFont.load_default())
            tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            draw.text((x + (width - tw) // 2, y + (height - th) // 2), text, fill=self.theme["button_fg"], font=ImageFont.load_default())
            self.block_coords[(x, y, x + width, y + height)] = (raid_type, disk, segment)

        def on_canvas_click(self, event):
            x, y = event.x, event.y
            for coords, (raid_type, disk, segment) in self.block_coords.items():
                if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                    self.show_detail_window(raid_type, disk, segment)
                    break

        def show_detail_window(self, raid_type, disk, segment):
            detail_window = tk.Toplevel(self.parent.master)
            detail_window.title(f"Details for {segment}")
            detail_window.geometry("600x400")
            detail_window.configure(bg=self.theme["bg"])
            text = tk.Text(detail_window, height=20, width=70, font=("Courier", 12), bg=self.theme["bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"])
            text.pack(pady=10, padx=10)
            file_path = RAID_FILES[disk - 1]
            try:
                with open(file_path, "r") as f:
                    file_data = f.read()
            except FileNotFoundError:
                text.insert(tk.END, f"[ERROR] Could not find file: {file_path}. Ensure CTFFiles folder exists.")
                return
            segment_size = 4
            flag_bytes = "RAID1".encode().hex()
            file_num = segment.split(" ")[1]
            mirror_pair = "1 and 2" if file_num in ["1", "2"] else "3 and 4"
            text.insert(tk.END, f"Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "File Contents (first 20 words):\n")
            words = file_data.split()
            first_20_words = " ".join(words[:20]) if len(words) >= 20 else " ".join(words)
            text.insert(tk.END, f"{first_20_words}\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000:04x}\n")

        def create_raid_image(self):
            self.canvas.update_idletasks()
            width = self.canvas.winfo_width() or 800
            height = self.canvas.winfo_height() or 600
            img = Image.new("RGB", (width, height), self.theme["bg"])
            draw = ImageDraw.Draw(img)
            self.block_coords = {}
            block_w, block_h = 140, 60
            spacing_x, spacing_y = 40, 40
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
            center_x = width // 2
            top_y = 50
            for i in range(4):
                row, col = i // 2, i % 2
                x = center_x - block_w - spacing_x // 2 + col * (block_w + spacing_x)
                y = top_y + row * (block_h + spacing_y)
                label = f"File {i+1}"
                self.draw_simple_block(draw, x, y, block_w, block_h, colors[i], label, "RAID 1", i+1, label)
            draw.text((center_x - 250, top_y + 2 * (block_h + spacing_y) + 20), "The flag is the RAID configuration of these files, inspect each file and submit the correct flag: Flag{RAID0}, Flag{RAID1}, Flag{RAID5}, or Flag{RAID10}", fill=self.theme["fg"], font=ImageFont.load_default())
            self.canvas_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
            self.canvas.image = self.canvas_image

    class RansomwareChallenge:
        def __init__(self, canvas, parent, emails):
            self.canvas = canvas
            self.parent = parent
            self.theme = parent.theme
            self.emails = emails
            self.phishing_indices = [0, 2, 4, 6, 7]
            self.selected_phishing = set()
            self.email_boxes = {}
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.canvas.after(200, self.create_email_image)

        def draw_simple_email(self, draw, x, y, width, height, color, text, idx):
            draw.rounded_rectangle([x, y, x + width, y + height], radius=10, fill=color, outline=self.theme["fg"], width=2)
            text_bbox = draw.textbbox((0, 0), text, font=ImageFont.load_default())
            tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            draw.text((x + (width - tw) // 2, y + (height - th) // 2), text, fill=self.theme["button_fg"], font=ImageFont.load_default())
            self.email_boxes[(x, y, x + width, y + height)] = idx

        def on_canvas_click(self, event):
            x, y = event.x, event.y
            for coords, idx in self.email_boxes.items():
                if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                    self.show_email_detail(idx, self.emails[idx][1])
                    break

        def show_email_detail(self, idx, content):
            if idx in self.selected_phishing:
                self.selected_phishing.remove(idx)
            else:
                self.selected_phishing.add(idx)
            detail_window = tk.Toplevel(self.parent.master)
            detail_window.title(f"Email {idx + 1} Details")
            detail_window.geometry("600x400")
            detail_window.configure(bg=self.theme["bg"])
            text = tk.Text(detail_window, height=20, width=70, font=("Courier", 12), bg=self.theme["bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"])
            text.pack(pady=10, padx=10)
            text.insert(tk.END, f"Email {idx + 1} Content:\n")
            text.insert(tk.END, f"{content}\n")
            text.config(state='disabled')
            tk.Button(detail_window, text="Close", font=("Courier", 14), bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=detail_window.destroy).pack(pady=10)
            if self.selected_phishing == set(self.phishing_indices[:5]):
                messagebox.showinfo("Hint", "You’ve identified the key emails! The flag may relate to their order.")

        def create_email_image(self):
            self.canvas.update_idletasks()
            width = self.canvas.winfo_width() or 900
            height = self.canvas.winfo_height() or 100
            img = Image.new("RGB", (width, height), self.theme["bg"])
            draw = ImageDraw.Draw(img)
            self.email_boxes = {}
            box_width, box_height = 60, 40
            spacing_x = 10
            top_y = 20
            for i, (title, content) in enumerate(self.emails):
                x = i * (box_width + spacing_x) + 20
                self.draw_simple_email(draw, x, top_y, box_width, box_height, "#333333", f"{i+1}", i)
            self.canvas_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
            self.canvas.image = self.canvas_image

    class TerminalChallengeView:
        def __init__(self, canvas, parent, challenge_name):
            self.canvas = canvas
            self.parent = parent
            self.challenge_name = challenge_name
            self.theme = parent.theme
            self.step_count = 0
            self.frame = tk.Frame(canvas, bg=self.theme["bg"])
            self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.app = parent
            self.canvas_width = canvas.winfo_width() or 800
            self.canvas_height = canvas.winfo_height() or 800
            self.buttons = []
            self.image_options = ["stegopicmsg.png", "stegopicmsg2.png", "stegopicmsg3.png", "stegopicmsg4.png", "stegopicmsg5.png"]
            self.selected_image = tk.StringVar(value=self.image_options[0])

            self.preloaded_files = {
                "keyword_search": readfile(KEYWORD_SEARCH, is_binary=False) or "",
                "file_list": readfile(FILE_LIST_FILE, is_binary=False) or "",
                "timeline": readfile(TIMELINE_FILE, is_binary=False) or "",
                "export_evidence": readfile(EXPORT_EVIDENCE_FILE, is_binary=False) or ""
            }

            self.setup_ui()

        def setup_ui(self):
            # Handle dropdown for challenges requiring it
            if self.challenge_name in ["Metadata Forensics", "Steganography", "Malware Static Analysis"]:
                dropdown_frame = tk.Frame(self.frame, bg=self.theme["bg"])
                dropdown_frame.pack(pady=10, fill=tk.X)
                tk.Label(dropdown_frame, text="Select File:", font=('Courier', 14), bg=self.theme["bg"], fg=self.theme["fg"]).pack(side=tk.LEFT, padx=5)
                self.file_var = tk.StringVar(value=list(META_FILES.keys())[0] if self.challenge_name == "Metadata Forensics" else self.image_options[0])
                dropdown = ttk.Combobox(dropdown_frame, textvariable=self.file_var, values=list(META_FILES.keys()) if self.challenge_name == "Metadata Forensics" else self.image_options, state='readonly', font=('Courier', 12), width=30, style='Custom.TCombobox')
                dropdown.pack(side=tk.LEFT, padx=5)
                dropdown.bind('<<ComboboxSelected>>', self.on_file_select)
                self.instruction_label = tk.Label(self.frame, text='', fg=self.theme["fg"], bg=self.theme["bg"], font=('Courier', 14), wraplength=1000, justify='center')
                self.instruction_label.pack(pady=5)

            # Button frame with dropdown on the same line if applicable
            button_frame = tk.Frame(self.frame, bg=self.theme["bg"])
            button_frame.pack(fill=tk.X, pady=(0, 10))
            if self.challenge_name == "Metadata Forensics":
                self.btn_extract_metadata = tk.Button(button_frame, text="🔍 Extract Metadata", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.extract_metadata)
                self.btn_extract_metadata.grid(row=0, column=0, padx=5, pady=5)
                self.buttons.append(self.btn_extract_metadata)
            elif self.challenge_name == "Steganography":
                self.btn1_cover_capacity = tk.Button(button_frame, text="📏 Check Capacity", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.check_cover_capacity)
                self.btn1_cover_capacity.grid(row=0, column=0, padx=5, pady=5)
                self.btn1_cover_extract = tk.Button(button_frame, text="🔍 Extract Data", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.extract_cover_data)
                self.btn1_cover_extract.grid(row=0, column=1, padx=5, pady=5)
                self.buttons.extend([self.btn1_cover_capacity, self.btn1_cover_extract])
            elif self.challenge_name == "Password Cracking":
                self.btn_zip_crack = tk.Button(button_frame, text="💾 Crack ZIP", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.zip_crack, state='normal')
                self.btn_zip_crack.grid(row=0, column=0, padx=5, pady=5)
                self.btn_display_hash = tk.Button(button_frame, text="📜 Display Hash", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.display_hash, state='disabled')
                self.btn_display_hash.grid(row=0, column=1, padx=5, pady=5)
                self.btn_crack_hash = tk.Button(button_frame, text="🔓 Crack MD5 Hash", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.crack_hash, state='disabled')
                self.btn_crack_hash.grid(row=0, column=2, padx=5, pady=5)
                self.btn_show_cracked = tk.Button(button_frame, text="📋 Show Cracked", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.show_cracked, state='disabled')
                self.btn_show_cracked.grid(row=0, column=3, padx=5, pady=5)
                self.buttons.extend([self.btn_zip_crack, self.btn_display_hash, self.btn_crack_hash, self.btn_show_cracked])
            elif self.challenge_name == "Malware Static Analysis":
                self.btn_strings = tk.Button(button_frame, text="🔍 Extract Strings", bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, command=self.extract_strings)
                self.btn_strings.grid(row=0, column=0, padx=5, pady=5)
                self.buttons.append(self.btn_strings)
            elif self.challenge_name in ["Memory Forensics", "Network Forensics", "Autopsy"]:
                commands = self.parent.get_challenge_commands(self.challenge_name)
                for idx, command in enumerate(commands):
                    btn_text = self.get_button_text(command, idx)
                    btn = tk.Button(button_frame, text=btn_text, bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, 
                                    command=lambda c=command: self.handle_tool_command(self.challenge_name, c))
                    btn.grid(row=0, column=idx, padx=5, pady=5)
                    self.buttons.append(btn)

            # Terminal frame with standardized size and stretching
            terminal_frame = tk.Frame(self.frame, bg=self.theme["bg"])
            terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            self.terminal_output = tk.Text(terminal_frame, bg=self.theme["terminal_bg"], fg=self.theme["terminal_fg"], insertbackground=self.theme["fg"], 
                                        padx=5, font=('Courier', 12), wrap='word', height=14)
            self.terminal_output.pack(side=tk.LEFT, fill=tk.X, expand=True)
            scrollbar = tk.Scrollbar(terminal_frame, command=self.terminal_output.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.terminal_output.config(yscrollcommand=scrollbar.set, state='disabled')
            tk.Button(self.frame, text='🗑️ Clear Terminal', bg=self.theme["button_bg"], fg=self.theme["button_fg"], font=('Courier', 10), width=20, 
                    command=self.clear_terminal).pack(pady=(0, 10))

            for button in self.buttons:
                button.config(state='normal')

            if self.challenge_name in ["Metadata Forensics", "Steganography", "Malware Static Analysis"]:
                self.display_instructions()

        def handle_tool_command(self, challenge_name, command):
            if self.terminal_output and self.terminal_output.winfo_exists():
                if challenge_name == "Autopsy":
                    self.handle_autopsy_command(command)
                    return
                elif challenge_name == "Metadata Forensics" and "{selected_file}" in command:
                    file_path = META_FILES[self.file_var.get()]
                    command = command.replace("{selected_file}", f'"{file_path}"')
                elif challenge_name == "Malware Static Analysis" and "{malware_file}" in command:
                    file_path = DEMO_FILES_DIR / self.file_var.get()
                    command = command.replace("{malware_file}", f'"{file_path}"')
                self.parent.run_command(command, lambda stdout, stderr: (
                    self.append_terminal_text(self.terminal_output, f"$ {command}"),
                    self.append_terminal_text(self.terminal_output, stdout if stdout else '[OUTPUT] No output.'),
                    self.append_terminal_text(self.terminal_output, stderr if stderr else ''),
                    self.append_terminal_text(self.terminal_output, '-' * 50)
                ), self.terminal_output)

        def get_button_text(self, command, idx):
            if "volatility" in command:
                if "pslist" in command: return "📋 Run pslist"
                elif "malfind" in command and "--dump" not in command: return "🔍 Run malfind"
                elif "pstree" in command: return "🌳 Run pstree"
                elif "netscan" in command: return "🌐 Run netscan"
                elif "dlllist" in command: return "📚 Run dlllist"
                elif "--dump" in command: return "💾 Dump Memory"
            elif "tshark" in command:
                if "-e frame.number" in command: return "📋 List Packets"
                elif "-e ip.src -e ip.dst | sort" in command: return "🌐 Analyze IPs"
                elif "-e tcp.srcport" in command or "-e udp.srcport" in command: return "🔌 Check Ports & Protocols"
                elif "-e tcp.flags" in command: return "📏 Analyze TCP Flags & Lengths"
                elif '-Y "http" -x' in command: return "Analyze Packet Content"
            elif "curl" in command: return "🌍 Geolocation"
            elif "autopsy" in command:
                if "--keyword-search" in command: return "🔍 Keyword Search"
                elif "--file-list" in command: return "📑 File List"
                elif "--timeline" in command: return "⏳ Timeline"
                elif "--export-evidence" in command: return "💾 Export Evidence"
            return f"Run Step {idx + 1}"

        def append_terminal_text(self, text_widget, message):
            text_widget.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_text = f"[{timestamp}] {message}\n"
            text_widget.insert(tk.END, full_text)
            text_widget.see(tk.END)
            text_widget.after(10, lambda: text_widget.see(tk.END))
            text_widget.update_idletasks()
            if message.startswith('[OBSERVATION]') or message.startswith('[HINT]'):
                start_idx = text_widget.index(tk.END + "-2l")
                end_idx = text_widget.index(tk.END + "-1c")
                text_widget.tag_add("findings_tag", start_idx, end_idx)
            text_widget.config(state='disabled')

        def clear_terminal(self):
            self.terminal_output.config(state='normal')
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.config(state='disabled')
            self.step_count = 0
            for btn in self.buttons:
                btn.config(state='normal')

        def animate_instruction_decrypt(self, label, original_text, step=0):
            if not label.winfo_exists():
                return
            total_steps = 30
            if step >= total_steps:
                label.config(text=original_text)
                return
            fraction = step / total_steps
            display_text = list(original_text)
            for i in range(len(original_text)):
                if i >= int(fraction * len(original_text)):
                    if display_text[i] not in '\n ':
                        display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
            label.config(text=''.join(display_text))
            label.after(100, lambda: self.animate_instruction_decrypt(label, original_text, step + 1))

        def destroy(self):
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.frame.destroy()

        def display_instructions(self):
            text_map = {
                "Memory Forensics": "Use Volatility3 discover the flag, check the results of the commands in the terminal. Format: Flag{flag}",
                "Network Forensics": "Use Wireshark/tshark to examine 'new_sample3.pcap'. Investigate IPs, ports, protocols, and flag exfiltration.",
                "Autopsy": "Use Autopsy to analyze a disk image for evidence of a crime.",
                "Steganography": "Select an image and use Stegosuite to check capacity and extract hidden messages. The flag (Format: Flag{flag}) may be embedded.",
                "Metadata Forensics": "Select a file and use Exiftool to extract metadata. The flag (Format: Flag{META_FLAG987}) is hidden in the metadata.",
                "Malware Static Analysis": "Use Strings and PEfile to analyze a malware sample without executing it.",
                "Password Cracking": "Crack passwords from a ZIP file and MD5 hash using John the Ripper and Hashcat. The flag (Format: Flag{flag}) is the cracked password."
            }
            self.parent.animate_instruction_decrypt(self.instruction_label, text_map.get(self.challenge_name, "Run the provided commands to analyze data and discover the flag."))

        def on_file_select(self, event):
            selected_file_name = self.file_var.get()
            self.append_terminal_text(self.terminal_output, f"Selected file: {selected_file_name}")
            self.display_instructions()

        def extract_metadata(self):
            self.btn_extract_metadata.config(state='disabled')
            selected_file_name = self.file_var.get()
            file_path = META_FILES[selected_file_name]
            if not os.path.exists(file_path):
                self.append_terminal_text(self.terminal_output, f'[ERROR] File not found: {selected_file_name}')
                self.btn_extract_metadata.config(state='normal')
                return
            self.append_terminal_text(self.terminal_output, f'[STEP 1] Extracting metadata from {selected_file_name}...')
            self.append_terminal_text(self.terminal_output, f'> exiftool "{file_path}"')
            self.parent.run_command(f'exiftool "{file_path}"', lambda stdout, stderr: (
                self.append_terminal_text(self.terminal_output, stdout if stdout else '[OUTPUT] No metadata extracted.'),
                self.append_terminal_text(self.terminal_output, stderr if stderr else ''),
                self.append_terminal_text(self.terminal_output, '[OBSERVATION] Examine the metadata for unusual fields or values (e.g., Comment, Description) that might contain the flag.'),
                self.btn_extract_metadata.config(state='normal')
            ), self.terminal_output)

        def check_cover_capacity(self):
            self.btn1_cover_capacity.config(state='disabled')
            image_path = DEMO_FILES_DIR / self.file_var.get()
            self.append_terminal_text(self.terminal_output, f'[STEP 1] Checking {self.file_var.get()} capacity...')
            self.append_terminal_text(self.terminal_output, f'> stegosuite capacity "{image_path}"')
            self.parent.run_command(f'stegosuite capacity "{image_path}"', lambda stdout, stderr: (
                self.append_terminal_text(self.terminal_output, stdout if stdout else '[OUTPUT] No capacity data available.'),
                self.append_terminal_text(self.terminal_output, stderr if stderr else ''),
                self.append_terminal_text(self.terminal_output, '[OBSERVATION] Capacity indicates potential for hidden data. Higher values suggest embedded content.'),
                self.btn1_cover_capacity.config(state='normal')
            ), self.terminal_output)

        def extract_cover_data(self):
            self.btn1_cover_extract.config(state='disabled')
            image_path = DEMO_FILES_DIR / self.file_var.get()
            self.append_terminal_text(self.terminal_output, f'[STEP 2] Extracting data from {self.file_var.get()}...')
            self.append_terminal_text(self.terminal_output, f'> stegosuite extract -k "default_key" "{image_path}"')
            self.parent.run_command(f'stegosuite extract -k "default_key" "{image_path}"', lambda stdout, stderr: (
                self.append_terminal_text(self.terminal_output, stdout if stdout else '[OUTPUT] No data extracted.'),
                self.append_terminal_text(self.terminal_output, stderr if stderr else ''),
                self.append_terminal_text(self.terminal_output, '[OBSERVATION] Check the extracted data for hidden messages. Try different images or keys if needed.'),
                self.btn1_cover_extract.config(state='normal')
            ), self.terminal_output)

        def parse_cracked_passwords(self, stdout, stderr):
            output = stdout if stdout else stderr
            cracked_info = []
            for line in output.splitlines():
                if ':' in line and not line.startswith('0 password hashes') and not line.startswith('1 password hash'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        file_name, password = parts[0], parts[1]
                        cracked_info.append(f'[CRACKED] File: {file_name}, Password: {password}')
            return cracked_info

        def zip_crack(self):
            self.btn_zip_crack.config(state='disabled')
            self.append_terminal_text(self.terminal_output, '[STEP 1] Extracting hash from the suspicious ZIP file...')
            self.append_terminal_text(self.terminal_output, f'> zip2john "{self.app.ZIP_FILE_PATH}" > "{self.app.HASH_FILE_PATH}"')
            self.parent.run_command(f'zip2john "{self.app.ZIP_FILE_PATH}" > "{self.app.HASH_FILE_PATH}"', lambda stdout, stderr: (
                self.append_terminal_text(self.terminal_output, '[INFO] Hash saved to zip_hash.txt'),
                self.append_terminal_text(self.terminal_output, '[INFO] A hash is a unique string representing encrypted data, like a password.'),
                self.append_terminal_text(self.terminal_output, '[STEP 2] Cracking the password using a wordlist...'),
                self.append_terminal_text(self.terminal_output, f'> john --wordlist="{self.app.WORDLIST_PATH}" "{self.app.HASH_FILE_PATH}"'),
                self.parent.run_command(f'john --wordlist="{self.app.WORDLIST_PATH}" "{self.app.HASH_FILE_PATH}"', lambda crack_stdout, crack_stderr: (
                    self.append_terminal_text(self.terminal_output, crack_stdout if crack_stdout else crack_stderr),
                    self.append_terminal_text(self.terminal_output, f'[RESULT] Cracking complete. Use "Show Cracked" or "Crack MD5 Hash" to proceed.'),
                    self.btn_crack_hash.config(state='normal'),
                    self.btn_display_hash.config(state='normal')
                ), self.terminal_output)
            ), self.terminal_output)

        def show_cracked(self):
            self.btn_show_cracked.config(state='disabled')
            self.append_terminal_text(self.terminal_output, '[STEP 3] Displaying the cracked password(s)...')
            self.append_terminal_text(self.terminal_output, f'> john --show "{self.app.HASH_FILE_PATH}"')
            self.parent.run_command(f'john --show "{self.app.HASH_FILE_PATH}"', lambda stdout, stderr: (
                [self.append_terminal_text(self.terminal_output, info) for info in self.parse_cracked_passwords(stdout, stderr)] or
                self.append_terminal_text(self.terminal_output, '[INFO] No passwords cracked yet or hash file not found.'),
                self.append_terminal_text(self.terminal_output, '-' * 50),
            ), self.terminal_output)

        def crack_hash(self):
            self.btn_crack_hash.config(state='disabled')
            with open(self.app.MD5_HASH_FILE, 'w') as f:
                f.write('482c811da5d5b4bc6d497ffa98491e38\n')  # Example MD5 hash for "password123"
            self.append_terminal_text(self.terminal_output, '[STEP 2] Cracking the MD5 hash using a wordlist...')
            self.append_terminal_text(self.terminal_output, f'> hashcat -m 0 -a 0 "{self.app.MD5_HASH_FILE}" "{self.app.WORDLIST_PATH}" --force')
            self.parent.run_command(f'hashcat -m 0 -a 0 "{self.app.MD5_HASH_FILE}" "{self.app.WORDLIST_PATH}" --force', lambda stdout, stderr: (
                self.append_terminal_text(self.terminal_output, stdout if stdout else stderr),
                self.append_terminal_text(self.terminal_output, '[RESULT] Cracking complete. Use "Show Cracked" to view results.'),
                self.btn_show_cracked.config(state='normal')
            ), self.terminal_output)

        def display_hash(self):
            self.btn_display_hash.config(state='disabled')
            self.append_terminal_text(self.terminal_output, '[STEP 1.5] Displaying the extracted hash...')
            hash_file = self.app.HASH_FILE_PATH
            try:
                with open(hash_file, 'r') as f:
                    hash_content = f.read().strip()
                    self.append_terminal_text(self.terminal_output, f'[HASH] Content of {os.path.basename(hash_file)}: {hash_content}')
            except FileNotFoundError:
                self.append_terminal_text(self.terminal_output, f'[ERROR] Hash file {hash_file} not found.')
            except Exception as e:
                self.append_terminal_text(self.terminal_output, f'[ERROR] Failed to read hash file: {str(e)}')
            self.btn_display_hash.config(state='normal')

        def extract_strings(self):
            self.btn_strings.config(state='disabled')
            malware_path = DEMO_FILES_DIR / self.file_var.get()
            self.append_terminal_text(self.terminal_output, f'[STEP 1] Extracting strings from {self.file_var.get()}...')
            self.append_terminal_text(self.terminal_output, f'> strings "{malware_path}"')
            self.parent.run_command(f'strings "{malware_path}"', lambda stdout, stderr: (
                self.append_terminal_text(self.terminal_output, stdout if stdout else '[OUTPUT] No strings extracted.'),
                self.append_terminal_text(self.terminal_output, stderr if stderr else ''),
                self.append_terminal_text(self.terminal_output, '[HINT] Look for the numbered parts of the flag (e.g., Flag 1=, 2=, etc) and combine them.'),
                self.btn_strings.config(state='normal')
            ), self.terminal_output)

        def handle_autopsy_command(self, command):
            """
            Simulate Autopsy by showing the pre-loaded contents of the text files.
            """
            if not hasattr(self, 'terminal_output') or not self.terminal_output.winfo_exists():
                print("Error: Terminal output not available", file=sys.stderr)
                return
            self.append_terminal_text(self.terminal_output, f"$ {command}")

            # Map CLI switches to pre-loaded content
            if "--keyword-search" in command:
                self.append_terminal_text(self.terminal_output, f"[DEBUG] Using pre-loaded keyword search content")
                simulated_output = self.preloaded_files["keyword_search"]
            elif "--file-list" in command:
                self.append_terminal_text(self.terminal_output, f"[DEBUG] Using pre-loaded file list content")
                simulated_output = self.preloaded_files["file_list"]
            elif "--timeline" in command:
                self.append_terminal_text(self.terminal_output, f"[DEBUG] Using pre-loaded timeline content")
                simulated_output = self.preloaded_files["timeline"]
            elif "--export-evidence" in command:
                self.append_terminal_text(self.terminal_output, f"[DEBUG] Using pre-loaded export evidence content")
                simulated_output = self.preloaded_files["export_evidence"]
            else:
                self.append_terminal_text(self.terminal_output,
                    "[SIM] Unsupported option – use --keyword-search, --file-list, " 
                    "--timeline, or --export-evidence.")
                return

            self.append_terminal_text(self.terminal_output, simulated_output or "[OUTPUT] No output.")
            # Add a contextual hint
            hints = {
                "keyword_search": "[HINT] Notice keywords that appear unusually often.",
                "file_list": "[HINT] Look for odd filenames or extensions.",
                "timeline": "[HINT] Pay attention to time gaps or spikes.",
                "export_evidence": "[HINT] Inspect exported artefacts for hidden data."
            }
            hint_key = next((k for k, v in {"--keyword-search": "keyword_search", "--file-list": "file_list", "--timeline": "timeline", "--export-evidence": "export_evidence"}.items() if k in command), None)
            self.append_terminal_text(self.terminal_output, hints.get(hint_key.replace("--", ""), ""))
            self.append_terminal_text(self.terminal_output, '-' * 50)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CTF Demo")
    root.geometry(WINDOW_SIZE)
    app = MainApp(root, DEFAULT_THEME, None, None, None)
    root.mainloop()