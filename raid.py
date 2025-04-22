import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os

# Sample file
SAMPLE_FILE = "sample.txt"
if not os.path.exists(SAMPLE_FILE):
    with open(SAMPLE_FILE, "w") as f:
        f.write("This is a sample file to demonstrate RAID configurations with 64 bytes of data.")

# Read sample file
with open(SAMPLE_FILE, "rb") as f:
    file_data = f.read()
    print(f"File size: {len(file_data)} bytes")
    file_size = len(file_data)

# Window setup
root = tk.Tk()
root.title("RAID Configurations")
root.geometry("800x600")

# Load font
font = ImageFont.truetype("arial.ttf", 12)  # Arial, size 12

# Store block coordinates for clickable regions
block_coords = {}

def hex_to_rgb(hex_color):
    """Convert hex color (e.g., '#FF4040') or named color (e.g., 'gray') to RGB tuple."""
    if hex_color.startswith('#'):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    else:
        color_map = {
            "gray": (128, 128, 128),  # Medium gray
            "black": (0, 0, 0),
            "white": (255, 255, 255),
        }
        if hex_color.lower() in color_map:
            return color_map[hex_color.lower()]
        raise ValueError(f"Unknown color name: {hex_color}")

def draw_simple_block(draw, x, y, width, height, fill_color, text, text_color="black", raid_type=None, disk=None, segment=None):
    # Draw block with rounded corners and thin gray outline
    corner_radius = 10
    draw.rounded_rectangle([x, y, x + width - 10, y + height], radius=corner_radius, fill=fill_color, outline="#808080")  # Light gray outline
    # Center text in the block
    text_pos = (x + (width - 10) / 2, y + height / 2)
    draw.text(text_pos, text, fill=text_color, font=font, anchor="mm")
    
    # Store coordinates for clickable region, including raid_type, disk, and segment for context
    block_coords[(x, y, x + width - 10, y + height)] = (raid_type, disk, segment)

def on_canvas_click(event):
    x, y = event.x, event.y
    for coords, (raid_type, disk, segment) in block_coords.items():
        if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
            show_detail_window(raid_type, disk, segment)
            break

