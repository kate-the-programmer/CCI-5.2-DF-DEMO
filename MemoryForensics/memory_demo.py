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

# File paths
SCRIPT_DIR = Path(__file__).parent
VOLATILITY_PATH = SCRIPT_DIR / 'volatility3/vol.py'
MEMORY_DUMP_PATH = SCRIPT_DIR / 'sample.mem'
OUTPUT_DIR = SCRIPT_DIR / 'output_dir'
OUTPUT_DIR.mkdir(exist_ok=True)

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

# --- Page Content Definitions ---
class PageContent:
    @staticmethod
    def memory_forensics_basics():
        return (
            "🖥️ Memory Forensics Basics\n"
            "Memory forensics involves analyzing a computer’s RAM to uncover evidence of malicious activity, such as malware or intrusions.\n\n"
            "💾 Why Analyze Memory?\n"
            "RAM holds volatile data—running processes, network connections, and injected code—that vanishes after a reboot. "
            "This makes it essential for incident response and malware analysis.\n\n"
            "🛠️ Use Cases\n"
            "- Detecting malware like rootkits and trojans.\n"
            "- Recovering details about processes and network activity.\n"
            "- Investigating suspicious system behavior.\n\n"
            "Next, let’s dive into Volatility 3, a powerful tool for memory forensics!"
        )

    @staticmethod
    def volatility_overview():
        return (
            "🔬 Volatility 3 Overview\n"
            "Volatility 3 is an open-source memory forensics framework for analyzing RAM dumps from Windows, Linux, and macOS systems.\n\n"
            "⚡ Key Features\n"
            "- Cross-platform: Supports multiple OS and dump formats.\n"
            "- Plugin-based: Uses extensible modules like malfind, pstree, and netscan.\n"
            "- Simplified: No OS profiles required, making analysis faster.\n\n"
            "🔍 Why Use It?\n"
            "It uncovers malware, process anomalies, and network activity, making it a go-to tool for forensic investigators.\n"
            "Next, we’ll explore key Volatility 3 plugins to analyze a memory dump."
        )

    @staticmethod
    def volatility_plugins():
        return (
            "🔧 Volatility 3 Plugins\n"
            "Volatility 3 uses plugins to dissect memory dumps. Here are the ones we’ll use:\n\n"
            "- pslist: Lists running processes to identify suspicious ones.\n"
            "- malfind: Detects injected code in memory, like malware shellcode.\n"
            "- pstree: Shows process hierarchy to spot unusual parent-child relationships.\n"
            "- netscan: Lists network connections tied to processes, revealing suspicious activity.\n"
            "- dlllist: Lists DLLs loaded by processes to find malicious modules.\n\n"
            "🛠️ How They Work\n"
            "Plugins parse RAM data to extract details like process IDs, memory regions, or network sockets.\n\n"
            "Let’s use these plugins to investigate a suspicious memory dump!"
        )

    @staticmethod
    def volatility_demo():
        return (
            "🕵️‍♂️ Scenario: Investigate Suspicious Memory Dump\n"
            "You’ve received a memory dump 'sample.mem' from a compromised system.\n"
            "We’ll use Volatility 3 to investigate suspicious processes.\n"
            "Click 'Run pslist' to list all running processes, then follow the steps to analyze further."
        )

    @staticmethod
    def summary():
        return (
            "📝 Demo Summary\n"
            "1. pslist:\n"
            "   - Listed all running processes, identifying explorer.exe (PID 2496, 24 threads, 689 handles) and iexplore.exe (PID 1888, 14 threads, 641 handles).\n"
            "   - Significance: High thread and handle counts in explorer.exe may indicate injected code; iexplore.exe’s later creation suggests potential malware.\n\n"
            "2. malfind:\n"
            "   - Found RWX regions with shellcode in explorer.exe (0x1790000) and iexplore.exe (0xd60000).\n"
            "   - Significance: Identical shellcode suggests a common infection vector.\n\n"
            "3. pstree:\n"
            "   - Showed expected hierarchy (winlogon.exe → userinit.exe → explorer.exe → iexplore.exe).\n"
            "   - Significance: Shellcode indicates post-launch compromise.\n\n"
            "4. netscan:\n"
            "   - iexplore.exe made HTTP connections to suspicious IPs (e.g., 199.27.77.184).\n"
            "   - Significance: Potential malicious communication.\n\n"
            "5. dlllist:\n"
            "   - explorer.exe loads 7-zip.dll; iexplore.exe loads Adobe DLLs.\n"
            "   - Significance: Non-system paths are potential injection vectors.\n\n"
            "6. Memory Dump:\n"
            "   - Dumped shellcode from explorer.exe (0x1790000).\n"
            "   - Significance: Jump-heavy shellcode confirms infection.\n\n"
            "📋 Common Commands\n"
            "- List processes: python3 vol.py -f dump.mem windows.pslist\n"
            "- Detect injected code: python3 vol.py -f dump.mem windows.malfind\n"
            "- Show process tree: python3 vol.py -f dump.mem windows.pstree\n"
            "- Scan network: python3 vol.py -f dump.mem windows.netscan\n"
            "- List DLLs: python3 vol.py -f dump.mem windows.dlllist --pid <pid>\n"
            "- Dump memory: python3 vol.py -f dump.mem -o output_dir windows.malfind --pid <pid> --dump\n\n"
            "🎯 Use Cases\n"
            "- Malware Analysis, Incident Response, Forensic Investigation.\n\n"
            "Thank you for completing the Memory Forensics Demo!"
        )

