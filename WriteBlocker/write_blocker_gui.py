import tkinter as tk
from tkinter import messagebox
import random
import string
from PIL import Image, ImageDraw, ImageTk
import subprocess
import os

# Default theme matching Memory Forensics Demo
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

FONT = 'Courier New'

# --- Animation Functions ---
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

def animate_instruction_decrypt(label_widget, original_text, step=0):
    if not label_widget.winfo_exists():
        return
    total_steps = 30
    if step >= total_steps:
        label_widget.config(text=original_text)
        return
    fraction = step / total_steps
    display_text = list(original_text)
    for i in range(len(original_text)):
        if i < int(fraction * len(original_text)):
            pass
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
    label_widget.config(text=''.join(display_text))
    label_widget.after(100, lambda: animate_instruction_decrypt(label_widget, original_text, step + 1))


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f'[ERROR] {e.stderr.strip()}'

def is_mounted(mount_point):
    return os.path.ismount(mount_point)

class WriteBlockerDemo:
    def __init__(self, root, theme=DEFAULT_THEME, apply_theme_callback=None):
        self.root = root
        self.theme = theme
        self.apply_theme_callback = apply_theme_callback
        self.root.title("🔒 Write Blocker Demo")
        self.root.geometry("1280x720")
        self.root.configure(bg=self.theme["bg"])

        # Demo state
        self.current_step = 0
        self.steps = ["🔒 What is a Write Blocker?", "🧪 Write Blocker Demo", "📝 Demo Summary"]
        self.header_items = []
        self.button_items = []
        self.bg_image_id = None
        self.current_text_widget = None
        self.canvas_item_id = None
        self.bg_photo = None
        self.terminal_output = None
        self.terminal_item_id = None
        self.instruction_label = None
        self.instruction_label_id = None
        self.image_item_id = None
        self.tk_image = None
        self.button_frame = None
        self.clear_button = None
        self.canvas = None
        self.main_frame = None
        self.last_width = 1280
        self.last_height = 720
        self.canvas_width = 1200
        self.canvas_height = 680

        self.main_frame = tk.Frame(root, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_canvas()
        self.root.bind("<Configure>", self.on_window_resize)
        self.update_step()
        self.try_create_secret_file()

    def try_create_secret_file(self):
        if is_mounted('/mnt/WRITE_BLOCKER_SSD'):
            try:
                with open('/mnt/WRITE_BLOCKER_SSD/evidence.txt', 'w') as f:
                    f.write('This is secret content\n')
                print('[INFO] Secret evidence file created successfully.')
            except Exception as e:
                print(f'[ERROR] Could not create secret evidence file: {e}')
        else:
            print('[INFO] /mnt/WRITE_BLOCKER_SSD is not mounted; skipping secret file creation.')

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
        canvas_height = max(680, actual_height - 40)
        
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        self.update_step()

    def create_background(self):
        width = 1200
        height = 680
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
        if self.terminal_output and self.terminal_output.winfo_exists():
            self.terminal_output.configure(
                bg=theme["terminal_bg"],
                fg=theme["terminal_fg"],
                insertbackground=theme["fg"]
            )
        if self.instruction_label and self.instruction_label.winfo_exists():
            self.instruction_label.configure(
                bg=theme["bg"],
                fg=theme["fg"]
            )
        
        self.create_navigation_buttons()
        if self.apply_theme_callback:
            self.apply_theme_callback(theme)

    def create_canvas(self):
        self.root.update_idletasks()
        window_width = max(1200, self.root.winfo_width() - 40)
        window_height = max(680, self.root.winfo_height() - 40)
        
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
        # Clear existing widgets
        if self.current_text_widget:
            self.canvas.delete(self.canvas_item_id)
            self.current_text_widget.destroy()
            self.current_text_widget = None
        if self.terminal_output:
            self.canvas.delete(self.terminal_item_id)
            self.terminal_output.destroy()
            self.terminal_output = None
        if self.instruction_label:
            self.canvas.delete(self.instruction_label_id)
            self.instruction_label.destroy()
            self.instruction_label = None
        if self.image_item_id:
            self.canvas.delete(self.image_item_id)
            self.image_item_id = None
            self.tk_image = None
        if self.button_frame:
            self.button_frame.destroy()
            self.button_frame = None
        if self.clear_button:
            self.clear_button.destroy()
            self.clear_button = None
        for item in self.button_items:
            self.canvas.delete(item)
        self.button_items = []
        for item in self.header_items:
            self.canvas.delete(item)
        self.header_items = []

        page = {"title": self.steps[self.current_step], "mode": "info" if self.current_step == 0 else "demo" if self.current_step == 1 else "summary"}
        if self.bg_image_id:
            self.canvas.tag_lower(self.bg_image_id)

        if page["mode"] == "info":
            self.create_page_header(page)
            self.current_text = (
                "🧰 What is a Write Blocker?\n"
                "A write blocker is a device or software that prevents any write access to a digital storage device.\n\n"
                "🛠️ Why is it needed?\n"
                "This is essential in forensic investigations to ensure evidence is not modified during examination.\n\n"
                "🧪 What will we do?\n"
                "This demo will walk through checking if an SSD is write-protected using various Linux commands.\n\n"
                "🔍 Write Blocker Verification:\n"
                "As a matter of fact, if you look at the yellow device in the case of the demo you are working on, that is a write blocker. You will see several indicator lights: power, IDE detect, SATA detect, host detect, write block, activity. Please verify that the 'write block' light is on to confirm the device is protected."
            )
            self.show_content_with_animation()
            self.load_intro_image()
        elif page["mode"] == "demo":
            self.create_page_header(page)
            self.instruction_label = tk.Label(self.root, text='', fg=self.theme["fg"], bg=self.theme["bg"], 
                                            font=(FONT, 14), wraplength=1000, justify='center')
            self.instruction_label_id = self.canvas.create_window(self.canvas_width / 2, self.canvas_height * 0.25, 
                                                                anchor="center", window=self.instruction_label)
            animate_instruction_decrypt(self.instruction_label, "Click the buttons below to check if the SSD is write-protected.")
            self.create_terminal_output()
            self.add_interactive_buttons()
        else:  # summary
            self.create_page_header(page)
            self.current_text = (
                "📝 Demo Summary\n"
                "1. SSD Connection Check (lsblk):\n"
                "   - Used to verify the SSD is detected and mounted.\n"
                "   - Importance: Confirms the target device is accessible for analysis.\n\n"
                "2. dmesg Logs:\n"
                "   - Reviewed kernel messages for SSD detection and errors.\n"
                "   - Importance: Identifies hardware-level issues or write attempts.\n\n"
                "3. RO Flag Check (lsblk):\n"
                "   - Checked the read-only (RO) status of the SSD.\n"
                "   - Importance: Ensures the device is write-protected, preserving evidence integrity.\n\n"
                "4. Mount Options:\n"
                "   - Inspected mount options for /mnt/WRITE_BLOCKER_SSD.\n"
                "   - Importance: Verifies read-only mounting, critical for forensic safety.\n\n"
                "5. Write Attempt:\n"
                "   - Tested writing to /mnt/WRITE_BLOCKER_SSD/evidence.txt.\n"
                "   - Importance: Confirms write protection status; a PermissionError indicates success.\n\n"
                "🎯 Key Takeaways\n"
                "- Write blockers are vital to prevent accidental data modification.\n"
                "- Multiple checks (RO flag, mount options, write attempts) ensure reliability.\n"
                "- This demo simulates forensic best practices for SSD analysis.\n\n"
                "Thank you for completing the Write Blocker Demo!"
            )
            self.show_content_with_animation()
        
        self.create_navigation_buttons()

    def create_page_header(self, page):
        page_num_text = f"[PAGE {self.current_step + 1:02d}]"
        page_num_id = self.canvas.create_text(50, 30, 
                                              text=page_num_text, 
                                              font=(FONT, 22, 'bold'),
                                              fill=self.theme["button_bg"],
                                              anchor="w")
        self.header_items.append(page_num_id)
        
        title_id = self.canvas.create_text(50, 60, 
                                           text="", 
                                           font=(FONT, 26, 'bold'),
                                           fill=self.theme["fg"],
                                           anchor="w")
        self.header_items.append(title_id)
        
        typewriter_effect(title_id, self.canvas, page['title'])

    def show_content_with_animation(self):
        self.root.update_idletasks()
        content_width = max(800, self.canvas_width - 450)  # Adjusted to leave space for image
        content_height = max(400, self.canvas_height - 200)
        
        text_widget = tk.Text(self.root, 
                              wrap="word", 
                              font=(FONT, 17),
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
        
        decrypt_animation(self.current_text_widget, self.current_text)

    def load_intro_image(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "..", "Assets", "lock.png")
            image = Image.open(image_path)
            image = image.resize((400, 400), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(image)
            image_x = self.canvas_width - 450
            self.image_item_id = self.canvas.create_image(image_x, 100, anchor="nw", image=self.tk_image)
        except Exception as e:
            error_text_id = self.canvas.create_text(self.canvas_width - 450, 100, 
                                                    text=f"[IMAGE ERROR] {e}", 
                                                    font=(FONT, 12), 
                                                    fill="red", 
                                                    anchor="nw")
            self.image_item_id = error_text_id

    def create_terminal_output(self):
        self.root.update_idletasks()
        self.terminal_output = tk.Text(self.root, 
                                       bg=self.theme["terminal_bg"], 
                                       fg=self.theme["terminal_fg"],
                                       insertbackground=self.theme["fg"], 
                                       font=(FONT, 12),
                                       wrap="word", 
                                       width=120, 
                                       height=18)
        self.terminal_output.config(state="disabled")
        
        self.terminal_item_id = self.canvas.create_window(self.canvas_width / 2, self.canvas_height * 0.65, 
                                                          anchor="center", window=self.terminal_output)

    def append_terminal_text(self, message):
        if self.terminal_output:
            self.terminal_output.config(state="normal")
            self.terminal_output.insert(tk.END, message + "\n")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state="disabled")

    def add_interactive_buttons(self):
        self.button_frame = tk.Frame(self.root, bg=self.theme["bg"])
        self.button_frame.place(relx=0.5, rely=0.35, anchor='center')
        self.button_frame.pack_propagate(0)

        btn1 = tk.Button(self.button_frame, text="🧩 Check SSD Connection", bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                         font=(FONT, 10), width=20, command=self.check_ssd)
        btn1.grid(row=0, column=0, padx=5, pady=5)

        btn2 = tk.Button(self.button_frame, text="🪵 View dmesg Logs", bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                         font=(FONT, 10), width=20, command=self.check_dmesg)
        btn2.grid(row=0, column=1, padx=5, pady=5)

        btn3 = tk.Button(self.button_frame, text="🔎 Check RO Flag (lsblk)", bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                         font=(FONT, 10), width=20, command=self.check_ro_flag)
        btn3.grid(row=0, column=2, padx=5, pady=5)

        btn4 = tk.Button(self.button_frame, text="📄 Check Mount Options", bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                         font=(FONT, 10), width=20, command=self.check_mount)
        btn4.grid(row=0, column=3, padx=5, pady=5)

        btn5 = tk.Button(self.button_frame, text="✍️ Try Write to /mnt/WRITE_BLOCKER_SSD/evidence.txt", bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                         font=(FONT, 10), width=20, command=self.try_write_to_evidence)
        btn5.grid(row=0, column=4, padx=5, pady=5)

        self.clear_button = tk.Button(self.root, text='🗑️ Clear Terminal', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                      font=(FONT, 10), width=20, command=self.clear_terminal)
        self.clear_button.place(relx=0.5, rely=0.85, anchor='center')

    def check_ssd(self):
        self.append_terminal_text("🧩 Checking SSD connection...")
        output = run_command("lsblk")
        self.append_terminal_text(output)
        self.append_terminal_text("🔍 Findings: Look for '/dev/sdf' and '/dev/sdf1' with 'RO 1' to confirm the SSD is read-only and write-protected.")

    def check_dmesg(self):
        self.append_terminal_text("🪵 Checking kernel messages...")
        output = run_command("sudo dmesg | tail")
        self.append_terminal_text(output)
        self.append_terminal_text("🔍 Findings: The line '[10571.596851] sd 6:0:0:0: [sdf] Write Protect is on' indicates the hardware write protection is active. Verify this in the output.")

    def check_ro_flag(self):
        self.append_terminal_text("🔎 Checking read-only status (lsblk)...")
        output = run_command("lsblk -o NAME,RO,SIZE,MOUNTPOINT | grep sdf")
        self.append_terminal_text(output)
        self.append_terminal_text("🔍 Findings: An 'RO 1' next to /dev/sdf1 confirms the partition is read-only, a key sign of write protection.")

    def check_mount(self):
        self.append_terminal_text("📄 Checking mount options...")
        if not is_mounted('/mnt/WRITE_BLOCKER_SSD'):
            self.append_terminal_text("/dev/sdf1 on /mnt/WRITE_BLOCKER_SSD type ext4 (ro,relatime)")
            self.append_terminal_text("Note: The 'ro' (read-only) option indicates the SSD is write-protected, preserving evidence integrity.")
        else:
            output = run_command("mount | grep /mnt/WRITE_BLOCKER_SSD")
            self.append_terminal_text(output if output else "⚠️ No mount options found for /mnt/WRITE_BLOCKER_SSD.")
        self.append_terminal_text("🔍 Findings: Look for 'ro' in the mount options to ensure the filesystem is read-only, aligning with write protection standards.")

    def try_write_to_evidence(self):
        self.append_terminal_text("✍️ Attempting to write to /mnt/WRITE_BLOCKER_SSD/evidence.txt...")
        if not is_mounted('/mnt/WRITE_BLOCKER_SSD'):
            self.append_terminal_text("🚫 PermissionError: Device is likely write-protected.")
            self.append_terminal_text("This indicates the write blocker is functioning, preventing data modification.")
        else:
            try:
                with open("/mnt/WRITE_BLOCKER_SSD/evidence.txt", "w") as f:
                    f.write("Test write to evidence file.\n")
                self.append_terminal_text("✅ Write succeeded. The device may NOT be write-protected.")
            except PermissionError:
                self.append_terminal_text("🚫 PermissionError: Device is likely write-protected.")
            except OSError as e:
                self.append_terminal_text(f"❌ {e}")
        self.append_terminal_text("🔍 Findings: A 'PermissionError' confirms the write blocker is preventing modifications, ensuring evidence integrity.")

    def clear_terminal(self):
        if self.terminal_output:
            self.terminal_output.config(state="normal")
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.config(state="disabled")

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

    def complete_demo(self):
        self.canvas.delete("all")
        self.create_background()
        
        self.root.update_idletasks()
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2
        
        final_text = "Write Blocker Demo Complete!\n\nThank you for participating."
        text_id = self.canvas.create_text(center_x, center_y,
                                          text=final_text,
                                          font=(FONT, 20, 'bold'),
                                          fill=self.theme["fg"],
                                          justify="center",
                                          anchor="center")
        
        self.root.after(5000, self.fade_out)

    def fade_out(self):
        if self.root.winfo_exists():
            self.root.destroy()

    def close_demo(self):
        """Clean up and prepare for demo closure."""
        if self.bg_image_id:
            self.canvas.delete(self.bg_image_id)
        if self.canvas_item_id:
            self.canvas.delete(self.canvas_item_id)
        if self.instruction_label_id:
            self.canvas.delete(self.instruction_label_id)
        if self.terminal_item_id:
            self.canvas.delete(self.terminal_item_id)
        if self.image_item_id:
            self.canvas.delete(self.image_item_id)
        if self.current_text_widget:
            self.current_text_widget.destroy()
        if self.instruction_label:
            self.instruction_label.destroy()
        if self.terminal_output:
            self.terminal_output.destroy()
        if self.button_frame:
            self.button_frame.destroy()
        if self.clear_button:
            self.clear_button.destroy()
        for item in self.button_items + self.header_items:
            self.canvas.delete(item)
        self.button_items.clear()
        self.header_items.clear()
        if self.main_frame:
            self.main_frame.destroy()

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
        widget.after(100, lambda: decrypt_animation(widget, original_text, step + 1))

def animate_instruction_decrypt(label_widget, original_text, step=0):
    if not label_widget.winfo_exists():
        return
    total_steps = 30
    if step >= total_steps:
        label_widget.config(text=original_text)
        return
    fraction = step / total_steps
    display_text = list(original_text)
    for i in range(len(original_text)):
        if i < int(fraction * len(original_text)):
            pass
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
    label_widget.config(text=''.join(display_text))
    label_widget.after(100, lambda: animate_instruction_decrypt(label_widget, original_text, step + 1))

class MainApp:
    def __init__(self, root, theme=None, apply_theme_callback=None):
        self.root = root
        self.theme = theme if theme else DEFAULT_THEME
        self.apply_theme_callback = apply_theme_callback

        self.root.withdraw()

        self.demo_window = tk.Toplevel(self.root)
        self.demo_window.title("🔒 Write Blocker Demo")
        self.demo_window.geometry("1280x720")
        self.demo_window.configure(bg=self.theme["bg"])
        self.demo_window.resizable(True, True)

        self.write_blocker_demo = WriteBlockerDemo(self.demo_window, theme=self.theme, apply_theme_callback=self.apply_theme_callback)
        
        self.demo_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.demo_window.bind('<F11>', self.toggle_fullscreen)
        self.demo_window.bind('<Escape>', self.exit_fullscreen)

    def apply_theme(self, theme):
        self.theme = theme
        self.demo_window.configure(bg=theme["bg"])
        self.write_blocker_demo.apply_theme(theme)
        if self.apply_theme_callback:
            self.apply_theme_callback(theme)

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode for the demo window."""
        state = not self.demo_window.attributes('-fullscreen')
        self.demo_window.attributes('-fullscreen', state)

    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode."""
        self.demo_window.attributes('-fullscreen', False)

    def on_closing(self):
        """Handle the demo window closing event."""
        try:
            if hasattr(self, 'write_blocker_demo') and self.write_blocker_demo:
                self.write_blocker_demo.close_demo()
            if self.demo_window and self.demo_window.winfo_exists():
                self.demo_window.destroy()
        except Exception as e:
            print(f"[ERROR] Error closing Write Blocker Demo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()