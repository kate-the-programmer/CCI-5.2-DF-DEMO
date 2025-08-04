import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os
import random

# Constants
FONT = 'Courier'
FONT_SIZE = 12

# Updated theme to match the image style with more colors
DEFAULT_THEME = {
    "bg": "#2C2F33",           # Dark gray background
    "fg": "#00FF00",           # Bright green text to match the image
    "button_bg": "#40444B",    # Dark blue button background
    "button_fg": "#00FF00",    # Green button text
    "button_active_bg": "#7289DA",  # Vibrant blue on hover
    "canvas_bg": "#2C2F33",    # Dark gray canvas background to match
    "block_outline": "#B0B0B0",  # Light gray outline
    "block_text": "#FFFFFF",   # White text in blocks
    "block_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5"],  # Expanded color palette
    "parity_color": "#7D7D9C",  # Muted purple for parity
    "terminal_bg": "#2C2F33",   # Same as canvas_bg
    "terminal_fg": "#00FF00",   # Green text
    "active_fg": "#FFFFFF",     # For active states
    "disabled_fg": "#666666"    # For disabled states
}

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
            continue
        elif display_text[i] not in '\n ':
            display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')

    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", ''.join(display_text))
    widget.config(state="disabled")
    widget.after(50, lambda: decrypt_animation(widget, original_text, step + 1))


