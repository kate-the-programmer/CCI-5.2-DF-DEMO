import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk
from datetime import datetime
import random

# --- Configuration ---
FONT = 'Courier'
WINDOW_SIZE = '1280x800'

# Default theme (used if no theme is provided by the master demo)
DEFAULT_THEME = {
    "bg": "#2B092E",           # Dark purple background
    "fg": "#BF33C9",           # Purple for text
    "button_bg": "#4A154B",    # Darker purple for buttons
    "button_fg": "#FFFFFF",    # White button text
    "terminal_bg": "#1E1E1E",  # Dark gray terminal background
    "terminal_fg": "#BF33C9",  # Purple terminal text
    "active_fg": "#FFFFFF",    # For active states
    "disabled_fg": "#666666"   # For disabled states
}

# File paths relative to the script's directory
SCRIPT_DIR = Path(__file__).parent
WORDLIST_PATH = '/usr/share/wordlists/john.lst'
ZIP_FILE_PATH = SCRIPT_DIR / 'secret.zip'
HASH_FILE_PATH = SCRIPT_DIR / 'zip_hash.txt'
MD5_HASH_FILE = SCRIPT_DIR / 'md5_hash.txt'
IMAGE_PATH = SCRIPT_DIR / 'infographic.jpg'

# --- Utility Functions ---
def append_terminal_text(text_widget, message):
    text_widget.config(state='normal')
    timestamp = datetime.now().strftime("%H:%M:%S")
    text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    text_widget.see(tk.END)
    text_widget.after(10, lambda: text_widget.see(tk.END))
    text_widget.update_idletasks()
    text_widget.config(state='disabled')

