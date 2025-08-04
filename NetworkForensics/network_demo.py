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

# File paths relative to the script's directory
SCRIPT_DIR = Path(__file__).parent
PCAP_FILE = SCRIPT_DIR / 'new_sample3.pcap'
OUTPUT_DIR = SCRIPT_DIR / 'output_dir'
IMAGE_PATH = SCRIPT_DIR / 'wireshark.png'

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# --- Utility Functions ---
def append_terminal_text(text_widget, message):
    text_widget.config(state='normal')
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_text = f"[{timestamp}] {message}\n"
    text_widget.insert(tk.END, full_text)
    text_widget.see(tk.END)
    text_widget.after(10, lambda: text_widget.see(tk.END))
    text_widget.update_idletasks()
    if message.startswith('[FINDINGS]'):
        start_idx = text_widget.index(tk.END + "-2l")
        end_idx = text_widget.index(tk.END + "-1c")
        text_widget.tag_add("findings_tag", start_idx, end_idx)
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
    def network_forensics_basics():
        return (
            "🌐 Network Forensics Basics\n"
            "Network forensics involves analyzing network traffic to identify suspicious activity, such as intrusions, malware communication, or data exfiltration.\n\n"
            "📦 Why Analyze Packet Captures?\n"
            "Packet captures (PCAPs) record all network activity, revealing who’s talking to whom, what services are used, and any anomalies like large data transfers or unusual DNS traffic.\n\n"
            "🛠️ Use Cases\n"
            "- Detecting malware command-and-control (C2) traffic.\n"
            "- Identifying unauthorized access or data leaks.\n"
            "- Investigating network performance issues.\n\n"
            "Next, let’s dive into Wireshark, a powerful tool for network forensics!"
        )

    @staticmethod
    def wireshark_overview():
        return (
            "🔬 Wireshark Overview\n"
            "Wireshark is an open-source packet analyzer used for network troubleshooting, analysis, and forensics.\n\n"
            "⚡ Key Features\n"
            "- Captures and displays packets in real-time or from PCAP files.\n"
            "- Filters packets by IP, port, protocol, and more.\n"
            "- Analyzes TCP/UDP traffic, DNS queries, and external communications.\n\n"
            "🔍 Why Use It?\n"
            "It helps uncover unusual traffic, such as large TCP data transfers or potential DNS tunneling, by examining IPs, ports, protocols, and packet details.\n"
            "Next, we’ll explore key Wireshark features for our analysis."
        )

    @staticmethod
    def wireshark_features():
        return (
            "🔧 Wireshark Features\n"
            "Wireshark provides powerful tools for network analysis. Here’s what we’ll focus on:\n\n"
            "- Packet Listing: Use tshark to list packets and extract basic info (IP, port, protocol).\n"
            "- Filters: Filter by IPs, ports, and protocols to isolate suspicious traffic.\n"
            "- TCP Analysis: Examine TCP flags and packet lengths for anomalies.\n"
            "- DNS Inspection: Analyze UDP traffic for potential DNS tunneling.\n"
            "- Geolocation: Identify the location of external IPs to detect potential C2 servers.\n\n"
            "🛠️ How They Work\n"
            "These features parse packet data to reveal communication patterns and anomalies.\n\n"
            "Let’s analyze a suspicious PCAP file with these tools!"
        )

    @staticmethod
    def network_forensics_demo():
        return (
            "🕵️‍♂️ Scenario: Analyze Suspicious Packet Capture\n"
            "You’ve received a packet capture 'new_sample3.pcap' from a network.\n"
            "We’ll use Wireshark (via tshark) to analyze it for suspicious activity.\n"
            "Click 'List Packets' to start by listing all packets in the capture."
        )

    @staticmethod
    def summary():
        return (
            "📝 Demo Summary\n"
            "1. List Packets:\n"
            "   - Listed 1000 packets in new_sample3.pcap using tshark. Sample: Packet 1: 10.0.2.15 -> 10.0.2.3, Protocol 17 (UDP), Length 97 bytes.\n"
            "   - Significance: Provided a high-level view of the traffic, showing a mix of local and external communications.\n\n"
            "2. Analyze IPs:\n"
            "   - Top talkers: 10.0.2.15 <-> 142.251.186.106 (308 packets), 10.0.2.15 <-> 199.201.110.204 (186 packets), 10.0.2.15 <-> 10.0.2.3 (48 packets).\n"
            "   - Significance: Significant external communication with 142.251.186.106 and 199.201.110.204, plus local DNS-like traffic with 10.0.2.3.\n\n"
            "3. Check Ports & Protocols:\n"
            "   - Protocols: TCP (907 packets), UDP (91 packets). UDP: 10.0.2.15 -> 10.0.2.3 (port 53), likely DNS. TCP: 10.0.2.15 <-> 142.251.186.106 (port 443), likely HTTPS.\n"
            "   - Significance: DNS traffic and HTTPS sessions are common, but large UDP packets (1399 bytes) to external IPs suggest potential tunneling.\n\n"
            "4. Analyze TCP Flags & Lengths:\n"
            "   - Largest packet: Packet 842: 199.201.110.204 -> 10.0.2.15, Length 47574 bytes, TCP Flags: ACK. Packet 453: 142.251.186.106 -> 10.0.2.15, Length 44450 bytes, TCP Flags: ACK.\n"
            "   - Significance: Large TCP packets suggest significant data transfers, potentially legitimate or suspicious.\n\n"
            "5. Geolocation:\n"
            "   - IP 199.201.110.204: Likely a CDN or hosting provider. 142.251.186.106 belongs to Google.\n"
            "   - Significance: Large data transfers from 199.201.110.204 require further investigation.\n\n"
            "📋 Common Wireshark/tshark Commands\n"
            "- List packets: tshark -r file.pcap -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto\n"
            "- Filter by IP: tshark -r file.pcap -Y \"ip.addr == 10.0.2.15\"\n"
            "- Analyze ports: tshark -r file.pcap -T fields -e tcp.srcport -e tcp.dstport\n"
            "- Check TCP flags: tshark -r file.pcap -T fields -e tcp.flags\n"
            "- Geolocation: curl ipinfo.io/<IP>\n\n"
            "🎯 Use Cases\n"
            "- Security Analysis, Network Troubleshooting, Threat Hunting.\n\n"
            "Thank you for completing the Network Forensics Demo!"
        )

    @staticmethod
    def wireshark_gui():
        return (
            "📝 Wireshark GUI Overview\n"
            "During this demo, we focused primarily on tshark, the terminal version of Wireshark, to analyze 'new_sample3.pcap'.\n\n"
            "There is also a Wireshark GUI available for more detailed analysis, which may be user-friendly for beginners.\n"
            "To open the GUI, run: wireshark new_sample3.pcap\n\n"
            "The GUI offers:\n"
            "- Packet list pane: Displays all packets with details like time, source, destination, protocol, and length.\n"
            "- Packet details pane: Shows detailed header and payload info.\n"
            "- Packet bytes pane: Displays raw data in hex and ASCII.\n"
            "- Filters: Apply display filters for IPs, ports, protocols, etc.\n\n"
            "Below is a screenshot of the Wireshark GUI analyzing new_sample3.pcap:\n"
        )

