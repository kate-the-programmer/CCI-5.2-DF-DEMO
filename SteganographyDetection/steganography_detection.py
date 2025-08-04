import tkinter as tk
from tkinter import messagebox
import random
import string
from PIL import Image, ImageDraw, ImageTk
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# --- Configuration ---
FONT = 'Courier'
WINDOW_SIZE = '1280x800'

# Default theme matching Password Cracking Demo
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
COVER_IMAGE_PATH = SCRIPT_DIR / 'stegopic.jpg'
STEGO_IMAGE_PATH = SCRIPT_DIR / 'stegopicmsg.png'
NEW_STEGO_IMAGE_PATH = SCRIPT_DIR / 'stegopic_embed.jpg'
DEFAULT_KEY = "defaultkey"

# --- Utility Functions ---
def append_terminal_text(text_widget, message):
    text_widget.config(state='normal')
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_text = f"[{timestamp}] {message}\n"
    text_widget.insert(tk.END, full_text)
    text_widget.see(tk.END)
    text_widget.after(10, lambda: text_widget.see(tk.END))
    text_widget.update_idletasks()
    if message.startswith('[OBSERVATION]'):
        start_idx = text_widget.index(tk.END + "-2l")
        end_idx = text_widget.index(tk.END + "-1c")
        text_widget.tag_add("observation_tag", start_idx, end_idx)
    text_widget.config(state='disabled')

def run_command(command, callback, text_widget=None, shell=True):
    def execute():
        try:
            result = subprocess.run(
                command,
                shell=shell,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )
            callback(result.stdout.strip(), result.stderr.strip())
        except subprocess.CalledProcessError as e:
            callback(None, f'[ERROR] {e.stderr.strip()}')
        except subprocess.TimeoutExpired:
            callback(None, '[ERROR] Command timed out after 60 seconds')
        except FileNotFoundError:
            callback(None, f'[ERROR] Command not found: {command}')
        except Exception as e:
            callback(None, f'[ERROR] Unexpected error: {str(e)}')
    threading.Thread(target=execute, daemon=True).start()

# --- Animation Functions ---
def typewriter_effect(text_id, canvas, full_text, current_text="", index=0):
    if index < len(full_text):
        current_text += full_text[index]
        canvas.itemconfig(text_id, text=current_text + "_")
        canvas.after(50, lambda: typewriter_effect(text_id, canvas, full_text, current_text, index + 1))
    else:
        canvas.itemconfig(text_id, text=full_text)

def typewriter_effect_label(label, full_text, current_text="", index=0):
    if index < len(full_text):
        current_text += full_text[index]
        label.config(text=current_text + "_")
        label.after(50, lambda: typewriter_effect_label(label, full_text, current_text, index + 1))
    else:
        label.config(text=full_text)

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

def animate_instruction_decrypt(label, original_text, step=0):
    if not label.winfo_exists():
        return
    total_steps = 30
    if step >= total_steps:
        label.config(text=original_text)
        return
    fraction = step / total_steps
    display_text = list(original_text)
    for i in range(len(original_text)):
        if i < int(fraction * len(original_text)):
            pass
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
    label.config(text=''.join(display_text))
    label.after(100, lambda: animate_instruction_decrypt(label, original_text, step + 1))