# --- Main Application ---
class MainApp:
    def __init__(self, root, theme=None, apply_theme_callback=None):
        self.root = root
        self.root.title("Memory Forensics Demo")
        self.root.geometry(WINDOW_SIZE)
        self.current_screen = None
        self.theme = theme if theme else DEFAULT_THEME
        self.apply_theme_callback = apply_theme_callback
        self.last_width = 1280
        self.last_height = 720
        self.canvas_width = 1200
        self.canvas_height = 680
        self.current_step = 0
        self.steps = ["🖥️ Memory Forensics Basics", "🔬 Volatility 3 Overview", "🔧 Volatility 3 Plugins", 
                      "🕵️‍♂️ Volatility 3 Demo", "📝 Demo Summary & Quick Reference"]
        self.header_items = []
        self.button_items = []
        self.bg_image_id = None
        self.current_text_widget = None
        self.canvas_item_id = None
        self.bg_photo = None
        self.demo_frame = None
        self.step_count = 0
        self.total_steps = 6  # Match the demo steps (pslist, malfind, etc.)

        self.pages = [
            {"title": "🖥️ Memory Forensics Basics", "content": PageContent.memory_forensics_basics, "mode": "info"},
            {"title": "🔬 Volatility 3 Overview", "content": PageContent.volatility_overview, "mode": "info"},
            {"title": "🔧 Volatility 3 Plugins", "content": PageContent.volatility_plugins, "mode": "info"},
            {"title": "🕵️‍♂️ Volatility 3 Demo", "content": PageContent.volatility_demo, "mode": "demo"},
            {"title": "📝 Demo Summary & Quick Reference", "content": PageContent.summary, "mode": "info"}
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
        
        typewriter_effect(title_id, self.canvas, page['title'])

    def show_content_with_animation(self):
        self.root.update_idletasks()
        content_width = max(800, self.canvas_width - 100)
        content_height = max(400, self.canvas_height - 200)
        
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
        if self.current_step == 3:  # Volatility 3 Demo
            self.demo_frame = tk.Frame(self.root, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=0, y=0)
            self.demo_frame.lift()

            label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], font=(FONT, 18))
            label.place(relx=0.5, y=20, anchor='n')
            def typewriter_effect_label(label_widget, full_text, current_text="", index=0):
                if not label_widget.winfo_exists():
                    return
                if index < len(full_text):
                    current_text += full_text[index]
                    label_widget.config(text=current_text + "_")
                    label_widget.after(50, lambda: typewriter_effect_label(label_widget, full_text, current_text, index + 1))
                else:
                    label_widget.config(text=full_text)

            typewriter_effect_label(label, '🕵️‍♂️ Scenario: Investigate Suspicious Memory Dump')

            self.current_text_widget = tk.Text(self.demo_frame, bg=self.theme["terminal_bg"], fg=self.theme["terminal_fg"], 
                                              insertbackground=self.theme["fg"], font=(FONT, 12), wrap='word', width=120, height=18)
            self.current_text_widget.place(relx=0.5, rely=0.55, anchor='center')
            self.current_text_widget.config(state='disabled')
            self.current_text_widget.tag_configure("findings_tag", background="#FFFF99", foreground="#000000", font=(FONT, 12, "bold"))

            self.instruction_label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], 
                                             font=(FONT, 14), wraplength=1000, justify='center')
            self.instruction_label.place(relx=0.5, rely=0.25, anchor='center')

            button_frame = tk.Frame(self.demo_frame, bg=self.theme["bg"])
            button_frame.place(relx=0.5, rely=0.35, anchor='center')
            button_frame.pack_propagate(0)

            self.btn1 = tk.Button(button_frame, text='📋 Run pslist', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.run_pslist)
            self.btn1.grid(row=0, column=0, padx=5, pady=5)
            self.btn1.config(state='disabled')

            self.btn2 = tk.Button(button_frame, text='🔍 Run malfind', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.run_malfind)
            self.btn2.grid(row=0, column=1, padx=5, pady=5)
            self.btn2.config(state='disabled')

            self.btn3 = tk.Button(button_frame, text='🌳 Run pstree', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.run_pstree)
            self.btn3.grid(row=0, column=2, padx=5, pady=5)
            self.btn3.config(state='disabled')

            self.btn4 = tk.Button(button_frame, text='🌐 Run netscan', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.run_netscan)
            self.btn4.grid(row=0, column=3, padx=5, pady=5)
            self.btn4.config(state='disabled')

            self.btn5 = tk.Button(button_frame, text='📚 Run dlllist', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.run_dlllist)
            self.btn5.grid(row=0, column=4, padx=5, pady=5)
            self.btn5.config(state='disabled')

            self.btn6 = tk.Button(button_frame, text='💾 Dump Memory', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.dump_memory)
            self.btn6.grid(row=0, column=5, padx=5, pady=5)
            self.btn6.config(state='disabled')

            btn_clear = tk.Button(self.demo_frame, text='🗑️ Clear Terminal', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.clear_terminal)
            btn_clear.place(relx=0.5, rely=0.85, anchor='center')

            animate_instruction_decrypt(self.instruction_label, "You’ve received a memory dump 'sample.mem' from a compromised system.\n"
                                                            "We’ll use Volatility 3 to investigate suspicious processes.\n"
                                                            "Click 'Run pslist' to list all running processes.")
            self.btn1.config(state='normal')
            self.create_navigation_buttons()

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

    def run_pslist(self):
        self.btn1.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 1] Listing running processes with pslist...')
        append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.pslist')
        run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.pslist', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Identified explorer.exe (PID 2496, 24 threads, 689 handles, created 2014-01-08 02:18:17 UTC) and iexplore.exe (PID 1888, 14 threads, 641 handles, created 2014-01-08 03:20:24 UTC).\n'
                                                    'Why it matters: High thread and handle counts in explorer.exe may indicate additional activity, possibly from injected code. iexplore.exe’s later creation suggests it was launched after user login, potentially by malware.'),
            animate_instruction_decrypt(self.instruction_label, "The pslist output lists all processes. Look for explorer.exe (PID 2496) and iexplore.exe (PID 1888).\n"
                                                             "Click 'Run malfind' to check for injected code in these processes."),
            self.btn2.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def run_malfind(self):
        self.btn2.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 2] Scanning for injected code with malfind...')
        append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.malfind')
        run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.malfind', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Found RWX memory regions in explorer.exe (PID 2496) at 0x1790000 (shellcode: b0 00 eb 70...) and iexplore.exe (PID 1888) at 0xd60000 (same shellcode: b0 00 eb 70...). Additional RWX regions in explorer.exe at 0x5d70000 (shellcode starting with pushad: 60 5a d3 ad...) and iexplore.exe at 0x6fff0000 (shellcode: 64 74 72 52...).\n'
                                                    'Why it matters: Identical shellcode in both processes suggests a common infection vector, likely targeting iexplore.exe and spreading to explorer.exe. The jump-heavy pattern (eb) indicates evasion techniques.'),
            animate_instruction_decrypt(self.instruction_label, "The malfind output shows suspicious RWX regions with shellcode.\n"
                                                             "Click 'Run pstree' to check process relationships for anomalies."),
            self.btn3.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def run_pstree(self):
        self.btn3.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 3] Checking process hierarchy with pstree...')
        append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.pstree')
        run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.pstree', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] explorer.exe (PID 2496) has parent userinit.exe (PID 2368) and grandparent winlogon.exe (PID 552). iexplore.exe (PID 1888) has parent explorer.exe (PID 2496).\n'
                                                    'Why it matters: The hierarchy is expected, but shellcode from malfind suggests post-launch compromise via injection.'),
            animate_instruction_decrypt(self.instruction_label, "The pstree output shows process hierarchy. Look for unusual parents for PIDs 2496 or 1888.\n"
                                                             "Click 'Run netscan' to investigate network connections."),
            self.btn4.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def run_netscan(self):
        self.btn4.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 4] Scanning for network activity with netscan...')
        append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.netscan')
        run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.netscan', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] No connections for explorer.exe (PID 2496). iexplore.exe (PID 1888) made HTTP connections to 199.27.77.184:80, 199.27.79.196:80, 54.230.117.162:80, and others, plus a local UDP on 127.0.0.1:50461.\n'
                                                    'Why it matters: Multiple connections to 199.27.77.184 and 199.27.79.196 may indicate communication with a malicious domain. No non-standard ports like 4444, but IPs need checking.'),
            animate_instruction_decrypt(self.instruction_label, "The netscan output lists network connections. Check for suspicious IPs or ports tied to PIDs 2496 or 1888.\n"
                                                             "Click 'Run dlllist' to list loaded DLLs."),
            self.btn5.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def run_dlllist(self):
        self.btn5.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 5] Listing DLLs for explorer.exe (PID 2496) and iexplore.exe (PID 1888)...')
        append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.dlllist --pid 2496')
        run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.dlllist --pid 2496', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] explorer.exe (PID 2496) loads 7-zip.dll from C:\\Program Files\\7-Zip\\7-zip.dll, plus gdiplus.dll and comctl32.dll from WinSxS.\n'
                                                    'Why it matters: 7-zip.dll is a non-system path, a potential injection vector if tampered with.'),
            append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.dlllist --pid 1888'),
            run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" windows.dlllist --pid 1888', lambda stdout2, stderr2: (
                append_terminal_text(self.current_text_widget, stdout2 if stdout2 else stderr2),
                append_terminal_text(self.current_text_widget, '[FINDINGS] iexplore.exe (PID 1888) loads AcroIEHelperShim.dll and AcroIEHelper.dll from C:\\Program Files\\Common Files\\Adobe\\Acrobat\\ActiveX\\, plus iebrshim.dll from C:\\Windows\\AppPatch\\.\n'
                                                        'Why it matters: Adobe DLLs are common exploitation targets. AppPatch DLLs are less common and should be checked.'),
                animate_instruction_decrypt(self.instruction_label, "The dlllist output shows loaded DLLs. Look for DLLs in non-standard paths for PIDs 2496 and 1888.\n"
                                                                 "Click 'Dump Memory' to extract the suspicious shellcode."),
                self.btn6.config(state='normal')
            ), self.current_text_widget)
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def dump_memory(self):
        self.btn6.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 6] Dumping suspicious memory region from explorer.exe (PID 2496)...')
        append_terminal_text(self.current_text_widget, f'> python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" -o "{OUTPUT_DIR}" windows.malfind --pid 2496 --dump')
        run_command(f'python3 "{VOLATILITY_PATH}" -f "{MEMORY_DUMP_PATH}" -o "{OUTPUT_DIR}" windows.malfind --pid 2496 --dump', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Dumped shellcode to output_dir/vad_0x1790000.dmp (region 0x1790000, shellcode: b0 00 eb 70...). Additional dumps at 0x3190000 (mostly zeros) and 0x5d70000 (shellcode: 60 5a d3 ad...).\n'
                                                    'Why it matters: The primary dump (vad_0x1790000.dmp) contains jump-heavy shellcode, likely a staged payload. Analyze it to reveal malware behavior.'),
            animate_instruction_decrypt(self.instruction_label, "The memory dump contains the suspicious shellcode from explorer.exe.\n"
                                                             "Proceed to the summary."),
            self.create_navigation_buttons()
        ), self.current_text_widget)

    def clear_terminal(self):
        self.current_text_widget.config(state='normal')
        self.current_text_widget.delete(1.0, tk.END)
        self.current_text_widget.config(state='disabled')
        self.setup_demo_frame()

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