class RAIDVisualizationApp:
    def __init__(self, parent, theme=None):
        self.parent = parent
        self.theme = theme if theme else DEFAULT_THEME
        self.button_items = []  # For storing button canvas items

        parent.title("RAID Visualization")
        parent.geometry("1200x800")  # Default to 1200x800
        parent.configure(bg=self.theme["bg"])
        parent.update_idletasks()  # Ensure window dimensions are set

        self.SAMPLE_FILE = "sample.txt"
        if not os.path.exists(self.SAMPLE_FILE):
            with open(self.SAMPLE_FILE, "w") as f:
                f.write("This is a sample file to demonstrate RAID configurations with 64 bytes of data.")

        with open(self.SAMPLE_FILE, "rb") as f:
            self.file_data = f.read()
            print(f"File size: {len(self.file_data)} bytes")

        self.main_frame = tk.Frame(parent, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.pil_font = ImageFont.load_default()  # Will be overridden with larger font in create_raid_image
        self.block_coords = {}
        self.bg_image_id = None
        self.last_width = 1200  # Initialize with default width
        self.last_height = 800  # Initialize with default height
        self.canvas_width = 1160  # Adjusted for padding (1200 - 40)
        self.canvas_height = 700  # Initial height, will adjust dynamically
        self.current_step = 0  # Track the current RAID configuration (0-3)
        self.steps = ["RAID 0", "RAID 1", "RAID 5", "RAID 1+0"]  # Define steps

        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_width, height=self.canvas_height, bg=self.theme["canvas_bg"], highlightthickness=0)
        self.canvas.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)  # Reduced padding for more space
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.parent.bind("<Configure>", self.on_window_resize)

        self.create_navigation_buttons()  # Initialize navigation buttons
        self.create_background()
        self.parent.after(100, self.update_step)  # Delay initial draw to ensure window is ready

    def apply_theme(self, theme):
        self.theme = theme
        self.parent.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])
        self.canvas.configure(bg=theme["canvas_bg"])
        for widget in self.main_frame.winfo_children():
            self._update_widget_theme(widget, theme)
        self.create_background()
        self.update_step()

    def _update_widget_theme(self, widget, theme):
        if isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        elif isinstance(widget, tk.Canvas):
            widget.configure(bg=theme["canvas_bg"])
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=theme["bg"])
        for child in widget.winfo_children():
            self._update_widget_theme(child, theme)

    def hex_to_rgb(self, hex_color):
        if hex_color.startswith('#'):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        color_map = {"gray": (128, 128, 128), "black": (0, 0, 0), "white": (255, 255, 255)}
        return color_map.get(hex_color.lower(), (0, 0, 0))

    def draw_simple_block(self, draw, x_start, y, width, height, fill_color, text, text_color=None, raid_type=None, disk=None, segment=None):
        if text_color is None:
            text_color = self.theme["block_text"]
        draw.rounded_rectangle([x_start, y, x_start + width - 10, y + height], radius=15, fill=fill_color, outline=self.theme["block_outline"], width=2)
        text_pos = (x_start + width / 2, y + height / 2)
        draw.text(text_pos, text, fill=text_color, font=ImageFont.load_default().font_variant(size=24), anchor="mm")
        self.block_coords[(x_start, y, x_start + width - 10, y + height)] = (raid_type, disk, segment)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        for coords, (raid_type, disk, segment) in self.block_coords.items():
            if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                self.show_detail_window(raid_type, disk, segment)
                break

    def show_detail_window(self, raid_type, disk, segment):
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Details for {segment}")
        detail_window.geometry("600x400")
        detail_window.configure(bg=self.theme["bg"])
        text = tk.Text(detail_window, height=20, width=70, font=(FONT, FONT_SIZE), bg=self.theme["canvas_bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"])
        text.pack(pady=10, padx=10)

        segment_size = 10
        if raid_type == "RAID 0":
            text.insert(tk.END, f"RAID 0 - Striping Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "Data is split across 2 drives for speed.\n")
            file_num, seg = segment[4], segment[-1]
            file_idx = int(file_num) - 1
            start = file_idx * segment_size + (0 if seg == 'a' else segment_size)
            data_segment = self.file_data[start:start + segment_size]
            text.insert(tk.END, f"File {file_num}: Segment {seg} on Disk {disk}\n")
            text.insert(tk.END, f"Sample Data: {data_segment.hex()}\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + (ord(seg) - ord('a')) * 0x100:04x}\n")
            text.insert(tk.END, "No redundancy; fails if any disk dies.\n")
        elif raid_type == "RAID 1":
            text.insert(tk.END, f"RAID 1 - Mirroring Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "Data is duplicated across 2 drives.\n")
            file_num = segment.split(" ")[1]
            text.insert(tk.END, f"File {file_num} mirrored on Disks 1 and 2.\n")
            text.insert(tk.END, f"Sample Data: {self.file_data[:segment_size].hex()}\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000:04x}\n")
            text.insert(tk.END, "Survives 1 disk failure.\n")
        elif raid_type == "RAID 5":
            if segment.startswith("P"):
                text.insert(tk.END, f"RAID 5 - Parity Detail for {segment} on Disk {disk}\n")
                stripe = int(segment[1]) - 1
                text.insert(tk.END, f"Parity for Stripe {stripe+1}:\n")
                if stripe == 0:
                    parity = bytes(a ^ b for a, b in zip(self.file_data[:10], self.file_data[10:20]))
                    text.insert(tk.END, f"Parity (F1a XOR F1b): {parity.hex()}\n")
                elif stripe == 1:
                    parity = bytes(a ^ b for a, b in zip(self.file_data[20:30], self.file_data[30:40]))
                    text.insert(tk.END, f"Parity (F2a XOR F2b): {parity.hex()}\n")
                text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + 0x200:04x}\n")
                text.insert(tk.END, "Survives 1 disk failure with degraded performance.\n")
            else:
                text.insert(tk.END, f"RAID 5 - Data Detail for {segment} on Disk {disk}\n")
                file_num, seg = segment.split(" ")[0][1], segment.split(" ")[0][2]
                file_idx = int(file_num) - 1
                seg_idx = ord(seg) - ord('a')
                start = file_idx * 20 + seg_idx * 10
                data_segment = self.file_data[start:start + 10]
                text.insert(tk.END, f"File {file_num}: Segment {seg}\n")
                text.insert(tk.END, f"Sample Data: {data_segment.hex()}\n")
                text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + 0x100 + seg_idx * 0x100:04x}\n")
        elif raid_type == "RAID 1+0":
            text.insert(tk.END, f"RAID 1+0 - Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "Data is striped across mirrors for both speed and redundancy.\n")
            file_num, seg = segment[4], segment[-1]
            file_idx = int(file_num) - 1
            start = file_idx * 20 + (0 if seg == 'a' else 10)
            data_segment = self.file_data[start:start + 10]
            text.insert(tk.END, f"File {file_num}: Segment {seg} mirrored on disk pair {1 if disk <= 2 else 2}\n")
            text.insert(tk.END, f"Sample Data: {data_segment.hex()}\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + (ord(seg) - ord('a')) * 0x100:04x}\n")
            text.insert(tk.END, "Survives 1 disk failure per mirror pair.\n")

    def create_background(self, width=None, height=None):
        if width is None:
            width = self.canvas.winfo_width()
        if height is None:
            height = self.canvas.winfo_height()
        if width <= 0 or height <= 0:  # Prevent invalid dimensions
            width, height = 1160, 660  # Updated fallback height
        bg_image = Image.new('RGB', (width, height), self.theme["canvas_bg"])
        draw = ImageDraw.Draw(bg_image)
        for i in range(0, width, 10):  # Reduced step to show more background pattern
            for j in range(0, height, 10):  # Reduced step to show more background pattern
                if random.random() > 0.7:  # Increased density to make background more visible
                    char = random.choice(['0', '1', '█', '▓', '▒', '░'])
                    draw.text((i, j), char, fill=self.theme["disabled_fg"])
        if self.bg_image_id:
            self.canvas.delete(self.bg_image_id)
        self.bg_image_id = self.canvas.create_image(0, 0, anchor="nw", image=ImageTk.PhotoImage(bg_image))
        self.canvas.image = ImageTk.PhotoImage(bg_image)  # Keep a reference

    def typewriter_effect(self, text_id, full_text, current_text="", index=0):
        if index < len(full_text):
            current_text += full_text[index]
            self.canvas.itemconfig(text_id, text=current_text + "_")
            self.parent.after(50, lambda: self.typewriter_effect(text_id, full_text, current_text, index + 1))
        else:
            self.canvas.itemconfig(text_id, text=full_text)

    def on_window_resize(self, event):
        """Handle window resize events to update background and navigation"""
        if event.widget == self.parent:
            self.parent.after(100, self.update_background_and_canvas)

    def update_background_and_canvas(self):
        """Update background and canvas size when window is resized"""
        try:
            self.parent.update_idletasks()
            actual_width = self.parent.winfo_width()
            actual_height = self.parent.winfo_height()
            
            if (hasattr(self, 'last_width') and hasattr(self, 'last_height') and
                abs(actual_width - self.last_width) < 50 and 
                abs(actual_height - self.last_height) < 50):
                return
            
            self.last_width = actual_width
            self.last_height = actual_height
            
            # Reserve less space for navigation buttons (e.g., 150px) to allow more canvas height
            canvas_width = max(1160, actual_width - 40)
            canvas_height = max(660, actual_height - 150)  # Reduced reservation
            
            self.canvas.config(width=canvas_width, height=canvas_height)
            self.canvas_width = canvas_width
            self.canvas_height = canvas_height
            
            self.create_background(canvas_width, canvas_height)
            self.create_navigation_buttons()  # Recreate buttons on resize
            self.update_step()
            
        except Exception as e:
            print(f"Error updating background: {e}")

    def update_step(self):
        """Update the display based on the current step"""
        self.canvas.delete("all")
        self.create_background()
        if self.current_step == 0:
            img = self.create_raid_image("RAID 0")
            title = "RAID 0 - Striping"
        elif self.current_step == 1:
            img = self.create_raid_image("RAID 1")
            title = "RAID 1 - Mirroring"
        elif self.current_step == 2:
            img = self.create_raid_image("RAID 5")
            title = "RAID 5 - Striping with Parity"
        elif self.current_step == 3:
            img = self.create_raid_image("RAID 1+0")
            title = "RAID 1+0 - Mirroring and Striping"
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img
                # Define the description for the current RAID type
        desc_map = {
            0: ("RAID 0: Striping - Data is split across multiple disks to increase read/write speeds. "
                "Use cases include high-performance computing and video editing. "
                "It offers no fault tolerance—failure of one disk results in data loss."),
            1: ("RAID 1: Mirroring - Identical data is written to two disks for redundancy. "
                "Good for critical data but doubles storage costs."),
            2: ("RAID 5: Striping with Parity - Balances speed and redundancy across 3+ disks. "
                "Can survive one disk failure."),
            3: ("RAID 1+0: Combines mirroring and striping for both speed and redundancy. "
                "Requires at least 4 disks and halves usable space.")
        }
        desc_text = desc_map.get(self.current_step, "")

        # Create and animate text widget for description
        text_widget = tk.Text(self.canvas, height=6, wrap='word',
                            bg=self.theme["terminal_bg"],
                            fg=self.theme["terminal_fg"],
                            font=('Courier', 14),
                            insertbackground=self.theme["fg"],
                            relief='flat',
                            borderwidth=0)
        text_window = self.canvas.create_window(self.canvas_width // 2, 200 + self.canvas_height // 2,
                                                window=text_widget, width=self.canvas_width - 100)
        decrypt_animation(text_widget, desc_text)


        title_id = self.canvas.create_text(self.canvas_width // 2, 50, text="", font=('Courier New', 36, 'bold'), fill=self.theme["fg"])
        self.typewriter_effect(title_id, title)
        self.create_navigation_buttons()  # Update buttons after step change

    def next_step(self):
        """Move to the next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step()

    def previous_step(self):
        """Move to the previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def complete_demo(self):
        """Fade out and close the window"""
        def fade(step):
            if step >= 0:
                alpha = int(0x2C2F33 * (step / 10))  # Simplified fade using background color
                self.canvas.config(bg=f'#{alpha:06x}')
                self.parent.after(50, lambda: fade(step - 1))
            else:
                self.parent.destroy()
        fade(10)

    def create_navigation_buttons(self):
        """Create styled navigation buttons with cyber aesthetic"""
        theme = self.theme
        for item in self.button_items:
            self.canvas.delete(item)
        self.button_items = []
        self.parent.update_idletasks()
        canvas_width = max(1160, self.canvas_width)
        canvas_height = max(660, self.canvas_height)  # Use dynamic canvas height
        button_y = self.canvas.winfo_y() + self.canvas_height + 50  # Position below canvas
        center_x = canvas_width // 2

        if self.current_step > 0:
            back_btn = tk.Button(self.parent,
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

        next_btn = tk.Button(self.parent,
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

    def create_raid_image(self, raid_type):
        try:
            # Dynamically calculate height based on content
            title_height = 100  # Space for title (y=50 + padding)
            block_height_total = 2 * (80 + 30)  # Reduced block height to 80 and spacing to 30
            desc_height = 150  # Estimated height for description (4-5 lines x ~30px each)
            hint_height = 50   # Space for hint
            total_content_height = title_height + block_height_total + desc_height + hint_height
            height = max(total_content_height, self.canvas.winfo_height() - 150)  # Reserve 150px for buttons
            width = self.canvas.winfo_width()

            img = Image.new("RGB", (width, height), self.theme["canvas_bg"])
            draw = ImageDraw.Draw(img)
            self.block_coords = {}
            ssd_width = 200  # Increased block width
            ssd_spacing = 50  # Increased spacing
            colors = self.theme["block_colors"]
            block_height = 80  # Reduced block height
            num_files = 2

            if raid_type == "RAID 0":
                num_drives = 2
            elif raid_type == "RAID 1":
                num_drives = 2
            elif raid_type == "RAID 5":
                num_drives = 3
            elif raid_type == "RAID 1+0":
                num_drives = 4

            # Calculate vertical starting point to center content under title area
            y_start = 100  # Start below the title area (title is at y=50)

            # Define center_x for centering elements
            center_x = width // 2

            # Disk labels
            disk_y = y_start
            for i in range(num_drives):
                x_start = center_x - (num_drives * (ssd_width + ssd_spacing) / 2) + i * (ssd_width + ssd_spacing)
                disk_text = f"Disk {i + 1}"
                disk_bbox = draw.textbbox((0, 0), disk_text, font=ImageFont.load_default().font_variant(size=20))
                disk_width = disk_bbox[2] - disk_bbox[0]
                draw.text((x_start + ssd_width / 2 - disk_width / 2, disk_y), disk_text, fill=self.theme["fg"], font=ImageFont.load_default().font_variant(size=20))

            # Blocks
            block_y_start = disk_y + 50
            for j in range(num_files):
                for i in range(num_drives):
                    if raid_type == "RAID 0":
                        segment = f"File{j+1}{'a' if i == 0 else 'b'}"
                        # Assign unique color per file, same for split segments
                        fill_color = colors[j]  # File1 uses colors[0], File2 uses colors[1]
                    elif raid_type == "RAID 1":
                        segment = f"File {j+1}"
                        fill_color = colors[j]  # Use color for File1 and File2
                    elif raid_type == "RAID 5":
                        if i == j % num_drives:
                            segment = f"P{j+1}"
                            fill_color = self.theme["parity_color"]
                        else:
                            segment_idx = 0 if i < (j % num_drives) else i-1
                            segment = f"F{j+1}{'a' if segment_idx == 0 else 'b'}"
                            fill_color = colors[j]
                    elif raid_type == "RAID 1+0":
                        mirror_group = i // 2
                        segment = f"File{j+1}{'a' if mirror_group == 0 else 'b'}"
                        fill_color = colors[j] if j == 0 else colors[1]  # Alternate colors for rows

                    x_start = center_x - (num_drives * (ssd_width + ssd_spacing) / 2) + i * (ssd_width + ssd_spacing)
                    fill_color = fill_color if 'fill_color' in locals() else colors[j % len(colors)]
                    self.draw_simple_block(draw, 
                                          x_start=x_start, 
                                          y=block_y_start + j * (block_height + 30), 
                                          width=ssd_width, 
                                          height=block_height, 
                                          fill_color=fill_color, 
                                          text=segment,
                                          raid_type=raid_type, 
                                          disk=i+1, 
                                          segment=segment)

            # # Descriptive text and instruction
            desc_y = block_y_start + (num_files * (block_height + 30))
            # if raid_type == "RAID 0":
            #     desc_text = ("RAID 0: Striping - Data is split across multiple disks to increase read/write speeds. \n"
            #                  "Use cases include high-performance computing and video editing where speed is critical. \n"
            #                  "Performance is excellent for speed with no overhead, but it offers no fault tolerance—failure of one disk results in data loss. \n"
            #                  "It requires at least 2 disks and is cost-effective but risky due to lack of redundancy.\n")
            # elif raid_type == "RAID 1":
            #     desc_text = ("RAID 1: Mirroring - Identical data is written to two or more disks for redundancy.\n"
            #                  "Use cases include critical data storage like databases and financial records. \n"
            #                  "Performance is moderate, with read speeds potentially doubled but write speeds limited by mirroring. \n"
            #                  "It tolerates a single disk failure and requires at least 2 disks, doubling storage costs.\n")
            # elif raid_type == "RAID 5":
            #     desc_text = ("RAID 5: Striping with Parity - Data and parity information are distributed across three or more disks. \n"
            #                  "Use cases include file servers and enterprise storage needing a balance of performance and redundancy. \n"
            #                  "Performance offers good read speeds and decent write speeds, with fault tolerance for one disk failure. \n"
            #                  "It requires at least 3 disks, providing (N-1) capacity where N is the number of disks.\n")
            # elif raid_type == "RAID 1+0":
            #     desc_text = ("RAID 1+0: Mirroring and Striping - Data is mirrored in pairs and then striped across the pairs for speed and redundancy. \n"
            #                  "Use cases include high-availability systems like transaction processing and real-time applications. \n"
            #                  "Performance is excellent with high read/write speeds, and it tolerates multiple disk failures as long as one disk per mirror pair remains. \n"
            #                  "It requires at least 4 disks, with storage capacity halved due to mirroring.\n")
            # desc_bbox = draw.textbbox((0, 0), desc_text, font=ImageFont.load_default().font_variant(size=20))
            # desc_width = desc_bbox[2] - desc_bbox[0]
            # draw.text((center_x - desc_width / 2, desc_y), desc_text, fill=self.theme["fg"], font=ImageFont.load_default().font_variant(size=20))
            # #print(f"Description set at y={desc_y}, height={height}, text={desc_text}")  # Debug print

            instruction_text = "*Click on each box for more information.*"
            instr_bbox = draw.textbbox((0, 0), instruction_text, font=ImageFont.load_default().font_variant(size=16))
            instr_width = instr_bbox[2] - instr_bbox[0]
            draw.text((center_x - instr_width / 2, desc_y + 30), instruction_text, fill=self.theme["fg"], font=ImageFont.load_default().font_variant(size=16))

            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating RAID image: {e}")
            return None
        
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

# MainApp class remains unchanged
class MainApp:
    def __init__(self, root, theme=None, apply_theme_callback=None):
        self.root = root
        self.theme = theme if theme else DEFAULT_THEME
        self.apply_theme_callback = apply_theme_callback
        self.root.withdraw()
        self.demo_window = tk.Toplevel(self.root)
        self.demo_window.title("RAID Visualization")
        self.demo_window.geometry("1200x800")  # Default to 1200x800
        self.demo_window.configure(bg=self.theme["bg"])
        self.raid_app = RAIDVisualizationApp(self.demo_window, theme=self.theme)
        self.demo_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.demo_window.bind("<Configure>", self.check_completion)

    def apply_theme(self, theme):
        self.theme = theme
        self.demo_window.configure(bg=theme["bg"])
        self.raid_app.apply_theme(theme)
        if self.apply_theme_callback:
            self.apply_theme_callback(theme)

    def on_closing(self):
        """Handle the demo window closing event."""
        try:
            # Clean up the RAIDVisualizationApp instance
            if hasattr(self, 'raid_app') and self.raid_app:
                self.raid_app.close_demo()

            # Destroy the demo window
            if self.demo_window:
                self.demo_window.destroy()

            # Do not reiconify the root window; let it exit naturally
            # self.root.deiconify()  # Removed to avoid reopening root
        except Exception as e:
            print(f"[ERROR] Error closing RAID Visualization Demo: {e}")

    def check_completion(self, event):
        if hasattr(self.raid_app, 'current_step') and self.raid_app.current_step == 3:
            pass  # Handled by create_navigation_buttons

if __name__ == "__main__":
    root = tk.Tk()
    root.title("RAID Visualization")
    root.geometry("1200x800")  # Default to 1200x800
    root.configure(bg=DEFAULT_THEME["bg"])
    app = MainApp(root, theme=DEFAULT_THEME)
    root.mainloop()