# --- Page Content Definitions ---
class PageContent:
    @staticmethod
    def steganography_basics():
        return (
            "🕵️ Steganography Basics\n"
            "Steganography hides data within innocent-looking files, like images, to conceal messages.\n\n"
            "💾 Why Detect It?\n"
            "Malware or sensitive data can be embedded in images, evading traditional detection.\n\n"
            "🛠️ Use Cases\n"
            "- Uncovering hidden C2 instructions.\n"
            "- Detecting data exfiltration attempts.\n"
            "- Forensic analysis of compromised media.\n\n"
            "Next, let’s explore tools to detect steganography!"
        )

    @staticmethod
    def stegosuite_overview():
        return (
            "🛠️ Stegosuite Overview\n"
            "Stegosuite is a CLI tool for analyzing steganography in image files, detecting hidden data.\n\n"
            "⚡ Key Features\n"
            "- LSB (Least Significant Bit) analysis.\n"
            "- Statistical anomaly detection.\n"
            "- Extraction of embedded messages.\n\n"
            "🔍 Why Use It?\n"
            "It helps identify manipulated images and extract hidden content.\n"
            "Next, let’s view the sample images!"
        )

    @staticmethod
    def image_display():
        return (
            "🖼️ Image Display\n"
            "This page displays the images for visual comparison:\n"
            "- stegopic.jpg: The cover image, a basic JPEG file with no hidden data.\n"
            "- stegopicmsg.png: The stego image, a PNG file with a hidden message.\n\n"
            "Note: The images may look visually similar despite the hidden data.\n"
            "Next, try embedding your own message!"
        )

    @staticmethod
    def steganography_interactive():
        return (
            "🖌️ Embed Your Message\n"
            "Enter a message to embed into stegopic.jpg using the default key 'defaultkey'.\n"
            "The process will be shown in the terminal, and you can extract the message.\n"
            "Click 'Embed Message' to start."
        )

    @staticmethod
    def steganography_analysis():
        return (
            "🔍 Analyze Steganography\n"
            "Analyze both stegopic.jpg and stegopic_embed.jpg.\n"
            "Click buttons to check capacity and extract data from each image."
        )

    @staticmethod
    def summary():
        return (
            "📝 Demo Summary\n"
            "- Steganography Basics: Learned how data is hidden in images.\n"
            "- Stegosuite Overview: Explored a CLI tool for detection.\n"
            "- Image Display: Viewed stegopic.jpg and stegopicmsg.png visually.\n"
            "- Interactive: Embedded and extracted a custom message with default key 'defaultkey'.\n"
            "- Analysis: Confirmed stegopic.jpg has no hidden capacity; stegopicmsg.png requires a key.\n\n"
            "📋 Common Commands\n"
            "- Check capacity: stegosuite capacity image.jpg\n"
            "- Embed data: stegosuite embed -k <key> -m \"<message>\" image.jpg -o stego.jpg\n"
            "- Extract data: stegosuite extract -k <key> stego.jpg\n\n"
            "🎯 Next Steps\n"
            "- Experiment with different messages using the default key.\n"
            "- Analyze extracted data for malicious content.\n"
            "- Verify image integrity with forensic tools.\n"
            "- Mitigate by scanning all media uploads.\n\n"
            "Thank you for completing the Steganography Detection Demo!"
        )

