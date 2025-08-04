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

# Default theme
DEFAULT_THEME = {
    "bg": "#1a1a1a",
    "fg": "#ff0000",
    "button_bg": "#ff0000",
    "button_fg": "#000000",
    "terminal_bg": "#1a1a1a",
    "terminal_fg": "#ff0000",
    "active_fg": "#FFFFFF",
    "disabled_fg": "#666666"
}

# File paths
DEMO_FILES_DIR = "Ransomware/demo_files"
SAMPLE_FILE = os.path.join(DEMO_FILES_DIR, "sample.txt")
BACKUP_FILE = os.path.join(DEMO_FILES_DIR, "sample_backup.txt")
BUSINESS_FILES = [
    os.path.join(DEMO_FILES_DIR, "business_letter.txt"),
    os.path.join(DEMO_FILES_DIR, "invoice.txt")
]

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
    try:
        print(f"Initializing sample files in {DEMO_FILES_DIR}...")
        os.makedirs(DEMO_FILES_DIR, exist_ok=True)
        if not os.path.exists(SAMPLE_FILE):
            writefile("This is a sample file to demonstrate a file configuration with 64 bytes of data.", SAMPLE_FILE)
            print(f"Created {SAMPLE_FILE}")
        if not os.path.exists(BACKUP_FILE):
            writefile(readfile(SAMPLE_FILE), BACKUP_FILE)
            print(f"Created {BACKUP_FILE}")
        for file in BUSINESS_FILES:
            backup_file = file + ".bak"
            if not os.path.exists(file):
                if os.path.basename(file) == "business_letter.txt":
                    writefile("Dear Client,\nWe are pleased to offer you a contract worth $500,000 for Q3 2025.\nRegards,\nBusiness Inc.", file)
                elif os.path.basename(file) == "invoice.txt":
                    writefile("Invoice #1234\n50 units of Product X at $200 each\nTotal: $10,000\nDue: 04/01/2025", file)
                print(f"Created {file}")
            if not os.path.exists(backup_file):
                writefile(readfile(file), backup_file)
                print(f"Created backup {backup_file}")
        with open(SAMPLE_FILE, "rb") as f:
            print(f"File size: {len(f.read())} bytes")
        return True, None
    except Exception as e:
        error_msg = f"Error creating sample files: {str(e)}"
        print(error_msg)
        return False, error_msg

def verify_required_images():
    missing_images = []
    for image_file in ["cyber_bg.png", "CyberSmokey.jpg"]:
        full_path = os.path.join("Assets", image_file)
        if not os.path.exists(full_path):
            missing_images.append(full_path)
    if missing_images:
        print(f"Note: Missing image files: {', '.join(missing_images)}. Will use fallback backgrounds.")
    return True, None

def initialize_ransomware_demo(parent_window, theme=None):
    try:
        print("Verifying required image files...")
        images_ok, image_error = verify_required_images()
        if not images_ok:
            return False, image_error
        print("Initializing sample files...")
        files_ok, file_error = initialize_sample_files()
        if not files_ok:
            return False, file_error
        print("Creating RansomwareDemo instance...")
        ransom_demo = RansomwareDemo(parent_window, theme=theme)
        return True, ransom_demo
    except Exception as e:
        tb = traceback.format_exc()
        error_msg = f"Error initializing ransomware demo: {str(e)}\n\nTraceback:\n{tb}"
        print(error_msg)
        return False, image_error