# --- Main Application ---
class MainApp:
    def __init__(self, root, theme=None, apply_theme_callback=None):
        self.root = root
        self.root.title("Network Forensics Demo")
        self.root.geometry(WINDOW_SIZE)
        self.current_screen = None
        self.theme = theme if theme else DEFAULT_THEME
        self.apply_theme_callback = apply_theme_callback
        self.last_width = 1280
        self.last_height = 720
        self.canvas_width = 1200
        self.canvas_height = 680
        self.current_step = 0
        self.steps = ["🌐 Network Forensics Basics", "🔬 Wireshark Overview", "🔧 Wireshark Features", 
                      "🕵️‍♂️ Network Forensics Demo", "📝 Demo Summary & Quick Reference", "📝 Wireshark GUI Overview"]
        self.header_items = []
        self.button_items = []
        self.bg_image_id = None
        self.current_text_widget = None
        self.canvas_item_id = None
        self.bg_photo = None
        self.demo_frame = None
        self.step_count = 0
        self.total_steps = 5  # Match the demo steps (List Packets, etc.)

        self.pages = [
            {"title": "🌐 Network Forensics Basics", "content": PageContent.network_forensics_basics, "mode": "info"},
            {"title": "🔬 Wireshark Overview", "content": PageContent.wireshark_overview, "mode": "info"},
            {"title": "🔧 Wireshark Features", "content": PageContent.wireshark_features, "mode": "info"},
            {"title": "🕵️‍♂️ Network Forensics Demo", "content": PageContent.network_forensics_demo, "mode": "demo"},
            {"title": "📝 Demo Summary & Quick Reference", "content": PageContent.summary, "mode": "info"},
            {"title": "📝 Wireshark GUI Overview", "content": PageContent.wireshark_gui, "mode": "info"}
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
        if self.current_step == 3:  # Network Forensics Demo
            self.demo_frame = tk.Frame(self.root, bg=self.theme["bg"], width=self.canvas_width, height=self.canvas_height)
            self.demo_frame.place(x=0, y=0)
            self.demo_frame.lift()

            label = tk.Label(self.demo_frame, text='', fg=self.theme["button_fg"], bg=self.theme["bg"], font=(FONT, 18))
            label.place(relx=0.5, y=20, anchor='n')
            typewriter_effect_label(label, '🕵️‍♂️ Scenario: Analyze Suspicious Packet Capture')

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

            self.btn1 = tk.Button(button_frame, text='📋 List Packets', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.list_packets)
            self.btn1.grid(row=0, column=0, padx=5, pady=5)
            self.btn1.config(state='disabled')

            self.btn2 = tk.Button(button_frame, text='🌐 Analyze IPs', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.analyze_ips)
            self.btn2.grid(row=0, column=1, padx=5, pady=5)
            self.btn2.config(state='disabled')

            self.btn3 = tk.Button(button_frame, text='🔌 Check Ports & Protocols', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.check_ports_protocols)
            self.btn3.grid(row=0, column=2, padx=5, pady=5)
            self.btn3.config(state='disabled')

            self.btn4 = tk.Button(button_frame, text='📏 Analyze TCP Flags & Lengths', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.analyze_tcp_flags_lengths)
            self.btn4.grid(row=0, column=3, padx=5, pady=5)
            self.btn4.config(state='disabled')

            self.btn5 = tk.Button(button_frame, text='🌍 Geolocation', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.geolocation)
            self.btn5.grid(row=0, column=4, padx=5, pady=5)
            self.btn5.config(state='disabled')

            btn_clear = tk.Button(self.demo_frame, text='🗑️ Clear Terminal', bg=self.theme["button_bg"], fg=self.theme["button_fg"], 
                                 font=(FONT, 10), width=20, command=self.clear_terminal)
            btn_clear.place(relx=0.5, rely=0.85, anchor='center')

            animate_instruction_decrypt(self.instruction_label, "You’ve received a packet capture 'new_sample3.pcap' from a network.\n"
                                                            "We’ll use Wireshark (via tshark) to analyze it for suspicious activity.\n"
                                                            "Click 'List Packets' to start by listing all packets in the capture.")
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

    def list_packets(self):
        self.btn1.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 1] Listing packets in the capture file...')
        append_terminal_text(self.current_text_widget, f'> tshark -r "{PCAP_FILE}" -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e frame.len')
        run_command(f'tshark -r "{PCAP_FILE}" -T fields -e frame.number -e ip.src -e ip.dst -e ip.proto -e frame.len', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Identified 1000 packets. Sample: Packet 1: 10.0.2.15 -> 10.0.2.3, Protocol 17 (UDP), Length 97 bytes.\n'
                                                    'Why it matters: This gives us a high-level view of the traffic, showing a mix of local and external communications.'),
            animate_instruction_decrypt(self.instruction_label, "The packet list shows all captured packets. Look for communication patterns.\n"
                                                             "Click 'Analyze IPs' to identify who’s talking to whom."),
            self.btn2.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def analyze_ips(self):
        self.btn2.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 2] Analyzing source and destination IPs...')
        append_terminal_text(self.current_text_widget, f'> tshark -r "{PCAP_FILE}" -T fields -e ip.src -e ip.dst | sort | uniq -c')
        run_command(f'tshark -r "{PCAP_FILE}" -T fields -e ip.src -e ip.dst | sort | uniq -c', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Top talkers: 10.0.2.15 <-> 142.251.186.106 (308 packets), 10.0.2.15 <-> 199.201.110.204 (186 packets), 10.0.2.15 <-> 10.0.2.3 (48 packets).\n'
                                                    'Why it matters: Significant external communication with 142.251.186.106 and 199.201.110.204, plus local DNS-like traffic with 10.0.2.3.'),
            animate_instruction_decrypt(self.instruction_label, "The IP analysis shows communication pairs, including external IPs.\n"
                                                             "Click 'Check Ports & Protocols' to examine services and protocols."),
            self.btn3.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def check_ports_protocols(self):
        self.btn3.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 3] Checking ports and protocols...')
        append_terminal_text(self.current_text_widget, f'> tshark -r "{PCAP_FILE}" -T fields -e ip.src -e ip.dst -e ip.proto -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport')
        run_command(f'tshark -r "{PCAP_FILE}" -T fields -e ip.src -e ip.dst -e ip.proto -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Protocols: TCP (907 packets), UDP (91 packets). UDP: 10.0.2.15 -> 10.0.2.3 (port 53), likely DNS. TCP: 10.0.2.15 <-> 142.251.186.106 (port 443), likely HTTPS.\n'
                                                    'Why it matters: DNS traffic and HTTPS sessions are common, but large UDP packets (1399 bytes) to external IPs suggest potential tunneling.'),
            animate_instruction_decrypt(self.instruction_label, "The ports and protocols reveal services in use, including DNS and HTTPS.\n"
                                                             "Click 'Analyze TCP Flags & Lengths' to investigate TCP traffic and packet sizes."),
            self.btn4.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def analyze_tcp_flags_lengths(self):
        self.btn4.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 4] Analyzing TCP flags and packet lengths...')
        append_terminal_text(self.current_text_widget, f'> tshark -r "{PCAP_FILE}" -T fields -e frame.number -e ip.src -e ip.dst -e tcp.flags -e frame.len | sort -k 5 -nr')
        run_command(f'tshark -r "{PCAP_FILE}" -T fields -e frame.number -e ip.src -e ip.dst -e tcp.flags -e frame.len | sort -k 5 -nr', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] Largest packet: Packet 842: 199.201.110.204 -> 10.0.2.15, Length 47574 bytes, TCP Flags: ACK. Packet 453: 142.251.186.106 -> 10.0.2.15, Length 44450 bytes, TCP Flags: ACK. Many small packets (54 bytes) are TCP ACKs.\n'
                                                    'Why it matters: Large TCP packets suggest significant data transfers, potentially legitimate or suspicious.'),
            animate_instruction_decrypt(self.instruction_label, "The TCP analysis shows large data transfers from external IPs.\n"
                                                             "Click 'Geolocation' to identify the location of these IPs."),
            self.btn5.config(state='normal')
        ), self.current_text_widget)
        self.create_navigation_buttons()

    def geolocation(self):
        self.btn5.config(state='disabled')
        self.step_count += 1
        append_terminal_text(self.current_text_widget, '[STEP 5] Performing geolocation on external IPs...')
        append_terminal_text(self.current_text_widget, f'> curl ipinfo.io/199.201.110.204')
        run_command(f'curl ipinfo.io/199.201.110.204', lambda stdout, stderr: (
            append_terminal_text(self.current_text_widget, stdout if stdout else stderr),
            append_terminal_text(self.current_text_widget, '[FINDINGS] IP 199.201.110.204: Geolocation data retrieved (likely a CDN or hosting provider). 142.251.186.106 belongs to Google (AS15169), likely a legitimate service.\n'
                                                    'Why it matters: Large data transfers from 199.201.110.204 could be legitimate or suspicious. Further investigation into packet content is needed.'),
            animate_instruction_decrypt(self.instruction_label, "Geolocation helps identify potential C2 servers or legitimate services.\n"
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