def run_command(command, callback, text_widget, shell=True):
    """Run a command in a separate thread to avoid freezing the GUI."""
    def execute():
        try:
            result = subprocess.run(
                command,
                shell=shell,
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

# --- Helper Animation Function ---
def animate_instruction(label_widget, full_text, current_text="", index=0):
    if index < len(full_text):
        current_text += full_text[index]
        label_widget.config(text=current_text + "_")
        label_widget.after(30, lambda: animate_instruction(label_widget, full_text, current_text, index + 1))
    else:
        label_widget.config(text=full_text)

def animate_instruction_decrypt(widget, original_text, step=0):
    if not widget.winfo_exists():
        return

    total_steps = 30
    if step >= total_steps:
        widget.config(text=original_text)
        return

    fraction = step / total_steps
    display_text = list(original_text)
    for i in range(len(original_text)):
        if i < int(fraction * len(original_text)):
            continue
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')

    widget.config(text=''.join(display_text))
    widget.after(100, lambda: animate_instruction_decrypt(widget, original_text, step + 1))

def typewriter_effect_label(widget, full_text, current_text="", index=0):
    if index < len(full_text):
        current_text += full_text[index]
        widget.config(text=current_text + "_")
        widget.after(50, lambda: typewriter_effect_label(widget, full_text, current_text, index + 1))
    else:
        widget.config(text=full_text)

def typewriter_effect(text_id, canvas, full_text, current_text="", index=0):
    if index < len(full_text):
        current_text += full_text[index]
        canvas.itemconfig(text_id, text=current_text + "_")
        canvas.after(50, lambda: typewriter_effect(text_id, canvas, full_text, current_text, index + 1))
    else:
        canvas.itemconfig(text_id, text=full_text)

# --- Page Content Definitions ---
class PageContent:
    @staticmethod
    def password_basics():
        return (
            "🔑 What Are Passwords?\n"
            "Passwords are secret strings used to authenticate users and protect data. They’re your first line of defense!\n\n"
            "📏 Password Complexity\n"
            "Strong passwords are long (12+ characters), mix uppercase, lowercase, numbers, and symbols (e.g., P@ssw0rd!2025), and avoid common words.\n"
            "Weak passwords like 'password123' are easy to crack.\n\n"
            "🔒 Encryption Methods\n"
            "Passwords are often stored as hashes (encrypted strings) using algorithms like MD5, SHA-256, or bcrypt.\n"
            "Example: 'password' → SHA-256 → 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8\n\n"
            "Next, let’s explore how attackers try to crack these passwords!"
        )

    @staticmethod
    def password_cracking():
        return (
            "💻 Password Cracking Overview\n"
            "Password cracking is the process of recovering passwords from their hashed form, often to test security or recover lost access.\n\n"
            "🛠️ Common Techniques\n"
            "- Brute Force: Trying all possible combinations (e.g., aaa, aab, aac...).\n"
            "- Dictionary Attack: Using a wordlist of common passwords (e.g., 'password123').\n"
            "- Rainbow Tables: Precomputed tables mapping hashes to passwords.\n\n"
            "⚖️ Ethical Use\n"
            "Ethical hackers use cracking to identify weak passwords and improve security. Unauthorized cracking is illegal!\n\n"
            "Next, we’ll look at tools used for cracking passwords."
        )

    @staticmethod
    def cracking_tools():
        return (
            "🔪 John the Ripper\n"
            "John the Ripper is an open-source password cracker. It uses dictionary attacks, brute force, and custom rules to crack hashes.\n"
            "It supports many hash types, including PKZIP (for ZIP files), MD5, and bcrypt.\n\n"
            "⚡ Hashcat\n"
            "Hashcat is another powerful cracking tool, optimized for speed. It leverages GPU power for faster cracking and supports hundreds of hash formats.\n"
            "It’s often used for advanced attacks like mask attacks (e.g., ?d?d?d for 3 digits).\n\n"
            "🔄 How They Work\n"
            "Both tools take a hash, apply cracking techniques (e.g., wordlist guesses), and compare results to find the original password.\n\n"
            "Let’s use John the Ripper in a real scenario next!"
        )

    @staticmethod
    def john_demo():
        return (
            "🕵️‍♂️ Scenario: Investigate a Suspicious ZIP File\n"
            "You’ve received a suspicious ZIP file named 'secret.zip'. It’s password-protected, and you need to investigate its contents.\n"
            "Click 'Check John Help' to begin, then 'Extract Hash' to get the ZIP hash, 'Reveal Password' to crack it, and 'Next Demo' to proceed."
        )

    @staticmethod
    def hashcat_demo():
        return (
            "🕵️‍♂️ Scenario: Crack a Leaked MD5 Password Hash\n"
            "You’ve found an MD5 hash in a leaked configuration file from a compromised system.\n"
            "Click 'Check Hashcat Help' to start, then 'Crack MD5 Hash' to reveal the password, and 'Next' to see the summary."
        )

    @staticmethod
    def summary():
        return (
            "🔍 Demo Recap\n"
            "1. John the Ripper:\n"
            "   - Extracted the hash from 'secret.zip' using zip2john.\n"
            "   - Cracked the ZIP password using a wordlist.\n"
            "   - Revealed the cracked password for investigation.\n\n"
            "2. Hashcat:\n"
            "   - Cracked an MD5 hash (482c811da5d5b4bc6d497ffa98491e38).\n"
            "   - Used a wordlist to reveal the password: 'password123'.\n\n"
            "📋 Common Commands\n"
            "John the Ripper:\n"
            "- Extract ZIP hash: zip2john file.zip > hash.txt\n"
            "- Crack with wordlist: john --wordlist=wordlist.txt hash.txt\n"
            "- Show cracked passwords: john --show hash.txt\n"
            "- Brute force: john --incremental hash.txt\n\n"
            "Hashcat:\n"
            "- Crack MD5 with wordlist: hashcat -m 0 -a 0 hash.txt wordlist.txt\n"
            "- Brute force (3 digits): hashcat -m 0 -a 3 hash.txt ?d?d?d\n"
            "- Show cracked passwords: hashcat --show hash.txt\n"
            "- Use rules: hashcat -m 0 -a 0 hash.txt wordlist.txt -r rules/best64.rule\n\n"
            "🎯 Use Cases\n"
            "- Security Testing: Identify weak passwords in systems.\n"
            "- Incident Response: Recover access to locked files.\n"
            "- Educational Training: Learn password security best practices.\n"
            "- Forensic Analysis: Investigate encrypted evidence.\n\n"
            "Thank you for completing the Password Cracking Demo!"
        )

# --- Main Application ---
class MainApp:
    def __init__(self, root, theme=None, apply_theme_callback=None):
        self.root = root
        self.root.title("Password Cracking Demo")
        self.root.geometry(WINDOW_SIZE)
        self.current_screen = None
        self.theme = theme if theme else DEFAULT_THEME
        self.apply_theme_callback = apply_theme_callback
        self.last_width = 1280
        self.last_height = 720
        self.canvas_width = 1200
        self.canvas_height = 680
        self.current_step = 0  # Track current page/step
        self.steps = ["🔐 Understanding Passwords", "🔓 What is Password Cracking?", "🛠️ Password Cracking Tools", 
                      "🕵️‍♂️ John the Ripper Demo", "🕵️‍♂️ Hashcat Demo", "📝 Demo Recap & Quick Reference"]
        self.header_items = []
        self.button_items = []
        self.bg_image_id = None
        self.current_text_widget = None
        self.canvas_item_id = None
        self.bg_photo = None
        self.demo_frame = None

        # Define pages with content and mode
        self.pages = [
            {"title": "🔐 Understanding Passwords", "content": PageContent.password_basics, "mode": "info"},
            {"title": "🔓 What is Password Cracking?", "content": PageContent.password_cracking, "mode": "info"},
            {"title": "🛠️ Password Cracking Tools", "content": PageContent.cracking_tools, "mode": "info"},
            {"title": "🕵️‍♂️ John the Ripper Demo", "content": PageContent.john_demo, "mode": "demo"},
            {"title": "🕵️‍♂️ Hashcat Demo", "content": PageContent.hashcat_demo, "mode": "demo"},
            {"title": "📝 Demo Recap & Quick Reference", "content": PageContent.summary, "mode": "info"}
        ]

        self.main_frame = tk.Frame(root, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_canvas()
        self.root.bind("<Configure>", self.on_window_resize)
        self.update_step()

    def on_window_resize(self, event):
        if event.widget == self.root:
            self.root.after(100, self.update_layout)

    def update_layout(self):
        self.root.update_idletasks()
        actual_width = self.root.winfo_width()
        actual_height = self.root.winfo_height()
        
        if (hasattr(self, 'last_width') and hasattr(self, 'last_height') and
            abs(actual_width - self.last_width) < 50 and 
            abs(actual_height - self.last_height) < 50):
            return
        
        self.last_width = actual_width
        self.last_height = actual_height
        
        canvas_width = max(1200, actual_width - 40)
        canvas_height = max(800, actual_height - 40)
        
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        # Only update canvas items and frames, not background
        self.update_step()

    def create_background(self):
        # Create background only once during initialization
        width = 1200
        height = 800
        bg_image = Image.new('RGB', (width, height), self.theme["bg"])
        draw = ImageDraw.Draw(bg_image)
        
        for i in range(0, width, 20):
            for j in range(0, height, 20):
                if random.random() > 0.9:
                    char = random.choice(['0', '1', '█', '▓', '▒', '░'])
                    draw.text((i, j), char, fill=self.theme["disabled_fg"])
        
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        if not self.bg_image_id:
            self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

    def apply_theme(self, theme):
        self.theme = theme
        self.root.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])
        self.canvas.configure(bg=theme["bg"])
        
        for item in self.header_items:
            text = self.canvas.itemcget(item, "text")
            if "[PAGE" in text:
                self.canvas.itemconfig(item, fill=theme["button_bg"])
            else:
                self.canvas.itemconfig(item, fill=theme["fg"])
        
        if self.current_text_widget and self.current_text_widget.winfo_exists():
            self.current_text_widget.configure(
                bg=theme["terminal_bg"],
                fg=theme["terminal_fg"],
                insertbackground=theme["fg"]
            )
        
        self.create_navigation_buttons()
        if self.apply_theme_callback:
            self.apply_theme_callback(theme)

    def create_canvas(self):
        self.root.update_idletasks()
        window_width = max(1200, self.root.winfo_width() - 40)
        window_height = max(800, self.root.winfo_height() - 40)
        
        self.canvas = tk.Canvas(self.main_frame, 
                                width=window_width, 
                                height=window_height, 
                                bg=self.theme["bg"], 
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_width = window_width
        self.canvas_height = window_height
        
        self.create_background()

    def update_step(self):
        if self.demo_frame:
            self.demo_frame.destroy()
        for item in self.button_items:
            self.canvas.delete(item)
        self.button_items = []
        for item in self.header_items:
            self.canvas.delete(item)
        self.header_items = []
        if self.current_text_widget:
            self.canvas.delete(self.canvas_item_id)

        page = self.pages[self.current_step]
        if self.bg_image_id:
            self.canvas.tag_lower(self.bg_image_id)

        if page["mode"] == "info":
            self.create_page_header(page)
            self.current_text = page['content']()
            self.show_content_with_animation()
            self.create_navigation_buttons()
        else:  # mode == "demo"
            self.setup_demo_frame()

    def create_page_header(self, page):
        page_num_text = f"[PAGE {self.current_step + 1:02d}]"
        page_num_id = self.canvas.create_text(50, 30, 
                                              text=page_num_text, 
                                              font=('Courier New', 22, 'bold'),
                                              fill=self.theme["button_bg"],
                                              anchor="w")
        self.header_items.append(page_num_id)
        
        title_id = self.canvas.create_text(50, 60, 
                                           text="", 
                                           font=('Courier New', 26, 'bold'),
                                           fill=self.theme["fg"],
                                           anchor="w")
        self.header_items.append(title_id)
        
        self.typewriter_effect(title_id, page['title'])

    def typewriter_effect(self, text_id, full_text, current_text="", index=0):
        if index < len(full_text):
            current_text += full_text[index]
            self.canvas.itemconfig(text_id, text=current_text + "_")
            self.root.after(50, lambda: self.typewriter_effect(text_id, full_text, current_text, index + 1))
        else:
            self.canvas.itemconfig(text_id, text=full_text)

    def show_content_with_animation(self):
        self.root.update_idletasks()
        content_width = max(800, self.canvas_width - 100)
        content_height = max(400, self.canvas_height - 200)  # Adjust for header and buttons
        
        text_widget = tk.Text(self.root, 
                              wrap="word", 
                              font=('Courier New', 17),
                              bg=self.theme["terminal_bg"], 
                              fg=self.theme["terminal_fg"],
                              borderwidth=2,
                              relief="ridge",
                              spacing1=4, 
                              spacing2=2, 
                              spacing3=4,
                              insertbackground=self.theme["fg"])
        
        text_widget.insert("1.0", self.current_text)
        text_widget.config(state="disabled")
        
        self.current_text_widget = text_widget
        self.canvas_item_id = self.canvas.create_window(50, 100, 
                                                        anchor="nw", 
                                                        window=text_widget, 
                                                        width=content_width, 
                                                        height=content_height)
        
        self.decrypt_animation(text_widget, self.current_text)

    def decrypt_animation(self, widget, original_text, step=0):
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
        self.root.after(100, lambda: self.decrypt_animation(widget, original_text, step + 1))

    def create_navigation_buttons(self):
        """Create styled navigation buttons with cyber aesthetic"""
        theme = self.theme
        for item in self.button_items:
            self.canvas.delete(item)
        self.button_items = []
        self.root.update_idletasks()
        canvas_width = max(1160, self.canvas_width)
        canvas_height = max(750, self.canvas_height)
        button_y = canvas_height - 50
        center_x = canvas_width // 2
        if self.current_step > 0:
            back_btn = tk.Button(self.root,
                               text="◄◄ [BACKUP]",
                               command=self.previous_step,
                               font=('Arial', 17, 'bold'),
                               bg=theme["bg"],
                               fg=theme["disabled_fg"],
                               activebackground=theme["disabled_fg"],
                               activeforeground=theme["bg"],
                               relief="flat",
                               bd=0,
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               highlightthickness=1,
                               highlightcolor=theme["disabled_fg"],
                               highlightbackground=theme["disabled_fg"])
            back_item = self.canvas.create_window(150, button_y, window=back_btn)
            self.canvas.tag_raise(back_item)
            self.button_items.append(back_item)
            back_border = self.canvas.create_rectangle(100, button_y-20, 200, button_y+20,
                                                     outline=theme["disabled_fg"],
                                                     width=1,
                                                     fill="")
            self.button_items.append(back_border)
        if self.current_step < len(self.steps) - 1:
            next_text = "[NEXT] ►►"
            next_cmd = self.next_step
            button_color = theme["button_fg"]
            border_color = theme["button_bg"]
        else:
            next_text = "[COMPLETE]"
            next_cmd = self.complete_demo
            button_color = theme["fg"]
            border_color = theme["fg"]
        next_btn = tk.Button(self.root,
                           text=next_text,
                           command=next_cmd,
                           font=('Arial', 17, 'bold'),
                           bg=theme["bg"],
                           fg=button_color,
                           activebackground=button_color,
                           activeforeground=theme["bg"],
                           relief="flat",
                           bd=0,
                           padx=15,
                           pady=5,
                           cursor="hand2",
                           highlightthickness=1,
                           highlightcolor=border_color,
                           highlightbackground=border_color)
        next_item = self.canvas.create_window(canvas_width - 150, button_y, window=next_btn)
        self.canvas.tag_raise(next_item)
        self.button_items.append(next_item)
        next_border = self.canvas.create_rectangle(canvas_width - 200, button_y-20, canvas_width - 100, button_y+20,
                                                 outline=border_color,
                                                 width=2,
                                                 fill="")
        self.button_items.append(next_border)
        progress_text = f">>> PROGRESS: {self.current_step + 1:02d}/{len(self.steps):02d} <<<"
        progress_item = self.canvas.create_text(center_x, button_y,
                                              text=progress_text,
                                              font=('Arial', 18, 'bold'),
                                              fill=theme["fg"])
        self.button_items.append(progress_item)
        progress_width = 200
        progress_filled = int((self.current_step + 1) / len(self.steps) * progress_width)
        progress_start_x = center_x - (progress_width // 2)
        progress_end_x = center_x + (progress_width // 2)
        progress_bg = self.canvas.create_rectangle(progress_start_x, button_y + 25, progress_end_x, button_y + 30,
                                                 outline=theme["disabled_fg"],
                                                 fill=theme["bg"],
                                                 width=1)
        self.button_items.append(progress_bg)
        if progress_filled > 0:
            progress_fill = self.canvas.create_rectangle(progress_start_x, button_y + 25, 
                                                       progress_start_x + progress_filled, button_y + 30,
                                                       outline="",
                                                       fill=theme["fg"],
                                                       width=0)
            self.button_items.append(progress_fill)

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step()

    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def complete_demo(self):
        self.canvas.delete("all")
        self.create_background()
        
        self.root.update_idletasks()
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2
        
        final_text = "Demo Complete!\n\nThank you for participating."
        text_id = self.canvas.create_text(center_x, center_y,
                                          text=final_text,
                                          font=('Courier New', 20, 'bold'),
                                          fill=self.theme["fg"],
                                          justify="center",
                                          anchor="center")
        
        self.root.after(5000, self.fade_out)

    def fade_out(self):
        self.root.destroy()

    def setup_demo_frame(self):
        if self.current_step == 3:  # John the Ripper Demo
            self.demo_frame = tk.Frame(self.root, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=0, y=0)  # Place frame over the canvas
            self.demo_frame.lift()  # Ensure frame is on top of canvas

            label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], font=(FONT, 18))
            label.place(relx=0.5, y=20, anchor='n')
            typewriter_effect_label(label, '🕵️‍♂️ Scenario: Investigate a Suspicious ZIP File')


            self.current_text_widget = tk.Text(self.demo_frame, bg=self.theme["terminal_bg"], fg=self.theme["terminal_fg"], 
                                              insertbackground=self.theme["fg"], font=(FONT, 12), wrap='word', width=100, height=15)
            self.current_text_widget.place(relx=0.5, rely=0.55, anchor='center')
            self.current_text_widget.config(state='disabled')

            self.instruction_label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], 
                                             font=(FONT, 14), wraplength=800, justify='center')
            self.instruction_label.place(relx=0.5, rely=0.25, anchor='center')

            btn1 = tk.Button(self.demo_frame, text='📘 Check John Help', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                             font=(FONT, 12), width=30, command=self.basic_john)
            btn1.place(relx=0.25, rely=0.35, anchor='center')
            btn1.config(state='disabled')

            btn2 = tk.Button(self.demo_frame, text='🔍 Extract Hash', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                             font=(FONT, 12), width=30, command=self.zip_crack)
            btn2.place(relx=0.5, rely=0.35, anchor='center')
            btn2.config(state='disabled')

            btn3 = tk.Button(self.demo_frame, text='🔓 Reveal Password', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                             font=(FONT, 12), width=30, command=self.show_cracked)
            btn3.place(relx=0.75, rely=0.35, anchor='center')
            btn3.config(state='disabled')

            btn_next = tk.Button(self.demo_frame, text='▶ Next Demo: Hashcat', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 12), width=30, command=self.next_step)
            btn_next.place(relx=0.75, rely=0.85, anchor='center')
            btn_next.config(state='disabled')

            btn_clear = tk.Button(self.demo_frame, text='🗑️ Clear Terminal', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                  font=(FONT, 12), width=30, command=self.clear_terminal)
            btn_clear.place(relx=0.5, rely=0.85, anchor='center')

            self.basic_john_step = 1
            animate_instruction_decrypt(self.instruction_label,"You’ve received a suspicious ZIP file named 'secret.zip'. It’s password-protected, and you need to investigate its contents.\nLet’s use John the Ripper to crack the password. First, let’s check John’s capabilities.\nClick the 'Check John Help' button to begin.")
            btn1.config(state='normal')

        elif self.current_step == 4:  # Hashcat Demo
            self.demo_frame = tk.Frame(self.root, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=0, y=0)  # Place frame over the canvas
            self.demo_frame.lift()  # Ensure frame is on top of canvas

            label = tk.Label(self.demo_frame, text='🕵️‍♂️ Scenario: Crack a Leaked MD5 Password Hash', 
                             fg=self.theme["button_fg"], bg=self.theme["bg"], font=(FONT, 18))
            label.place(relx=0.5, y=20, anchor='n')
            typewriter_effect_label(label, '🕵️‍♂️ Scenario: Crack a Leaked MD5 Password Hash')
            self.current_text_widget = tk.Text(self.demo_frame, bg=self.theme["terminal_bg"], fg=self.theme["terminal_fg"], 
                                              insertbackground=self.theme["fg"], font=(FONT, 12), wrap='word', width=100, height=15)
            self.current_text_widget.place(relx=0.5, rely=0.55, anchor='center')
            self.current_text_widget.config(state='disabled')

            self.instruction_label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], 
                                             font=(FONT, 14), wraplength=800, justify='center')
            self.instruction_label.place(relx=0.5, rely=0.25, anchor='center')

            btn1 = tk.Button(self.demo_frame, text='📘 Check Hashcat Help', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                             font=(FONT, 12), width=30, command=self.basic_hashcat)
            btn1.place(relx=0.25, rely=0.35, anchor='center')
            btn1.config(state='disabled')

            btn2 = tk.Button(self.demo_frame, text='🔍 Crack MD5 Hash', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                             font=(FONT, 12), width=30, command=self.crack_hash)
            btn2.place(relx=0.5, rely=0.35, anchor='center')
            btn2.config(state='disabled')

            btn_next = tk.Button(self.demo_frame, text='▶ Next: Summary', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 12), width=30, command=self.next_step)
            btn_next.place(relx=0.75, rely=0.85, anchor='center')
            btn_next.config(state='disabled')

            btn_clear = tk.Button(self.demo_frame, text='🗑️ Clear Terminal', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                  font=(FONT, 12), width=30, command=self.clear_terminal)
            btn_clear.place(relx=0.5, rely=0.85, anchor='center')

            animate_instruction_decrypt(self.instruction_label,"You’ve found an MD5 hash in a leaked configuration file from a compromised system.\nLet’s use Hashcat to crack the password. First, let’s check Hashcat’s capabilities.\nClick the 'Check Hashcat Help' button to begin.")
            btn1.config(state='normal')

    def basic_john(self):
        if hasattr(self, 'basic_john_step') and self.basic_john_step == 1:
            append_terminal_text(self.current_text_widget, '[STEP 1] Checking John the Ripper capabilities...')
            append_terminal_text(self.current_text_widget, '> john --help')
            def john_help_callback(stdout, stderr):
                append_terminal_text(self.current_text_widget, stdout if stdout else stderr)
                append_terminal_text(self.current_text_widget, '[INFO] John the Ripper is ready to use!')
                self.basic_john_step = 2
                self.demo_frame.winfo_children()[4].config(state='normal')  # Enable Extract Hash
            run_command('john --help', john_help_callback, self.current_text_widget)

    def extract_cracked_password(self, output):
        """Extract the cracked password from the john command output."""
        cracked_password = None
        for line in output.splitlines():
            if '(secret.zip' in line and not line.startswith('Loaded'):
                cracked_password = line.split()[0]
                break
        return cracked_password

    def parse_cracked_passwords(self, stdout, stderr):
        """Parse the john --show output to extract cracked passwords."""
        output = stdout if stdout else stderr
        cracked_info = []
        for line in output.splitlines():
            if ':' in line and not line.startswith('0 password hashes') and not line.startswith('1 password hash'):
                parts = line.split(':')
                if len(parts) >= 2:
                    file_name = parts[0]
                    password = parts[1]
                    cracked_info.append(f'[CRACKED] File: {file_name}, Password: {password}')
        return cracked_info

    def zip_crack(self):
        append_terminal_text(self.current_text_widget, '[STEP 2] Extracting hash from the suspicious ZIP file...')
        append_terminal_text(self.current_text_widget, f'> zip2john {ZIP_FILE_PATH} > {HASH_FILE_PATH}')
        run_command(f'zip2john "{ZIP_FILE_PATH}" > "{HASH_FILE_PATH}"', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, '[INFO] Hash saved to zip_hash.txt'),
            append_terminal_text(self.current_text_widget, '[INFO] A hash is a unique string representing encrypted data, like a password.'),
            append_terminal_text(self.current_text_widget, '[HASH] Sample Password Hash:'),
            append_terminal_text(self.current_text_widget, '       File: example.zip'),
            append_terminal_text(self.current_text_widget, '       Type: $pkzip$ (ZIP file hash)'),
            append_terminal_text(self.current_text_widget, '       Data: 1*1*2*0*24*8*48*EXAMPLE_HASH*0###'),
            append_terminal_text(self.current_text_widget, '[STEP 3] Cracking the password using a wordlist...'),
            append_terminal_text(self.current_text_widget, f'> john --wordlist={WORDLIST_PATH} {HASH_FILE_PATH}'),
            run_command(f'john --wordlist="{WORDLIST_PATH}" "{HASH_FILE_PATH}"', lambda crack_stdout, crack_stderr: (
                append_terminal_text(self.current_text_widget, crack_stdout if crack_stdout else crack_stderr),
                append_terminal_text(self.current_text_widget, f'[RESULT] Cracked Password: {self.extract_cracked_password(crack_stdout if crack_stdout else "") or "Not found in wordlist"}'),
                self.demo_frame.winfo_children()[5].config(state='normal')  # Enable Reveal Password
            ), self.current_text_widget)
        ), self.current_text_widget)
        self.demo_frame.winfo_children()[4].config(state='disabled')

    def show_cracked(self):
        append_terminal_text(self.current_text_widget, '[STEP 4] Displaying the cracked password...')
        append_terminal_text(self.current_text_widget, f'> john --show {HASH_FILE_PATH}')
        run_command(f'john --show "{HASH_FILE_PATH}"', lambda stdout, stderr: (
            [append_terminal_text(self.current_text_widget, info) for info in self.parse_cracked_passwords(stdout, stderr)] or 
            append_terminal_text(self.current_text_widget, '[INFO] No passwords cracked yet or hash file not found.'),
            append_terminal_text(self.current_text_widget, '-' * 50),
            self.demo_frame.winfo_children()[6].config(state='normal')  # Enable Next Demo
        ), self.current_text_widget)
        self.demo_frame.winfo_children()[5].config(state='disabled')

    def clear_terminal(self):
        self.current_text_widget.config(state='normal')
        self.current_text_widget.delete(1.0, tk.END)
        self.current_text_widget.config(state='disabled')
        self.setup_demo_frame()  # Reset to current demo state

    def basic_hashcat(self):
        append_terminal_text(self.current_text_widget, '[STEP 1] Checking Hashcat capabilities...')
        append_terminal_text(self.current_text_widget, '> hashcat --help')
        run_command('hashcat --help', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[INFO] Hashcat is ready to use!'),
            append_terminal_text(self.current_text_widget, '[INFO] Found MD5 hash: 482c811da5d5b4bc6d497ffa98491e38 (password: password123)'),
            self.demo_frame.winfo_children()[4].config(state='normal')  # Enable Crack MD5 Hash
        ), self.current_text_widget)
        self.demo_frame.winfo_children()[3].config(state='disabled')

    def crack_hash(self):
        with open(MD5_HASH_FILE, 'w') as f:
            f.write('482c811da5d5b4bc6d497ffa98491e38\n')
        append_terminal_text(self.current_text_widget, '[STEP 2] Cracking the MD5 hash using a wordlist...')
        append_terminal_text(self.current_text_widget, f'> hashcat -m 0 -a 0 {MD5_HASH_FILE} {WORDLIST_PATH} --force')
        run_command(f'hashcat -m 0 -a 0 "{MD5_HASH_FILE}" "{WORDLIST_PATH}" --force', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[RESULT] Cracked Password: password123'),
            self.demo_frame.winfo_children()[5].config(state='normal')  # Enable Next
        ), self.current_text_widget)
        self.demo_frame.winfo_children()[4].config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()