# --- Main Application ---
class MainApp:
    def __init__(self, root, theme=None, apply_theme_callback=None):
        self.root = root
        self.root.title("Steganography Detection Demo")
        self.root.geometry(WINDOW_SIZE)
        self.current_screen = None
        self.theme = theme if theme else DEFAULT_THEME
        self.apply_theme_callback = apply_theme_callback
        self.last_width = 1280
        self.last_height = 720
        self.canvas_width = 1200
        self.canvas_height = 680
        self.current_step = 0
        self.steps = ["🕵️ Steganography Basics", "🛠️ Stegosuite Overview", "🖼️ Image Display", 
                      "🖌️ Embed Your Message", "🔍 Analyze Steganography", "📝 Demo Summary"]
        self.header_items = []
        self.button_items = []
        self.bg_image_id = None
        self.current_text_widget = None
        self.canvas_item_id = None
        self.bg_photo = None
        self.demo_frame = None
        self.step_count = 0
        self.total_steps = 4  # Match the analysis steps (Check Capacity, Extract Data for each image)
        self.script_dir = Path(__file__).parent
        self.cover_image_path = COVER_IMAGE_PATH
        self.stego_image_path = STEGO_IMAGE_PATH
        self.new_stego_image_path = NEW_STEGO_IMAGE_PATH
        self.default_key = DEFAULT_KEY
        self.message_entry = None
        self.extract_button = None

        self.pages = [
            {"title": "🕵️ Steganography Basics", "content": PageContent.steganography_basics, "mode": "info"},
            {"title": "🛠️ Stegosuite Overview", "content": PageContent.stegosuite_overview, "mode": "info"},
            {"title": "🖼️ Image Display", "content": PageContent.image_display, "mode": "info"},
            {"title": "🖌️ Embed Your Message", "content": PageContent.steganography_interactive, "mode": "demo"},
            {"title": "🔍 Analyze Steganography", "content": PageContent.steganography_analysis, "mode": "demo"},
            {"title": "📝 Demo Summary", "content": PageContent.summary, "mode": "info"}
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
        
        self.update_step()

    def create_background(self):
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
        if hasattr(self, "cover_img_id"):
            self.canvas.delete(self.cover_img_id)
        if hasattr(self, "stego_img_id"):
            self.canvas.delete(self.stego_img_id)


        page = self.pages[self.current_step]
        if self.bg_image_id:
            self.canvas.tag_lower(self.bg_image_id)

        if page["mode"] == "info":
            self.create_page_header(page)
            self.current_text = page['content']()

            if self.current_step == 2:
                self.show_content_with_animation(height=280)
                self.display_images()
            else:
                self.show_content_with_animation()

            self.create_navigation_buttons()
        else:
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
        
        typewriter_effect(title_id, self.canvas, page['title'])

    def show_content_with_animation(self, height=None):
        self.root.update_idletasks()
        content_width = max(800, self.canvas_width - 100)
        content_height = height if height else max(400, self.canvas_height - 200)
        
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
        
        decrypt_animation(text_widget, self.current_text)

    def setup_demo_frame(self):
        if self.current_step == 3:  # Embed Your Message
            self.demo_frame = tk.Frame(self.root, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=0, y=0)
            self.demo_frame.lift()

            label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], font=(FONT, 18))
            label.place(relx=0.5, y=20, anchor='n')
            typewriter_effect_label(label, '🖌️ Embed Your Message')

            input_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            input_frame.place(relx=0.5, rely=0.3, anchor='center')

            message_label = tk.Label(input_frame, text="Message:", fg=self.theme["fg"], bg=self.theme["bg"], font=(FONT, 12))
            message_label.grid(row=0, column=0, padx=5, pady=5)
            self.message_entry = tk.Entry(input_frame, bg=self.theme["terminal_bg"], fg=self.theme["fg"], font=(FONT, 12), width=40)
            self.message_entry.grid(row=0, column=1, padx=5, pady=5)

            self.current_text_widget = tk.Text(self.demo_frame, bg=self.theme["terminal_bg"], fg=self.theme["terminal_fg"], 
                                  insertbackground=self.theme["fg"], font=(FONT, 12), wrap='word', width=120, height=14)
            self.current_text_widget.place(relx=0.5, rely=0.58, anchor='center')  # move up slightly

            self.current_text_widget.config(state='disabled')

            button_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            button_frame.place(relx=0.5, rely=0.7, anchor='center')

            embed_button = tk.Button(button_frame, text="Embed Message", bg=self.theme["button_bg"], 
                                   fg=self.theme["button_fg"], font=(FONT, 12), command=self.embed_message)
            embed_button.grid(row=0, column=0, padx=5, pady=5)

            self.extract_button = tk.Button(button_frame, text="Extract Message", bg=self.theme["button_bg"], 
                                          fg=self.theme["button_fg"], font=(FONT, 12), command=self.extract_message, state='disabled')
            self.extract_button.grid(row=0, column=1, padx=5, pady=5)

            self.instruction_label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], 
                                  font=(FONT, 14), wraplength=1000, justify='center')
            self.instruction_label.place(relx=0.5, rely=0.12, anchor='center')

            self.animate_instruction_decrypt(
                self.instruction_label,
                "Enter a message to embed into stegopic.jpg using the default key 'defaultkey'.\n"
                "The process will be shown in the terminal, and you can extract the message.\n"
                "Click 'Embed Message' to start."
            )

            self.create_navigation_buttons()

        elif self.current_step == 4:  # 🔍 Analyze Steganography
            # --- frame only occupies upper 82 % so nav/progress show at bottom ------
            self.demo_frame = tk.Frame(self.root, bg=self.theme["bg"])
            self.demo_frame.place(x=0, y=0, relwidth=1, relheight=0.82)

            # headline / instructions
            self.instruction_label = tk.Label(
                self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"],
                font=(FONT, 14), wraplength=1000, justify='center'
            )
            self.instruction_label.place(relx=0.5, rely=0.08, anchor='center')

            # -------------------- tool buttons --------------------
            button_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            button_frame.place(relx=0.5, rely=0.25, anchor='center')

            self.btn1_cover_capacity = tk.Button(
                button_frame, text='🔍 Check Capacity (stegopic.jpg)',
                bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                font=(FONT, 10), width=30, command=self.check_cover_capacity
            )
            self.btn1_cover_capacity.grid(row=0, column=0, padx=5, pady=5)

            self.btn1_cover_extract = tk.Button(
                button_frame, text='💾 Extract Data (stegopic.jpg)',
                bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                font=(FONT, 10), width=30, command=self.extract_cover_data
            )
            self.btn1_cover_extract.grid(row=1, column=0, padx=5, pady=5)

            self.btn2_new_capacity = tk.Button(
                button_frame, text='🔍 Check Capacity (stegopic_embed.jpg)',
                bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                font=(FONT, 10), width=30, command=self.check_new_capacity
            )
            self.btn2_new_capacity.grid(row=0, column=1, padx=5, pady=5)

            self.btn2_new_extract = tk.Button(
                button_frame, text='💾 Extract Data (stegopic_embed.jpg)',
                bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                font=(FONT, 10), width=30, command=self.extract_new_data
            )
            self.btn2_new_extract.grid(row=1, column=1, padx=5, pady=5)

            # ---------------- terminal box -----------------------
            self.current_text_widget = tk.Text(
                self.demo_frame, bg=self.theme["terminal_bg"], fg=self.theme["terminal_fg"],
                insertbackground=self.theme["fg"], font=(FONT, 12), wrap='word',
                width=120, height=14        # shorter to keep bottom clear
            )
            self.current_text_widget.place(relx=0.5, rely=0.57, anchor='center')
            self.current_text_widget.config(state='disabled')
            self.current_text_widget.tag_configure(
                "observation_tag", background="#FFFF99", foreground="#000000",
                font=(FONT, 12, "bold")
            )

            # animate the instruction text
            self.animate_instruction_decrypt(
                self.instruction_label,
                "Analyze both stegopic.jpg and stegopic_embed.jpg.\n"
                "Click buttons to check capacity and extract data."
            )

            # enable tool buttons + NAVIGATION BAR
            for btn in (self.btn1_cover_capacity, self.btn1_cover_extract,
                        self.btn2_new_capacity, self.btn2_new_extract):
                btn.config(state='normal')

            self.create_navigation_buttons()          # nav & progress now visible



    def create_navigation_buttons(self):
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

    def embed_message(self):
        message = self.message_entry.get().strip()
        if not message:
            append_terminal_text(self.current_text_widget, "Please enter a message.")
            return

        embed_command = f'stegosuite embed -k "{self.default_key}" -m "{message}" "{self.cover_image_path}" -o "{self.new_stego_image_path}"'
        append_terminal_text(self.current_text_widget, f"> {embed_command}")
        append_terminal_text(self.current_text_widget, "Embedding message... Please wait.")
        run_command(embed_command, self.on_embed_complete, self.current_text_widget)

    def on_embed_complete(self, stdout, stderr):
        if stderr:
            filtered_stderr = '\n'.join(line for line in stderr.split('\n') if not line.startswith('Picked up _JAVA_OPTIONS'))
            if filtered_stderr:
                append_terminal_text(self.current_text_widget, f"[ERROR] {filtered_stderr}")
            actual_output_path = self.script_dir / 'stegopic_embed.jpg'
            if actual_output_path.exists():
                append_terminal_text(self.current_text_widget, "Embedding succeeded, but output file renamed to stegopic_embed.jpg.")
                self.new_stego_image_path = actual_output_path
                self.extract_button.config(state='normal')
        else:
            append_terminal_text(self.current_text_widget, "Message embedded successfully! New image created.")
            self.extract_button.config(state='normal')

    def extract_message(self):
        extract_command = f'stegosuite extract -k "{self.default_key}" "{self.new_stego_image_path}"'
        append_terminal_text(self.current_text_widget, f"> {extract_command}")
        append_terminal_text(self.current_text_widget, "Extracting message... Please wait.")
        run_command(extract_command, self.on_extract_complete, self.current_text_widget)

    def on_extract_complete(self, stdout, stderr):
        if stderr:
            filtered_stderr = '\n'.join(line for line in stderr.split('\n') if not line.startswith('Picked up _JAVA_OPTIONS'))
            if filtered_stderr:
                append_terminal_text(self.current_text_widget, f"[ERROR] {filtered_stderr}")

        if stdout:
            lines = stdout.strip().splitlines()
            extracted_message = None
            for line in lines:
                if line.lower().startswith("extracted message:"):
                    extracted_message = line.split(":", 1)[1].strip()
                append_terminal_text(self.current_text_widget, line)

            if extracted_message:
                append_terminal_text(self.current_text_widget, f"📦 Extracted message: {extracted_message}")
            else:
                append_terminal_text(self.current_text_widget, "No clearly marked message found.")
        else:
            append_terminal_text(self.current_text_widget, "No message extracted. Check the image or increase timeout if needed.")

    def check_cover_capacity(self):
        self.btn1_cover_capacity.config(state='disabled')
        append_terminal_text(self.current_text_widget, '[STEP 1] Checking stegopic.jpg capacity...')
        append_terminal_text(self.current_text_widget, f'> stegosuite capacity "{self.cover_image_path}"')
        run_command(f'stegosuite capacity "{self.cover_image_path}"', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else '[OUTPUT] No capacity data available.'),
            append_terminal_text(self.current_text_widget, stderr if stderr else ''),
            append_terminal_text(self.current_text_widget, '[OBSERVATION] Capacity of stegopic.jpg indicates no significant hidden data.\n'
                                                    'What to look for: Low or zero capacity values.'),
            self.btn1_cover_capacity.config(state='normal')
        ), self.current_text_widget)

    def extract_cover_data(self):
        self.btn1_cover_extract.config(state='disabled')
        append_terminal_text(self.current_text_widget, '[STEP 2] Extracting data from stegopic.jpg...')
        append_terminal_text(self.current_text_widget, f'> stegosuite extract -k "{self.default_key}" "{self.cover_image_path}"')
        run_command(f'stegosuite extract -k "{self.default_key}" "{self.cover_image_path}"', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else '[OUTPUT] No data extracted.'),
            append_terminal_text(self.current_text_widget, stderr if stderr else ''),
            append_terminal_text(self.current_text_widget, '[OBSERVATION] No data extracted from stegopic.jpg with default key.\n'
                                                    'What to look for: No message unless previously embedded.'),
            self.btn1_cover_extract.config(state='normal')
        ), self.current_text_widget)

    def check_new_capacity(self):
        self.btn2_new_capacity.config(state='disabled')
        append_terminal_text(self.current_text_widget, '[STEP 3] Checking stegopic_embed.jpg capacity...')
        append_terminal_text(self.current_text_widget, f'> stegosuite capacity "{self.new_stego_image_path}"')
        run_command(f'stegosuite capacity "{self.new_stego_image_path}"', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else '[OUTPUT] No capacity data available.'),
            append_terminal_text(self.current_text_widget, stderr if stderr else ''),
            append_terminal_text(self.current_text_widget, '[OBSERVATION] Capacity of stegopic_embed.jpg may indicate hidden data.\n'
                                                    'What to look for: Non-zero capacity values.'),
            self.btn2_new_capacity.config(state='normal')
        ), self.current_text_widget)

    def extract_new_data(self):
        self.btn2_new_extract.config(state='disabled')
        append_terminal_text(self.current_text_widget, '[STEP 4] Extracting data from stegopic_embed.jpg...')
        append_terminal_text(self.current_text_widget, f'> stegosuite extract -k "{self.default_key}" "{self.new_stego_image_path}"')
        run_command(f'stegosuite extract -k "{self.default_key}" "{self.new_stego_image_path}"', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else '[OUTPUT] No data extracted or error occurred.'),
            append_terminal_text(self.current_text_widget, stderr if stderr else ''),
            append_terminal_text(self.current_text_widget, '[OBSERVATION] Data extracted from stegopic_embed.jpg with default key.\n'
                                                    'What to look for: Extracted message or file path.'),
            self.btn2_new_extract.config(state='normal')
        ), self.current_text_widget)

    def display_images(self):
        try:
            cover_img = Image.open(self.cover_image_path).resize((400, 300), Image.LANCZOS)
            stego_img = Image.open(self.stego_image_path).resize((400, 300), Image.LANCZOS)

            self.cover_photo = ImageTk.PhotoImage(cover_img)
            self.stego_photo = ImageTk.PhotoImage(stego_img)

            # Display both on canvas
            cover_x = self.canvas_width // 4
            stego_x = (self.canvas_width * 3) // 4
            image_y = 550  # position below the reduced text box

            self.cover_img_id = self.canvas.create_image(cover_x, image_y, image=self.cover_photo)
            self.stego_img_id = self.canvas.create_image(stego_x, image_y, image=self.stego_photo)

        except Exception as e:
            print(f"[ERROR loading images] {e}")


    def typewriter_effect_label(self, widget, full_text, current_text="", index=0):
        if index < len(full_text):
            current_text += full_text[index]
            widget.config(text=current_text + "_")
            self.root.after(50, lambda: self.typewriter_effect_label(widget, full_text, current_text, index + 1))
        else:
            widget.config(text=full_text)

    def animate_instruction_decrypt(self, widget, original_text, step=0):
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
        self.root.after(100, lambda: self.animate_instruction_decrypt(widget, original_text, step + 1))

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()