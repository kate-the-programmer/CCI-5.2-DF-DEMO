import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os

# Constants
FONT = 'Courier'
FONT_SIZE = 12
class RAIDVisualizationApp:
    def __init__(self, parent):
        # Set parent window properties
        self.parent = parent
        parent.title("RAID Visualization")
        parent.geometry("800x600")
        
        # Sample file
        self.SAMPLE_FILE = "sample.txt"
        if not os.path.exists(self.SAMPLE_FILE):
            with open(self.SAMPLE_FILE, "w") as f:
                f.write("This is a sample file to demonstrate RAID configurations with 64 bytes of data.")

        # Read sample file
        with open(self.SAMPLE_FILE, "rb") as f:
            self.file_data = f.read()
            print(f"File size: {len(self.file_data)} bytes")

        # Setup main frame
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize PIL font for drawing on images
        self.pil_font = ImageFont.load_default()
        # Store block coordinates for clickable regions
        self.block_coords = {}
        
        # GUI Layout
        label = tk.Label(self.main_frame, text="RAID Configurations", font=(FONT, 14))
        label.pack(pady=10)
        
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        self.btn_raid0 = tk.Button(self.button_frame, text="RAID 0", command=self.show_raid0, 
                                   width=10, relief="flat", bg="white", fg="black", bd=0, font=(FONT, FONT_SIZE))
        self.btn_raid0.pack(side=tk.LEFT, padx=5)
        
        self.btn_raid1 = tk.Button(self.button_frame, text="RAID 1", command=self.show_raid1, 
                                   width=10, relief="flat", bg="white", fg="black", bd=0, font=(FONT, FONT_SIZE))
        self.btn_raid1.pack(side=tk.LEFT, padx=5)
        
        self.btn_raid5 = tk.Button(self.button_frame, text="RAID 5", command=self.show_raid5, 
                                   width=10, relief="flat", bg="white", fg="black", bd=0, font=(FONT, FONT_SIZE))
        self.btn_raid5.pack(side=tk.LEFT, padx=5)
        
        self.btn_raid10 = tk.Button(self.button_frame, text="RAID 1+0", command=self.show_raid10, 
                                    width=10, relief="flat", bg="white", fg="black", bd=0, font=(FONT, FONT_SIZE))
        self.btn_raid10.pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(self.main_frame, width=600, height=300)
        self.canvas.pack(pady=20, padx=100, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Initialize with RAID 0 view
        self.show_raid0()

    def hex_to_rgb(self, hex_color):
        if hex_color.startswith('#'):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        color_map = {"gray": (128, 128, 128), "black": (0, 0, 0), "white": (255, 255, 255)}
        return color_map.get(hex_color.lower(), (0, 0, 0))

    def draw_simple_block(self, draw, x_start, y, width, height, fill_color, text, text_color="black", raid_type=None, disk=None, segment=None):
        draw.rounded_rectangle([x_start, y, x_start + width - 10, y + height], radius=10, fill=fill_color, outline="#808080")
        text_pos = (x_start + (width - 10) / 2, y + height / 2)
        draw.text(text_pos, text, fill=text_color, font=self.pil_font, anchor="mm")
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
        text = tk.Text(detail_window, height=20, width=70, font=(FONT, FONT_SIZE))
        text.pack(pady=10, padx=10)
        
        segment_size = 10
        if raid_type == "RAID 0":
            text.insert(tk.END, f"RAID 0 - Striping Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "Data is split across 2 drives for speed.\n")
            file_num, seg = segment[4], segment[-1]  # e.g., "File1a" -> file 1, segment 'a'
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
                    text.insert(tk.END, f"Parity (F2a XOR F2b): {parity.hex()}\\n")
                text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + 0x200:04x}\\n")
                text.insert(tk.END, "Survives 1 disk failure with degraded performance.\\n")
            else:
                text.insert(tk.END, f"RAID 5 - Data Detail for {segment} on Disk {disk}\\n")
                file_num, seg = segment.split(" ")[0][1], segment.split(" ")[0][2]  # e.g., "F1a" -> file 1, segment 'a'
                file_idx = int(file_num) - 1
                seg_idx = ord(seg) - ord('a')
                start = file_idx * 20 + seg_idx * 10
                data_segment = self.file_data[start:start + 10]
                text.insert(tk.END, f"File {file_num}: Segment {seg}\\n")
                text.insert(tk.END, f"Sample Data: {data_segment.hex()}\\n")
                text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + 0x100 + seg_idx * 0x100:04x}\\n")
        elif raid_type == "RAID 1+0":
            text.insert(tk.END, f"RAID 1+0 - Detail for {segment} on Disk {disk}\\n")
            text.insert(tk.END, "Data is striped across mirrors for both speed and redundancy.\\n")
            file_num, seg = segment[4], segment[-1]  # e.g., "File1a" -> file 1, segment 'a'
            file_idx = int(file_num) - 1
            start = file_idx * 20 + (0 if seg == 'a' else 10)
            data_segment = self.file_data[start:start + 10]
            text.insert(tk.END, f"File {file_num}: Segment {seg} mirrored on disk pair {1 if disk <= 2 else 2}\\n")
            text.insert(tk.END, f"Sample Data: {data_segment.hex()}\\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + (ord(seg) - ord('a')) * 0x100:04x}\\n")
            text.insert(tk.END, "Survives 1 disk failure per mirror pair.\\n")

    def show_raid0(self):
        self.canvas.delete("all")
        img = self.create_raid_image("RAID 0")
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

    def show_raid1(self):
        self.canvas.delete("all")
        img = self.create_raid_image("RAID 1")
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

    def show_raid5(self):
        self.canvas.delete("all")
        img = self.create_raid_image("RAID 5")
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

    def show_raid10(self):
        self.canvas.delete("all")
        img = self.create_raid_image("RAID 1+0")
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

    def create_raid_image(self, raid_type):
        try:
            width, height = 600, 400
            img = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(img)

            # Clear previous block coordinates
            self.block_coords = {}

            ssd_width = 115
            ssd_spacing = 30
            colors = ["#FF4040", "#40FF40", "#4040FF", "#FFFF40"]
            block_height = 50
            num_files = 2  # Limit to 2 files for simplicity across configs

            # Adjust number of drives based on RAID type
            if raid_type == "RAID 0":
                num_drives = 2
            elif raid_type == "RAID 1":
                num_drives = 2
            elif raid_type == "RAID 5":
                num_drives = 3
            elif raid_type == "RAID 1+0":
                num_drives = 4

            # Disk labels
            for i in range(num_drives):
                x_start = i * (ssd_width + ssd_spacing) + 50
                draw.text((x_start + 40, 5), f"Disk {i + 1}", fill="black", font=self.pil_font)

            # Create visualization based on RAID type
            if raid_type == "RAID 0":
                for j in range(num_files):  # For each file
                    for i in range(num_drives):  # For each drive
                        y_start = 40 + j * (block_height + 20)
                        segment = f"File{j+1}{'a' if i == 0 else 'b'}"
                        self.draw_simple_block(draw, 
                                          x_start=i * (ssd_width + ssd_spacing) + 50, 
                                          y=y_start, 
                                          width=ssd_width, 
                                          height=block_height, 
                                          fill_color=colors[j], 
                                          text=segment,
                                          raid_type="RAID 0", 
                                          disk=i+1, 
                                          segment=segment)
                draw.text((50, 275), "RAID 0: Striping - Data split across disks for speed but no redundancy.",
                          fill="black", font=self.pil_font)
                
            elif raid_type == "RAID 1":
                for j in range(num_files):  # For each file
                    y_start = 40 + j * (block_height + 20)
                    for i in range(num_drives):
                        x_start = i * (ssd_width + ssd_spacing) + 50
                        segment = f"File {j+1}"
                        self.draw_simple_block(draw, 
                                          x_start=x_start, 
                                          y=y_start, 
                                          width=ssd_width, 
                                          height=block_height, 
                                          fill_color=colors[j], 
                                          text=segment, 
                                          raid_type="RAID 1", 
                                          disk=i+1, 
                                          segment=segment)
                draw.text((50, 275), "RAID 1: Mirroring - Identical data on both disks for redundancy.",
                          fill="black", font=self.pil_font)
            
            elif raid_type == "RAID 5":
                for j in range(num_files):  # For each file (2 stripes)
                    y_start = 40 + j * (block_height + 20)
                    for i in range(num_drives):
                        x_start = i * (ssd_width + ssd_spacing) + 50
                        if (i == j % num_drives):  # Rotating parity
                            segment = f"P{j+1}"
                            fill_color = "#E0E0E0"  # Gray for parity
                        else:
                            # Calculate the segment letter based on position
                            segment_idx = 0 if i < (j % num_drives) else i-1
                            segment = f"F{j+1}{'a' if segment_idx == 0 else 'b'}"
                            fill_color = colors[j]
                        
                        self.draw_simple_block(draw, 
                                          x_start=x_start, 
                                          y=y_start, 
                                          width=ssd_width, 
                                          height=block_height,
                                          fill_color=fill_color, 
                                          text=segment, 
                                          raid_type="RAID 5", 
                                          disk=i+1, 
                                          segment=segment)
                draw.text((50, 275), "RAID 5: Striping with Parity - Data + parity distributed across disks.",
                          fill="black", font=self.pil_font)
            
            elif raid_type == "RAID 1+0":
                for j in range(num_files):  # For each file
                    for i in range(num_drives):
                        x_start = i * (ssd_width + ssd_spacing) + 50
                        y_start = 40 + j * (block_height + 20)
                        
                        # Determine which segment based on mirrored pairs (1&2, 3&4)
                        mirror_group = (i // 2)
                        segment = f"File{j+1}{'a' if mirror_group == 0 else 'b'}"
                        
                        self.draw_simple_block(draw, 
                                          x_start=x_start, 
                                          y=y_start, 
                                          width=ssd_width, 
                                          height=block_height, 
                                          fill_color=colors[j], 
                                          text=segment, 
                                          raid_type="RAID 1+0", 
                                          disk=i+1, 
                                          segment=segment)
                draw.text((50, 275), "RAID 1+0: Mirroring + Striping - Mirrors on pairs, stripes across pairs.",
                          fill="black", font=self.pil_font)
            
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error in create_raid_image: {e}")
            raise