def show_detail_window(raid_type, disk, segment):
    detail_window = tk.Toplevel(root)
    detail_window.title(f"Details for {segment}")
    detail_window.geometry("600x400")
    
    text = tk.Text(detail_window, height=20, width=70)
    text.pack(pady=10, padx=10)
    
    if raid_type == "RAID 0":
        text.insert(tk.END, f"RAID 0 - Striping Detail for {segment} on Disk {disk}\n")
        text.insert(tk.END, "Data is split into segments across drives for speed.\n")
        file_num, seg = segment[1], segment[-1]  # e.g., "F1a" -> file 1, segment 'a'
        file_idx = int(file_num) - 1  # Convert to 0-based index
        segment_size = 10  # Use 10 bytes per segment for demo
        if seg == 'a':
            start = file_idx * segment_size
            data_segment = file_data[start:start + segment_size]
        elif seg == 'b':
            start = file_idx * segment_size + 10
            data_segment = file_data[start:start + segment_size]
        elif seg == 'c':
            start = file_idx * segment_size + 20
            data_segment = file_data[start:start + min(segment_size, len(file_data) - (file_idx * segment_size + 20))]
        text.insert(tk.END, f"File {file_num}: Segment {seg} on Disk {disk}\n")
        text.insert(tk.END, f"Sample Data: {data_segment.hex()} (segment of sample.txt)\n")
        text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + (ord(seg) - ord('a')) * 0x100:04x}\n")
        text.insert(tk.END, "No redundancy; data loss if any disk fails.\n")

    elif raid_type == "RAID 1":
        text.insert(tk.END, f"RAID 1 - Mirroring Detail for {segment} on Disk {disk}\n")
        text.insert(tk.END, "Data is duplicated across all disks for full redundancy.\n")
        file_num = segment.split(" ")[1]  # e.g., "File 1" -> file 1
        text.insert(tk.END, f"File {file_num} is mirrored on Disks 1, 2, and 3.\n")
        text.insert(tk.END, f"Sample Data: {file_data[:10].hex()} (first 10 bytes of sample.txt)\n")
        text.insert(tk.END, "Memory Address (simulated): 0x{disk * 0x1000:04x} (same on all disks)\n")
        text.insert(tk.END, "Can survive up to 2 disk failures with 3 disks.\n")

    elif raid_type == "RAID 5":
        if segment.startswith("P"):
            text.insert(tk.END, f"RAID 5 - Parity Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "Parity (XOR of data segments) allows data recovery if a disk fails.\n")
            stripe = int(segment[1]) - 1  # e.g., "P1" -> stripe 0
            text.insert(tk.END, f"Parity {segment} calculated for Stripe {stripe+1}:\n")
            text.insert(tk.END, "Sample Parity Calculation (simplified XOR):\n")
            segment_size = 10  # Match RAID 0 segment size
            if stripe == 0:  # P1 (Stripe 1): F1a (Disk 1) XOR F1b (Disk 2)
                f1a_data = file_data[:segment_size]  # Bytes 0-9 for F1a (Disk 1)
                f1b_data = file_data[10:20]  # Bytes 10-19 for F1b (Disk 2)
                parity = bytes(a ^ b for a, b in zip(f1a_data, f1b_data[:len(f1a_data)]))
                text.insert(tk.END, f"  F1a XOR F1b = P1: {parity.hex()} (first {len(f1a_data)} bytes)\n")
            elif stripe == 1:  # P2 (Stripe 2): F2a (Disk 1) XOR F2b (Disk 3)
                f2a_data = file_data[20:30]  # Bytes 20-29 for F2a (Disk 1)
                f2b_data = file_data[40:50]  # Bytes 40-49 for F2b (Disk 3)
                parity = bytes(a ^ b for a, b in zip(f2a_data, f2b_data[:len(f2a_data)]))
                text.insert(tk.END, f"  F2a XOR F2b = P2: {parity.hex()} (first {len(f2a_data)} bytes)\n")
            elif stripe == 2:  # P3 (Stripe 3): F3a (Disk 2) XOR F3b (Disk 3)
                f3a_data = file_data[30:40]  # Bytes 30-39 for F3a (Disk 2)
                f3b_data = file_data[50:60]  # Bytes 50-59 for F3b (Disk 3)
                parity = bytes(a ^ b for a, b in zip(f3a_data, f3b_data[:len(f3a_data)]))
                text.insert(tk.END, f"  F3a XOR F3b = P3: {parity.hex()} (first {len(f3a_data)} bytes)\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + stripe * 0x100:04x}\n")
        else:
            text.insert(tk.END, f"RAID 5 - Striping Detail for {segment} on Disk {disk}\n")
            text.insert(tk.END, "Data is striped across drives with parity for fault tolerance.\n")
            file_num, seg = segment[1], segment[-1]  # e.g., "F1a" -> file 1, segment 'a'
            file_idx = int(file_num) - 1
            stripe = file_idx  # Map file to stripe (File 1 -> Stripe 0, File 2 -> Stripe 1, File 3 -> Stripe 2)
            segment_size = 10  # Use 10 bytes per segment for demo
            if seg == 'a':
                if stripe == 0:  # F1a on Disk 1
                    data_segment = file_data[:segment_size]  # Bytes 0-9
                elif stripe == 1:  # F2a on Disk 1
                    data_segment = file_data[20:30]  # Bytes 20-29
                elif stripe == 2:  # F3a on Disk 2
                    data_segment = file_data[30:40]  # Bytes 30-39
            elif seg == 'b':
                if stripe == 0:  # F1b on Disk 2
                    data_segment = file_data[10:20]  # Bytes 10-19
                elif stripe == 1:  # F2b on Disk 3
                    data_segment = file_data[40:50]  # Bytes 40-49
                elif stripe == 2:  # F3b on Disk 3
                    data_segment = file_data[50:60]  # Bytes 50-59
            text.insert(tk.END, f"File {file_num}: Segment {seg} on Disk {disk}\n")
            text.insert(tk.END, f"Sample Data: {data_segment.hex()} (segment of sample.txt)\n")
            text.insert(tk.END, f"Memory Address (simulated): 0x{disk * 0x1000 + stripe * 0x100 + (ord(seg) - ord('a')) * 0x10:04x}\n")
            text.insert(tk.END, "Parity on another disk ensures data recovery if this disk fails.\n")

    text.config(state=tk.DISABLED)  # Make text read-only

def show_raid0():
    global canvas
    try:
        img = create_raid_image("RAID 0")
        print(f"Image created: {img}")
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.image = img
    except Exception as e:
        print(f"Error in show_raid0: {e}")
        raise

def show_raid1():
    global canvas
    img = create_raid_image("RAID 1")
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.image = img

def show_raid5():
    global canvas
    img = create_raid_image("RAID 5")
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.image = img

def create_raid_image(raid_type):
    try:
        width, height = 600, 400
        print(f"Creating image for {raid_type} with size {width}x{height}")
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        ssd_width = 150
        ssd_spacing = 30
        colors = ["#FF4040", "#40FF40", "#4040FF"]  # Vibrant colors for File 1, File 2, File 3
        num_files = 3
        block_height = 50  # Height of each block
        corner_radius = 10  # Radius for rounded corners

        # Add disk labels above each column
        for i in range(3):
            x_start = i * (ssd_width + ssd_spacing) + 50
            print(f"Drawing Disk label for Disk {i + 1} at x={x_start}")
            draw.text((x_start + 40, 5), f"Disk {i + 1}", fill="black", font=font)

        if raid_type == "RAID 0":
            print("Processing RAID 0")
            for i in range(3):  # 3 SSDs
                x_start = i * (ssd_width + ssd_spacing) + 50
                for j in range(num_files):  # 3 segments per drive
                    y_start = 20 + j * (block_height + 10)
                    print(f"Drawing block for F{j+1}{chr(97+i)} at ({x_start}, {y_start})")
                    draw_simple_block(draw, x_start, y_start, ssd_width, block_height, colors[j], f"F{j+1}{chr(97+i)}",
                                      raid_type="RAID 0", disk=i + 1, segment=f"F{j+1}{chr(97+i)}")
            draw.text((50, 200), "RAID 0: Striping- Divides data into blocks spread across drives for speed. No redundancy.", 
                      fill="black", font=font)

        elif raid_type == "RAID 1":
            print("Processing RAID 1")
            for i in range(3):  # 3 SSDs
                x_start = i * (ssd_width + ssd_spacing) + 50
                for j in range(num_files):
                    y_start = 20 + j * 60
                    print(f"Drawing block for File {j+1} at ({x_start}, {y_start})")
                    draw_simple_block(draw, x_start, y_start, ssd_width, block_height, colors[j], f"File {j + 1}",
                                      raid_type="RAID 1", disk=i + 1, segment=f"File {j + 1}")
            draw.text((50, 200), "RAID 1: Mirroring - Duplicates all data across all disks for full redundancy.", 
                      fill="black", font=font)

        elif raid_type == "RAID 5":
            print("Processing RAID 5")
            # Define stripes with correct segment and parity placement, alternating parity
            stripes = [
                (0, 1, 2),  # Stripe 1: F1a (Disk 1), F1b (Disk 2), P1 (Disk 3)
                (0, 2, 1),  # Stripe 2: F2a (Disk 1), P2 (Disk 3), F2b (Disk 2)
                (2, 0, 1)   # Stripe 3: P3 (Disk 2), F3a (Disk 1), F3b (Disk 3)
            ]
            for stripe_idx, (disk_f1, disk_f2, disk_p) in enumerate(stripes):
                for disk_idx, content in enumerate([disk_f1, disk_f2, disk_p]):
                    parity_value = 2  # Parity block
                    x_start = disk_idx * (ssd_width + ssd_spacing) + 50
                    y_start = 20 + stripe_idx * (block_height + 10)
                    if content == parity_value:  # Parity block
                        print(f"Drawing parity block P{stripe_idx+1} at ({x_start}, {y_start})")
                        draw_simple_block(draw, x_start, y_start, ssd_width, block_height, "gray", f"P{stripe_idx+1}", "white",
                                          raid_type="RAID 5", disk=disk_idx + 1, segment=f"P{stripe_idx+1}")
                    else:  # File segment
                        file_idx = stripe_idx  # File matches stripe (File 1 -> Stripe 0, etc.)
                        segment = 'a' if content == disk_f1 else 'b'  # 'a' for first segment, 'b' for second
                        print(f"Drawing block for F{file_idx+1}{segment} at ({x_start}, {y_start})")
                        draw_simple_block(draw, x_start, y_start, ssd_width, block_height, colors[file_idx], 
                                          f"F{file_idx+1}{segment}",
                                          raid_type="RAID 5", disk=disk_idx + 1, segment=f"F{file_idx+1}{segment}")
            draw.text((50, 200), "RAID 5: Striping + Parity - Stripes data with parity (XOR) to rebuild lost data on failure.", 
                      fill="black", font=font)

        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error in create_raid_image: {e}")
        raise

        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error in create_raid_image: {e}")
        raise

# GUI Layout (buttons at top, canvas in middle)
label = tk.Label(root, text="RAID Configurations", font=("Arial", 14))
label.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)  # Buttons centered at top

btn_raid0 = tk.Button(button_frame, text="RAID 0", command=show_raid0, width=10, relief="flat", bg="white", fg="black", bd=0)
btn_raid0.pack(side=tk.LEFT, padx=5)

btn_raid1 = tk.Button(button_frame, text="RAID 1", command=show_raid1, width=10, relief="flat", bg="white", fg="black", bd=0)
btn_raid1.pack(side=tk.LEFT, padx=5)

btn_raid5 = tk.Button(button_frame, text="RAID 5", command=show_raid5, width=10, relief="flat", bg="white", fg="black", bd=0)
btn_raid5.pack(side=tk.LEFT, padx=5)

# Create and bind canvas
canvas = tk.Canvas(root, width=600, height=300)
canvas.pack(pady=20, padx=100, fill=tk.BOTH, expand=True)  # Centered in middle with padding
canvas.bind("<Button-1>", on_canvas_click)

# Initial display
show_raid0()

root.mainloop()