class RansomwareDemo(tk.Frame):
    def __init__(self, parent, theme=None):
        super().__init__(parent)
        self.root = parent
        self.theme = theme if theme else DEFAULT_THEME
        self.TITLE_FONT_SIZE = 20
        self.TEXT_FONT_SIZE = 17
        self.BUTTON_FONT_SIZE = 14
        self.SMALL_FONT_SIZE = 12
        print(f"Font sizes initialized - Title: {self.TITLE_FONT_SIZE}, Text: {self.TEXT_FONT_SIZE}, Button: {self.BUTTON_FONT_SIZE}, Small: {self.SMALL_FONT_SIZE}")
        self.page = 0
        self.aes_key = None
        self.encrypted_files = {}
        self.current_text_widget = None
        self.current_text = ""
        self.canvas_item_id = None
        self.button_items = []
        self.icon_items = []  # Separate list for icon items
        self.header_items = []
        self.bg_image_id = None
        self.demo_ended = False
        self.canvas_width = 1200
        self.canvas_height = 800
        self.completed_steps = set()
        self.icon_images = []  # To retain image references
        self.steps = [
            {'title': 'Ransomware Attack', 'description': 'Introduction to Ransomware', 'content': self.get_ransom_text},
            {'title': 'Ransomware Attacks', 'description': 'Famous Attacks and Vectors', 'content': self.get_ransom_attacks_text},
            {'title': 'Ransomware Mitigation', 'description': 'Protection Strategies', 'content': self.get_ransom_mitigation_text},
            {'title': 'Detection Techniques', 'description': 'Identifying Ransomware', 'content': self.get_ransom_detection_techniques_text},
            {'title': 'Response Strategies', 'description': 'Handling an Attack', 'content': self.get_ransom_response_strategies_text},
            {'title': 'Critical Infrastructure', 'description': 'Impact on Essential Services', 'content': self.get_ransom_critical_infrastructure_text},
            {'title': 'Phishing Example', 'description': 'Demo Email', 'content': self.get_demo_email_text},
            {'title': 'Encryption Demo', 'description': 'Files Encrypted', 'content': self.get_ransomware_encrypted_text},
            {'title': 'Backup Recovery', 'description': 'Restoring Files', 'content': self.get_ransom_backup_recovery_text},
            {'title': 'Sources', 'description': 'References and Resources', 'content': self.get_sources_text}
        ]
        self.current_step = 0
        self.pack(fill=tk.BOTH, expand=True)
        self.main_frame = tk.Frame(self, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.init_gui()
        self.init_background_images()

    def init_gui(self):
        self.init_file_icons()
        self.create_canvas()
        self.root.bind('<Configure>', self.on_window_resize)
        self.root.focus_force()
        self.load_step()

    def init_file_icons(self):
        try:
            file_icon_path = os.path.join("Assets", "file_icon.png")
            if not os.path.exists(file_icon_path):
                print(f"File icon not found at {file_icon_path}, creating fallback...")
                file_icon = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
                draw = ImageDraw.Draw(file_icon)
                draw.rectangle([5, 5, 45, 45], outline="black", fill="white")
                draw.text((10, 20), "TXT", fill="black")
            else:
                file_icon = Image.open(file_icon_path).resize((50, 50), Image.Resampling.LANCZOS)
            self.file_icon_tk = ImageTk.PhotoImage(file_icon)
            self.icon_images.append(self.file_icon_tk)  # Retain reference
            print("File icon initialized successfully")
        except Exception as e:
            print(f"Error creating file icon: {str(e)}")
            file_icon = Image.new("RGBA", (50, 50), (200, 200, 200, 255))
            draw = ImageDraw.Draw(file_icon)
            draw.rectangle([5, 5, 45, 45], outline="black", fill="gray")
            draw.text((10, 20), "FILE", fill="black")
            self.file_icon_tk = ImageTk.PhotoImage(file_icon)
            self.icon_images.append(self.file_icon_tk)  # Retain reference

    def init_background_images(self):
        try:
            print("Loading final background image: CyberSmokey.jpg")
            final_image_path = os.path.join("Assets", "CyberSmokey.jpg")
            if not os.path.exists(final_image_path):
                print(f"CyberSmokey.jpg not found at {final_image_path}, using fallback...")
                self.final_image = Image.new('RGB', (1200, 800), self.theme["bg"])
            else:
                self.final_image = Image.open(final_image_path)
            self.final_photo = None
            self.resize_background_images(self.canvas_width, self.canvas_height)
            print("Successfully loaded CyberSmokey.jpg")
        except Exception as e:
            print(f"Error loading final image: {str(e)}")
            self.final_image = Image.new('RGB', (1200, 800), self.theme["bg"])

    def resize_background_images(self, width, height):
        """Resize background images to match the canvas size"""
        try:
            if hasattr(self, 'final_image'):
                resized_final = self.final_image.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                self.final_photo = ImageTk.PhotoImage(resized_final)
        except Exception as e:
            print(f"Error resizing background images: {e}")

    def on_window_resize(self, event):
        """Handle window resize events to update background"""
        if event.widget == self.root:
            self.root.after(100, self.update_background_and_canvas)

    def update_background_and_canvas(self):
        """Update background and canvas size when window is resized"""
        try:
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
            self.create_background(canvas_width, canvas_height)
            self.resize_background_images(canvas_width, canvas_height)
            self.load_step()
        except Exception as e:
            print(f"Error updating background: {e}")

    def create_background(self, width=None, height=None):
        """Create cyber-themed background with specified dimensions"""
        try:
            theme = self.theme
            if width is None or height is None:
                self.root.update_idletasks()
                width = max(1200, self.canvas.winfo_width())
                height = max(800, self.canvas.winfo_height())
            bg_width = max(width, 1200)
            bg_height = max(height, 800)
            bg_image = Image.new('RGB', (bg_width, bg_height), theme["bg"])
            draw = ImageDraw.Draw(bg_image)
            for i in range(0, bg_width, 20):
                for j in range(0, bg_height, 20):
                    if random.random() > 0.9:
                        char = random.choice(['0', '1', '█', '▓', '▒', '░'])
                        draw.text((i, j), char, fill=theme["disabled_fg"])
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)
            self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        except Exception as e:
            print(f"Error creating background: {e}")
            self.bg_photo = None

    def apply_theme(self, theme):
        """Apply the provided theme to all UI elements"""
        self.theme = theme
        self.root.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])
        self.canvas.configure(bg=theme["bg"])
        self.create_background()
        for item in self.header_items:
            text = self.canvas.itemcget(item, "text")
            if "[STEP" in text:
                self.canvas.itemconfig(item, fill=theme["button_bg"])
            elif text == self.steps[self.current_step]['description']:
                self.canvas.itemconfig(item, fill=theme["active_fg"])
            else:
                self.canvas.itemconfig(item, fill=theme["fg"])
        if self.current_text_widget and self.current_text_widget.winfo_exists():
            self.current_text_widget.configure(
                bg=theme["terminal_bg"],
                fg=theme["terminal_fg"],
                insertbackground=theme["fg"]
            )
        self.create_navigation_buttons()
        for item_id in self.canvas.find_all():
            widget = self.canvas.itemcget(item_id, "window")
            if widget:
                widget_instance = self.canvas.nametowidget(widget)
                self._update_widget_theme(widget_instance, theme)

    def _update_widget_theme(self, widget, theme):
        """Recursively update the theme for a widget and its children"""
        if isinstance(widget, tk.Text):
            widget.configure(bg=theme["terminal_bg"], fg=theme["terminal_fg"], insertbackground=theme["fg"])
        elif isinstance(widget, tk.Button):
            if widget.cget("text").startswith("https://"):
                widget.configure(bg=theme["bg"], fg="#00b7eb")
            else:
                widget.configure(bg=theme["terminal_bg"], fg=theme["button_fg"], activebackground=theme["button_fg"], activeforeground=theme["terminal_bg"], highlightcolor=theme["disabled_fg"], highlightbackground=theme["disabled_fg"])
        elif isinstance(widget, tk.Label):
            if widget.cget("image"):
                widget.configure(bg="#d3d3d3", fg="black")  # Light gray background for visibility
        for child in widget.winfo_children():
            self._update_widget_theme(child, theme)

    def create_canvas(self):
        """Create main canvas for content"""
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
        self.create_background(window_width, window_height)

    def load_step(self):
        """Load current step content"""
        if self.demo_ended:
            print("Demo has ended, stopping step load.")
            return
        # Delete all existing button, header, and icon items
        for item in self.button_items:
            self.canvas.delete(item)
        self.button_items = []
        for item in self.header_items:
            self.canvas.delete(item)
        self.header_items = []
        for item in self.icon_items:
            self.canvas.delete(item)
        self.icon_items = []  # Clear the icon_items list
        if self.current_text_widget:
            self.canvas.delete(self.canvas_item_id)
        step = self.steps[self.current_step]
        if self.bg_image_id:
            self.canvas.tag_lower(self.bg_image_id)
        self.create_step_header(step)
        self.current_text = step['content']()
        self.show_content_with_animation()
        self.create_navigation_buttons()
        if self.current_step in [7, 8]:  # Ensure icons are raised after load
            self.canvas.tag_raise("icon_labels")
            print(f"Icon labels raised for step {self.current_step}")

    def create_step_header(self, step):
        """Create animated step header"""
        theme = self.theme
        step_num_text = f"[STEP {self.current_step + 1:02d}]"
        step_num_id = self.canvas.create_text(50, 30, 
                                            text=step_num_text, 
                                            font=('Courier New', 22, 'bold'),
                                            fill=theme["button_bg"],
                                            anchor="w")
        self.header_items.append(step_num_id)
        title_id = self.canvas.create_text(50, 60, 
                                         text="", 
                                         font=('Courier New', 26, 'bold'),
                                         fill=theme["fg"],
                                         anchor="w")
        self.header_items.append(title_id)
        desc_id = self.canvas.create_text(50, 90, 
                                        text=step['description'], 
                                        font=('Courier New', 18),
                                        fill=theme["active_fg"],
                                        anchor="w")
        self.header_items.append(desc_id)
        self.typewriter_effect(title_id, step['title'])

    def typewriter_effect(self, text_id, full_text, current_text="", index=0):
        """Animate text appearing character by character"""
        if index < len(full_text):
            current_text += full_text[index]
            self.canvas.itemconfig(text_id, text=current_text + "_")
            self.root.after(50, lambda: self.typewriter_effect(text_id, full_text, current_text, index + 1))
        else:
            self.canvas.itemconfig(text_id, text=full_text)

    def show_content_with_animation(self):
        """Show content with matrix-style decryption animation"""
        theme = self.theme
        content_width = max(800, self.canvas_width - 100)
        content_height = 400 if self.current_step in [6, 7, 8] else max(400, self.canvas_height - 250)  # Increased to 400 for step 6
        text_widget = tk.Text(self.root, 
                            wrap="word", 
                            font=('Courier New', 17),
                            bg=theme["terminal_bg"], 
                            fg=theme["terminal_fg"],
                            relief="ridge",
                            spacing1=4, 
                            spacing2=2, 
                            spacing3=4,
                            insertbackground=theme["fg"])
        text_widget.insert("1.0", self.current_text)
        self.current_text_widget = text_widget
        self.canvas_item_id = self.canvas.create_window(50, 130, 
                                                    anchor="nw", 
                                                    window=text_widget, 
                                                    width=content_width, 
                                                    height=content_height)
        self.canvas.tag_raise(self.canvas_item_id)
        print(f"Text widget created at x=50, y=130, width={content_width}, height={content_height}, canvas_height={self.canvas_height}")
        self.decrypt_animation(text_widget, self.current_text, callback=self.show_demo_email_buttons if self.current_step == 6 else None)
        if self.current_step in [7, 8]:  # Only call for steps 7 and 8
            self.show_ransomware_encrypted_buttons() if self.current_step == 7 else self.show_ransomware_backup_recovery_buttons()
        text_widget.config(state="disabled")  # Disable after animation

    def decrypt_animation(self, widget, original_text, step=0, callback=None):
        """Animate text decryption (like in ransomware demo)"""
        try:
            if not widget.winfo_exists():
                if callback: callback()
                return
            total_steps = 30
            if step >= total_steps:
                widget.config(state="normal")
                widget.delete("1.0", tk.END)
                widget.insert("1.0", original_text)
                widget.config(state="disabled")
                if callback: callback()
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
            self.root.after(100, lambda: self.decrypt_animation(widget, original_text, step + 1, callback))
        except Exception as e:
            print(f"Animation error: {e}")

    def decrypt_animation(self, widget, original_text, step=0, callback=None):
        """Animate text decryption (like in ransomware demo)"""
        try:
            if not widget.winfo_exists():
                if callback: callback()
                return
            total_steps = 30
            if step >= total_steps:
                widget.config(state="normal")
                widget.delete("1.0", tk.END)
                widget.insert("1.0", original_text)
                widget.config(state="disabled")
                if callback: callback()
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
            self.root.after(100, lambda: self.decrypt_animation(widget, original_text, step + 1, callback))
        except Exception as e:
            print(f"Animation error: {e}")

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
        """Navigate to next step with animation"""
        if self.demo_ended:
            print("Demo has ended, no further navigation allowed.")
            return
        if self.current_text_widget:
            self.encrypt_and_transition()
        else:
            self.transition_to_next()

    def encrypt_and_transition(self):
        """Animate encryption before transitioning"""
        self.scramble_animation(self.current_text_widget, self.current_text, 0, self.transition_to_next)

    def scramble_animation(self, widget, original_text, step, callback):
        """Animate text scrambling"""
        try:
            if not widget.winfo_exists():
                callback()
                return
            total_steps = 20
            if step >= total_steps:
                callback()
                return
            scrambled = list(original_text)
            for i in range(min(step * 3, len(original_text))):
                if scrambled[i] not in '\n ':
                    scrambled[i] = random.choice('█▓▒░01!@#$%^&*')
            widget.configure(state="normal")
            widget.delete("1.0", tk.END)
            widget.insert("1.0", ''.join(scrambled))
            widget.configure(state="disabled")
            self.root.after(50, lambda: self.scramble_animation(widget, original_text, step + 1, callback))
        except Exception as e:
            print(f"Scramble error: {e}")
            callback()

    def transition_to_next(self):
        """Move to next step"""
        self.completed_steps.add(self.current_step)
        self.current_step += 1
        if self.current_step == 7:  # Encryption demo page
            self.set_encrypted_files()
        if self.current_step < len(self.steps):
            self.load_step()
        else:
            self.complete_demo()

    def previous_step(self):
        """Navigate to previous step"""
        if self.demo_ended:
            print("Demo has ended, no further navigation allowed.")
            return
        if self.current_step > 0:
            self.current_step -= 1
            self.load_step()

    def complete_demo(self):
        """Complete the demo with final animation"""
        self.demo_ended = True
        self.canvas.delete("all")
        if hasattr(self, 'final_photo') and self.final_photo:
            self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.final_photo)
        else:
            self.create_background()
        self.root.update_idletasks()
        canvas_width = max(1160, self.canvas_width)
        canvas_height = max(760, self.canvas_height)
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        self.text_id = self.canvas.create_text(center_x, center_y, 
                                              text="DEMO COMPLETED",
                                              font=('Courier New', 30, 'bold'),
                                              fill=self.theme["fg"])
        self.root.after(5000, self.fade_out_final)

    def fade_out_final(self, alpha=1.0, step=0.05):
        """Fade out the final screen"""
        if alpha <= 0:
            self.canvas.delete("all")
            self.root.destroy()
            return
        red_value = int(255 * alpha)
        color = f"#{red_value:02x}0000"
        self.canvas.itemconfigure(self.text_id, fill=color)
        self.root.after(50, lambda: self.fade_out_final(alpha-step))

    def writeAESKey(self, bits=128):
        key = get_random_bytes(bits//8)
        key_path = os.path.join(DEMO_FILES_DIR, "aes128_key.bin")
        writefile(key, key_path, is_binary=True)
        print(f"AES key written to {key_path}")
        return key

    def encryptAES(self, message, key):
        cipher = AES.new(key, AES.MODE_CBC)
        initialVector = cipher.iv
        message_bytes = message.encode('utf-8') if isinstance(message, str) else message
        ciphertext = cipher.encrypt(pad(message_bytes, AES.block_size))
        return b64encode(initialVector + ciphertext)

    def decryptAES(self, ciphertext, key):
        cipherData = b64decode(ciphertext)
        initialVector = cipherData[:AES.block_size]
        ciphertext = cipherData[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CBC, iv=initialVector)
        message = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return message.decode('utf-8')

    def inspect_encrypted_file(self, file):
        content = self.encrypted_files.get(file, b"No encryption performed yet.").decode('utf-8')[:100] + "..." if self.encrypted_files.get(file) else "No encryption yet."
        messagebox.showinfo(f"Encrypted {os.path.basename(file)}", f"Contents of {os.path.basename(file)}:\n\n{content}", parent=self.root)

    def inspect_restored_file(self, file):
        content = readfile(file)
        messagebox.showinfo(f"Restored {os.path.basename(file)}", f"Contents of {os.path.basename(file)}:\n\n{content}", parent=self.root)

    def set_encrypted_files(self):
        self.encrypted_files = {}
        try:
            for file in BUSINESS_FILES:
                try:
                    if not os.path.exists(file):
                        raise FileNotFoundError(f"File {file} not found")
                    content = readfile(file)
                    self.encrypted_files[file] = self.encryptAES(content, self.aes_key)
                    with open(file, "wb") as f:
                        f.write(b64decode(self.encrypted_files[file]))
                    print(f"Encrypted {file}")
                except Exception as e:
                    print(f"Error encrypting file {file}: {str(e)}")
                    self.encrypted_files[file] = self.encryptAES(f"Encrypted content for {os.path.basename(file)}", self.aes_key)
        except Exception as e:
            print(f"Error in set_encrypted_files: {str(e)}")
            messagebox.showwarning("Encryption Error", "There was an error encrypting the files. The demo will continue with simulated encryption.", parent=self.root)

    def get_ransom_text(self):
        if self.aes_key is None:
            self.aes_key = self.writeAESKey(bits=128)
        return (
            "Ransomware Attack\n\n"
            "A ransomware attack is a type of malware that encrypts a victim's files. The attacker then demands a ransom "
            "from the victim to restore access to the data upon payment.\n\n"
            "Key Characteristics:\n"
            "- Users are shown instructions for how to pay a fee to get the decryption key.\n"
            "- Costs can range from a few hundred dollars to thousands, payable to cybercriminals in Bitcoin.\n\n"
            "Impact:\n"
            "The ransomware attack is a growing threat to individuals and organizations of all sizes."
        )

    def get_ransom_attacks_text(self):
        return (
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

    def get_ransom_mitigation_text(self):
        return (
            "Ransomware Mitigation\n\n"
            "To protect against ransomware attacks, consider the following mitigation strategies:\n"
            "- Regularly back up your data and store it in a secure, offline location (e.g., external drive, cloud with versioning).\n"
            "- Keep your software up to date with the latest security patches.\n"
            "- Be cautious when opening email attachments or clicking on links from unknown sources.\n"
            "- Use strong, unique passwords for all accounts and enable two-factor authentication where possible.\n"
            "- Educate employees about the risks of ransomware and how to recognize phishing attempts.\n"
            "- Implement network segmentation and restrict user access to sensitive data.\n"
            "- Consider using security software that can detect and block ransomware attacks."
        )

    def get_ransom_detection_techniques_text(self):
        return (
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

    def get_ransom_response_strategies_text(self):
        return (
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

    def get_ransom_critical_infrastructure_text(self):
        return (
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

    def get_demo_email_text(self):
        if self.aes_key is None:
            self.aes_key = self.writeAESKey(bits=128)
        return (
            "From: NetflixCustomer5ervice@eexample.com\n"
            "To: YourEmailAddress@email.com\n"
            "Subject: Netflix Account Verification\n"
            "Dear Customer,\n\n"
            "We've detected unusual activity on your Netflix account. "
            "To ensure your account security, please click the [LINK] to verify your information.\n\n"
            "Your account will be locked if you don't verify within 24 hours.\n\n"
            "Thank you,\n"
            "The Netflix Customer Support."
        )

    def get_ransomware_encrypted_text(self):
        if not self.encrypted_files:
            self.set_encrypted_files()
        return (
            "Ransomware in Action\n\n"
            "Your files have been encrypted with a strong AES encryption algorithm.\n\n"
            "The impact of ransomware:\n"
            "- All your important files are now inaccessible\n"
            "- Without the decryption key, recovery is nearly impossible\n"
            "- Attackers typically demand payment in cryptocurrency\n"
            "- Even if you pay, there's no guarantee you'll get your files back\n\n"
            "Click on the file icons below to see what encrypted files look like:"
        )

    def get_ransom_backup_recovery_text(self):
        for file in BUSINESS_FILES:
            backup_content = readfile(file + ".bak")
            writefile(backup_content, file)
        return (
            "Recovering with Backups\n\n"
            "Backups are a key mitigation strategy against ransomware. Here's how they work:\n"
            "- Regular backups (e.g., to an offline drive or cloud with versioning) preserve your data.\n"
            "- After an attack, isolate the system, remove the ransomware, and restore from a clean backup.\n\n"
            "Demo: We encrypted 'business_letter.txt' and 'invoice.txt'. Files have now been restored. Click icons to inspect:"
        )

    def get_sources_text(self):
        return (
            "Sources and resources\n\n"
            "1. Cryptographic ransomware encryption detection: Survey -- https://www.sciencedirect.com/science/article/pii/S0167404823002596\n"
            "2. Ransomware: Recent advances, analysis, challenges and future research directions -- https://pmc.ncbi.nlm.nih.gov/articles/PMC8463105/\n"
            "3. Ransomware: Minimizing the Risks -- https://pmc.ncbi.nlm.nih.gov/articles/PMC5300711/\n"
            "4. STOPRANSOMWARE -- https://www.cisa.gov/stopransomware\n"
        )

    def show_ransomware_encrypted_buttons(self):
        text_box_top = 130
        content_height = 400  # Fixed height from show_content_with_animation
        text_box_bottom = text_box_top + content_height
        icon_y_center = text_box_bottom + 150  # Adjusted to ensure visibility
        print(f"Creating encrypted file icons at x={self.canvas_width//2-150}, x={self.canvas_width//2+150}, y={icon_y_center}, canvas_height={self.canvas_height}")
        # Debug rectangle to visualize icon position
        file1_label = tk.Label(
            self.canvas,
            text="business_letter.txt",
            image=self.file_icon_tk,
            compound="top",
            fg="black",
            bg="#d3d3d3",  # Light gray background for visibility
            font=("Arial", self.BUTTON_FONT_SIZE),
            cursor="hand2",
            width=100,  # Increased size for debugging
            height=70,  # Add border for visibility
            relief="solid"
        )
        file1_label.image = self.file_icon_tk  # Retain image reference in label
        file1_label.bind("<Button-1>", lambda event: self.inspect_encrypted_file(BUSINESS_FILES[0]))
        print(f"Created file1_label at {self.canvas_width//2-150}, {icon_y_center}")
        file2_label = tk.Label(
            self.canvas,
            text="invoice.txt",
            image=self.file_icon_tk,
            compound="top",
            fg="black",
            bg="#d3d3d3",  # Light gray background for visibility
            font=("Arial", self.BUTTON_FONT_SIZE),
            cursor="hand2",
            width=100,  # Increased size for debugging
            height=70,
            borderwidth=2,  # Add border for visibility
            relief="solid"
        )
        file2_label.image = self.file_icon_tk  # Retain image reference in label
        file2_label.bind("<Button-1>", lambda event: self.inspect_encrypted_file(BUSINESS_FILES[1]))
        print(f"Created file2_label at {self.canvas_width//2+150}, {icon_y_center}")
        file1_item = self.canvas.create_window(
            self.canvas_width // 2 - 150,
            icon_y_center,
            window=file1_label,
            anchor="center"
        )
        file2_item = self.canvas.create_window(
            self.canvas_width // 2 + 150,
            icon_y_center,
            window=file2_label,
            anchor="center"
        )
        self.canvas.addtag_withtag("icon_labels", file1_item)
        self.canvas.addtag_withtag("icon_labels", file2_item)
        self.canvas.tag_raise("icon_labels")
        self.root.update_idletasks()  # Force update
        self.root.update()  # Ensure rendering
        self.icon_items.extend([file1_item, file2_item])  # Store in icon_items
        print("Encrypted file icons created and raised")

    def show_ransomware_backup_recovery_buttons(self):
        text_box_top = 130
        content_height = 400  # Fixed height from show_content_with_animation
        text_box_bottom = text_box_top + content_height
        icon_y_center =  text_box_bottom + 150 # Adjusted to ensure visibility
        print(f"Creating recovery file icons at x={self.canvas_width//2-150}, x={self.canvas_width//2+150}, y={icon_y_center}, canvas_height={self.canvas_height}")
        # Debug rectangle to visualize icon position
        file1_label = tk.Label(
            self.canvas,
            text="business_letter.txt",
            image=self.file_icon_tk,
            compound="top",
            fg="black",
            bg="#d3d3d3",  # Light gray background for visibility
            font=("Arial", self.BUTTON_FONT_SIZE),
            cursor="hand2",
            width=100,  # Increased size for debugging
            height=70,
            borderwidth=2,  # Add border for visibility
            relief="solid"
        )
        file1_label.image = self.file_icon_tk  # Retain image reference in label
        file1_label.bind("<Button-1>", lambda event: self.inspect_restored_file(BUSINESS_FILES[0]))
        print(f"Created file1_label at {self.canvas_width//2-150}, {icon_y_center}")
        file2_label = tk.Label(
            self.canvas,
            text="invoice.txt",
            image=self.file_icon_tk,
            compound="top",
            fg="black",
            bg="#d3d3d3",  # Light gray background for visibility
            font=("Arial", self.BUTTON_FONT_SIZE),
            cursor="hand2",
            width=100,  # Increased size for debugging
            height=70,
            borderwidth=2,  # Add border for visibility
            relief="solid"
        )
        file2_label.image = self.file_icon_tk  # Retain image reference in label
        file2_label.bind("<Button-1>", lambda event: self.inspect_restored_file(BUSINESS_FILES[1]))
        print(f"Created file2_label at {self.canvas_width//2+150}, {icon_y_center}")
        file1_item = self.canvas.create_window(
            self.canvas_width // 2 - 150,
            icon_y_center,
            window=file1_label,
            anchor="center"
        )
        file2_item = self.canvas.create_window(
            self.canvas_width // 2 + 150,
            icon_y_center,
            window=file2_label,
            anchor="center"
        )
        self.canvas.addtag_withtag("icon_labels", file1_item)
        self.canvas.addtag_withtag("icon_labels", file2_item)
        self.canvas.tag_raise("icon_labels")
        self.root.update_idletasks()  # Force update
        self.root.update()  # Ensure rendering
        self.icon_items.extend([file1_item, file2_item])  # Store in icon_items
        print("Recovery file icons created and raised")

    def show_demo_email_buttons(self):
        def on_click():
            self.set_encrypted_files()
            messagebox.showwarning(
                "Ransom Notice",
                "Your files have been encrypted!\n\n"
                "To recover your data, send 0.5 Bitcoin to: 1A1bP2cQ5RFei2D3MPT4T5SLv7Diw0FaN\n"
                "Email proof of payment to: attacker@darkwebmail.com\n"
                "You have 24 hours, or your files will be lost forever.",
                parent=self.root
            )
            self.next_step()

        text_box_top = 130
        content_height = 400  # Match the text widget height
        text_box_bottom = text_box_top + content_height
        link_y_center = text_box_bottom + 50  # Position below the text widget, above navigation buttons

        # Create the email link button similar to navigation buttons
        link_button = tk.Button(
            self.root,
            text="https://www.netflx.com/verify?token=1234567890abcdef",
            command=on_click,
            font=('Arial', self.BUTTON_FONT_SIZE, 'bold'),
            bg=self.theme["bg"],  # Match background
            fg="#00b7eb",  # Cyan color typical for email links
            activeforeground=self.theme["bg"],  # Contrast background on click
            relief="flat",
            bd=0,
            padx=20,  # Increase padding for length
            pady=5,
            cursor="hand2",
            highlightthickness=1,
            highlightcolor="#00b7eb",  # Match link color
            highlightbackground="#00b7eb"
        )
        link_item = self.canvas.create_window(
            self.canvas_width // 2,  # Center horizontally
            link_y_center,
            window=link_button,
            anchor="center"
        )
        self.canvas.tag_raise(link_item)
        self.button_items.append(link_item)

        # # Add border similar to navigation buttons
        # border_width = 200  # Adjust width to fit the long URL
        # border_start_x = (self.canvas_width // 2) - (border_width // 2)
        # border_end_x = (self.canvas_width // 2) + (border_width // 2)
        # link_border = self.canvas.create_rectangle(
        #     border_start_x, link_y_center - 20,
        #     border_end_x, link_y_center + 20,
        #     outline="#00",
        #     width=2,
        #     fill=""
        # )
        # self.button_items.append(link_border)

        print(f"Email link button created at x={self.canvas_width//2}, y={link_y_center}")
    
    def close_demo(self):
        """Clean up and prepare for demo closure."""
        try:
            # Cancel any pending after events
            if hasattr(self.parent, 'after_cancel'):
                for after_id in self.parent.after_info():
                    self.parent.after_cancel(after_id)

            # Destroy canvas items
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)
            if hasattr(self, 'canvas.image'):
                del self.canvas.image  # Remove image reference

            # Destroy widgets in main_frame
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            # Clear button items
            for item in self.button_items:
                self.canvas.delete(item)
            self.button_items.clear()

            # Destroy the main frame
            if self.main_frame:
                self.main_frame.destroy()
        except Exception as e:
            print(f"[ERROR] Error during RAID Visualization cleanup: {e}")

class MainApp:
    def __init__(self, root, title=None, **kwargs):
        self.root = root
        self.theme = kwargs.get("theme", DEFAULT_THEME)
        self.apply_theme_callback = kwargs.get("apply_theme_callback")
        self.root.withdraw()
        self.demo_window = tk.Toplevel(self.root)
        self.demo_window.title(title or "Ransomware Attacks")
        self.demo_window.geometry("1200x800")
        self.demo_window.configure(bg=self.theme["bg"])
        self.demo_window.resizable(True, True)
        success, status = initialize_ransomware_demo(self.demo_window, theme=self.theme)
        if not success:
            messagebox.showerror("Initialization Error", status, parent=self.demo_window)
            self.demo_window.destroy()
            return
        self.ransom_demo = status
        self.demo_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def apply_theme(self, theme):
        self.theme = theme
        self.demo_window.configure(bg=theme["bg"])
        self.ransom_demo.apply_theme(theme)
        if self.apply_theme_callback:
            self.apply_theme_callback(theme)

    def _on_closing(self):
        """Handle the demo window closing event."""
        try:
            # Clean up the RansomwareDemo instance
            if hasattr(self, 'ransom_demo') and self.ransom_demo:
                self.ransom_demo.close_demo()

            # Destroy the demo window
            if self.demo_window:
                self.demo_window.destroy()

            # Do not reiconify the root window; let it exit naturally
            # self.root.deiconify()  # Removed to avoid reopening root
        except Exception as e:
            print(f"[ERROR] Error closing Ransomware Demo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ransomware Attacks")
    root.geometry("1200x800")
    root.configure(bg=DEFAULT_THEME["bg"])
    success, status = initialize_ransomware_demo(root, theme=DEFAULT_THEME)
    if not success:
        messagebox.showerror("Initialization Error", status)
        root.destroy()
    else:
        root.mainloop()