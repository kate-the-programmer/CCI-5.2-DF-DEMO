#!/usr/bin/env python3
"""
Autopsy Digital Forensics Demo - Styled like Ransomware Demo
Enhanced visual interface with animations and effects
FIXED: Background now properly covers fullscreen
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import string
import time
from PIL import Image, ImageDraw, ImageTk
import os

# Dark theme similar to ransomware demo
# self.theme = {
#     "bg": "#1a1a1a",           # Dark background
#     "fg": "#00ff00",           # Green text (matrix style)
#     "button_bg": "#ff0000",    # Red buttons
#     "button_fg": "#ffffff",    # White button text
#     "terminal_bg": "#000000",  # Black terminal
#     "terminal_fg": "#00ff00",  # Green terminal text
#     "active_fg": "#ffffff",    # White for active states
#     "disabled_fg": "#666666",  # Gray for disabled states
#     "card_bg": "#2d2d2d",      # Dark cards
#     "border": "#444444"        # Dark borders
# }

class AutopsyDemo:
    def __init__(self, root, next_callback, app, theme, apply_theme_callback=None):
        self.root = root
        self.next_callback = next_callback
        self.app = app
        self.theme = theme
        self.apply_theme_callback = apply_theme_callback
        self.root.title("🔍 Autopsy Digital Forensics Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.theme["bg"])
        
        # Demo state
        self.current_step = 0
        self.completed_steps = set()
        self.current_text = ""
        self.current_text_widget = None
        self.canvas_item_id = None
        self.button_items = []
        self.header_items = []  # Track header elements
        self.bg_image_id = None
        self.bg_photo = None
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialize steps data
        self.initialize_steps()
        
        # Create UI components
        self.create_canvas()
        
        # Bind window resize events to update background
        self.root.bind('<Configure>', self.on_window_resize)
        
        self.load_step()
    
    def initialize_steps(self):
        self.steps = [
            {
                'title': 'Getting Started with Autopsy',
                'description': 'Launch Autopsy and understand the workspace',
                'content': self.get_getting_started_content
            },
            {
                'title': 'Creating Your Investigation Case',
                'description': 'Step-by-step case creation process',
                'content': self.get_case_creation_content
            },
            {
                'title': 'Adding the USB Drive Image',
                'description': 'Import your .dd evidence file into Autopsy',
                'content': self.get_add_usb_image_content
            },
            {
                'title': 'Configuring Ingest Modules',
                'description': 'Select the right analysis modules for deleted file recovery',
                'content': self.get_configure_ingest_content
            },
            {
                'title': 'Monitoring Evidence Processing',
                'description': 'Watch Autopsy analyze your USB image',
                'content': self.get_monitoring_content
            },
            {
                'title': 'Navigating to Deleted Files',
                'description': 'Find the deleted files view in Autopsy',
                'content': self.get_navigate_deleted_content
            },
            {
                'title': 'Examining Deleted File Details',
                'description': 'Analyze metadata and recover deleted content',
                'content': self.get_examine_deleted_content
            },
            {
                'title': 'Recovering and Extracting Files',
                'description': 'Export deleted files from the USB image',
                'content': self.get_recovery_content
            },
            {
                'title': 'Documenting Your Findings',
                'description': 'Create reports and maintain chain of custody',
                'content': self.get_documentation_content
            }
        ]
    
    def on_window_resize(self, event):
        """Handle window resize events to update background"""
        # Only respond to main window resize events
        if event.widget == self.root:
            # Small delay to avoid too many rapid updates
            self.root.after(100, self.update_background_and_canvas)
    
    def update_background_and_canvas(self):
        """Update background and canvas size when window is resized"""
        try:
            # Get current actual window dimensions
            self.root.update_idletasks()
            actual_width = self.root.winfo_width()
            actual_height = self.root.winfo_height()
            
            # Only update if dimensions have actually changed significantly
            if (hasattr(self, 'last_width') and hasattr(self, 'last_height') and
                abs(actual_width - self.last_width) < 50 and 
                abs(actual_height - self.last_height) < 50):
                return
            
            self.last_width = actual_width
            self.last_height = actual_height
            
            # Update canvas size
            canvas_width = max(1200, actual_width - 40)  # Account for padding
            canvas_height = max(800, actual_height - 40)
            
            self.canvas.config(width=canvas_width, height=canvas_height)
            self.canvas_width = canvas_width
            self.canvas_height = canvas_height
            
            # Recreate background with new dimensions
            self.create_background(canvas_width, canvas_height)
            
            # Refresh the current step to reposition elements
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
        # Update root and frame
        self.root.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])
        self.canvas.configure(bg=theme["bg"])
        
        # Recreate background with new colors
        self.create_background()
        
        # Update header elements
        for item in self.header_items:
            text = self.canvas.itemcget(item, "text")
            if "[STEP" in text:  # Step number
                self.canvas.itemconfig(item, fill=theme["button_bg"])
            elif text == self.steps[self.current_step]['description']:  # Description
                self.canvas.itemconfig(item, fill=theme["active_fg"])
            else:  # Title
                self.canvas.itemconfig(item, fill=theme["fg"])
        
        # Update content text widget if it exists
        if self.current_text_widget and self.current_text_widget.winfo_exists():
            self.current_text_widget.configure(
                bg=theme["terminal_bg"],
                fg=theme["terminal_fg"],
                insertbackground=theme["fg"]
            )
        
        # Update navigation buttons (recreate them to apply new theme)
        self.create_navigation_buttons()

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
        # Clear previous content
        for item in self.button_items:
            self.canvas.delete(item)
        self.button_items = []
        
        # Clear previous header items
        for item in self.header_items:
            self.canvas.delete(item)
        self.header_items = []
        
        if self.current_text_widget:
            self.canvas.delete(self.canvas_item_id)
        
        step = self.steps[self.current_step]
        
        # Ensure background is behind everything
        if self.bg_image_id:
            self.canvas.tag_lower(self.bg_image_id)
        
        # Create header
        self.create_step_header(step)
        
        # Get content and show with animation
        self.current_text = step['content']()
        self.show_content_with_animation()
        
        # Create navigation buttons
        self.create_navigation_buttons()
    
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
        self.root.update_idletasks()
        content_width = max(800, self.canvas_width - 100)
        content_height = max(400, self.canvas_height - 250)
        
        text_widget = tk.Text(self.root, 
                             wrap="word", 
                             font=('Courier New', 17),
                             bg=theme["terminal_bg"], 
                             fg=theme["terminal_fg"],
                             borderwidth=2,
                             relief="ridge",
                             spacing1=4, 
                             spacing2=2, 
                             spacing3=4,
                             insertbackground=theme["fg"])
        
        text_widget.insert("1.0", self.current_text)
        text_widget.config(state="disabled")
        
        self.current_text_widget = text_widget
        self.canvas_item_id = self.canvas.create_window(50, 130, 
                                                       anchor="nw", 
                                                       window=text_widget, 
                                                       width=content_width, 
                                                       height=content_height)
        
        self.decrypt_animation(text_widget, self.current_text)
        
        # Start decryption animation
        self.decrypt_animation(text_widget, self.current_text)
    
    def decrypt_animation(self, widget, original_text, step=0):
        """Animate text decryption (like in ransomware demo)"""
        try:
            if not widget.winfo_exists():
                return
            
            total_steps = 30
            if step >= total_steps:
                widget.config(state="normal")
                widget.delete("1.0", tk.END)
                widget.insert("1.0", original_text)
                widget.config(state="disabled")
                return
            
            # Create scrambled version
            fraction = step / total_steps
            display_text = list(original_text)
            
            for i in range(len(original_text)):
                if i < int(fraction * len(original_text)):
                    # Keep original character
                    pass
                elif display_text[i] not in '\n ':
                    # Scramble with cyber characters
                    display_text[i] = random.choice('█▓▒░01ABCDEFabcdef!@#$%^&*')
            
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            widget.insert("1.0", ''.join(display_text))
            widget.config(state="disabled")
            
            self.root.after(100, lambda: self.decrypt_animation(widget, original_text, step + 1))
            
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
        canvas_height = max(760, self.canvas_height)
        button_y = canvas_height - 80
        center_x = canvas_width // 2
        
        if self.current_step > 0:
            back_btn = tk.Button(self.root,
                               text="◄◄ [BACK]",
                               command=self.previous_step,
                               font=('Courier New', 17, 'bold'),
                               bg=theme["terminal_bg"],
                               fg=theme["disabled_fg"],
                               activebackground=theme["disabled_fg"],
                               activeforeground=theme["terminal_bg"],
                               relief="flat",
                               bd=2,
                               padx=15,
                               pady=10,
                               cursor="hand2",
                               highlightthickness=1,
                               highlightcolor=theme["disabled_fg"],
                               highlightbackground=theme["disabled_fg"])
            back_item = self.canvas.create_window(150, button_y, window=back_btn)
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
                           font=('Courier New', 17, 'bold'),
                           bg=theme["terminal_bg"],
                           fg=button_color,
                           activebackground=button_color,
                           activeforeground=theme["terminal_bg"],
                           relief="flat",
                           bd=2,
                           padx=15,
                           pady=10,
                           cursor="hand2",
                           highlightthickness=1,
                           highlightcolor=border_color,
                           highlightbackground=border_color)
        next_item = self.canvas.create_window(canvas_width - 150, button_y, window=next_btn)
        self.button_items.append(next_item)
        
        next_border = self.canvas.create_rectangle(canvas_width - 200, button_y-20, canvas_width - 100, button_y+20,
                                                 outline=border_color,
                                                 width=2,
                                                 fill="")
        self.button_items.append(next_border)
        
        progress_text = f">>> PROGRESS: {self.current_step + 1:02d}/{len(self.steps):02d} <<<"
        progress_item = self.canvas.create_text(center_x, button_y,
                                              text=progress_text,
                                              font=('Courier New', 18, 'bold'),
                                              fill=theme["fg"])
        self.button_items.append(progress_item)
        
        progress_width = 200
        progress_filled = int((self.current_step + 1) / len(self.steps) * progress_width)
        progress_start_x = center_x - (progress_width // 2)
        progress_end_x = center_x + (progress_width // 2)
        
        progress_bg = self.canvas.create_rectangle(progress_start_x, button_y + 25, progress_end_x, button_y + 30,
                                                 outline=theme["disabled_fg"],
                                                 fill=theme["terminal_bg"],
                                                 width=1)
        self.button_items.append(progress_bg)
        
        if progress_filled > 0:
            progress_fill = self.canvas.create_rectangle(progress_start_x, button_y + 25, 
                                                       progress_start_x + progress_filled, button_y + 30,
                                                       outline="",
                                                       fill=theme["fg"],
                                                       width=0)
            self.button_items.append(progress_fill)
        
        # print(f"Canvas items: {self.canvas.find_all()}")  # Debug print
        # print(f"Button items: {self.button_items}")
    
    def next_step(self):
        """Navigate to next step with animation"""
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
            
            # Scramble text
            scrambled = list(original_text)
            for i in range(min(step * 3, len(original_text))):
                if scrambled[i] not in '\n ':
                    scrambled[i] = random.choice('█▓▒░01!@#$%^&*')
            
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            widget.insert("1.0", ''.join(scrambled))
            widget.config(state="disabled")
            
            self.root.after(50, lambda: self.scramble_animation(widget, original_text, step + 1, callback))
            
        except Exception as e:
            print(f"Scramble error: {e}")
            callback()
    
    def transition_to_next(self):
        """Move to next step"""
        self.completed_steps.add(self.current_step)
        self.current_step += 1
        self.load_step()
    
    def previous_step(self):
        """Navigate to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.load_step()
    
    def complete_demo(self):
        """Complete the demo with final animation"""
        self.canvas.delete("all")
        
        # Recreate background for completion screen
        self.create_background()
        
        # Calculate center position for responsive display
        self.root.update_idletasks()
        canvas_width = max(1160, self.canvas_width)
        canvas_height = max(760, self.canvas_height)
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Final message
        final_text = """╔══════════════════════════════════════════════╗
║        AUTOPSY WALKTHROUGH COMPLETE          ║
╚══════════════════════════════════════════════╝
    
You have successfully completed the Autopsy 
Digital Forensics walkthrough program!

Key Skills Acquired:
► USB drive image analysis
► Deleted file recovery techniques
► Evidence processing workflows
► Professional documentation methods
► Chain of custody procedures

You're now ready to perform real forensic 
investigations using Autopsy!
"""
        
        text_id = self.canvas.create_text(center_x, center_y,
                                        text=final_text,
                                        font=('Courier New', 20, 'bold'),
                                        fill=self.theme["fg"],
                                        justify="center",
                                        anchor="center")
        
        # Add decorative border around the completion message
        text_bbox = self.canvas.bbox(text_id)
        if text_bbox:
            padding = 50
            border_rect = self.canvas.create_rectangle(
                text_bbox[0] - padding, text_bbox[1] - padding,
                text_bbox[2] + padding, text_bbox[3] + padding,
                outline=self.theme["fg"],
                width=3,
                fill=""
            )
        
        # Fade out after 5 seconds
        self.root.after(5000, self.fade_out)
    
    def fade_out(self):
        """Fade out and close"""
        messagebox.showinfo("Training Complete", 
                          "Autopsy Digital Forensics training completed!\n\nYou're ready to investigate!")
        self.root.destroy()
    
    # Content methods for each step - PRACTICAL WALKTHROUGH
    def get_getting_started_content(self):
        return """
>> AUTOPSY FORENSICS WALKTHROUGH INITIATED...
>> PRACTICAL DELETED FILE RECOVERY TRAINING...

GETTING STARTED WITH AUTOPSY
============================

SCENARIO: You have a USB drive image (.dd file) from a suspect's computer.
Your mission: Find and recover deleted files that may contain evidence.

STEP 1: LAUNCH AUTOPSY
┌─────────────────────────────────────────────┐
│ 1. Double-click the Autopsy desktop icon    │
│ 2. Wait for the startup screen to appear    │
│ 3. The main window will open automatically  │
│ 4. You should see the start screen options  │
└─────────────────────────────────────────────┘

WHAT YOU'LL SEE:
• "Create New Case" button (large, center)
• "Open Recent Case" option
• Recent cases list (if any exist)
• Help and tutorial links

WORKSPACE OVERVIEW:
▸ Cases are stored in: C:\\Cases\\ (default)
▸ Each case gets its own folder
▸ Evidence files are copied/linked to case folder
▸ All analysis results stored in case database

PREPARATION CHECKLIST:
✓ Autopsy 4.19+ installed and running
✓ USB drive image file (.dd) ready
✓ At least 2GB free disk space
✓ Administrator privileges (if needed)

IMPORTANT NOTES:
• This walkthrough uses a real Autopsy interface
• Follow each step exactly as written
• Screenshots help verify you're in the right place
• Don't skip steps - each builds on the previous

STATUS: Ready to begin practical forensic investigation.
Click NEXT to start creating your case.
        """
    
    def get_case_creation_content(self):
        return """
>> CASE CREATION PROTOCOL ACTIVE...
>> ESTABLISHING FORENSIC WORKSPACE...

CREATING YOUR INVESTIGATION CASE
================================

STEP 2: CREATE NEW CASE

EXACT STEPS TO FOLLOW:
┌─────────────────────────────────────────────┐
│ 1. Click "Create New Case" button           │
│ 2. Case Information dialog appears          │
│ 3. Fill in the following fields:            │
│    • Case Name: "USB_Recovery_Demo"         │
│    • Base Directory: C:\\Cases               │
│    • Case Type: "Single-user case"          │
│ 4. Click "Next" button                      │
│ 5. Case Details screen appears              │
│ 6. Fill in optional information:            │
│    • Case Number: "2024-USB-001"            │
│    • Examiner: [Your Name]                  │
│    • Examiner Phone: [Optional]             │
│    • Examiner Email: [Optional]             │
│    • Notes: "USB deleted file recovery"     │
│ 7. Click "Finish" button                    │
└─────────────────────────────────────────────┘

VERIFICATION CHECKPOINTS:
✓ Case folder created at: C:\\Cases\\USB_Recovery_Demo
✓ Main Autopsy window shows your case name in title bar
✓ Left panel shows empty "Data Sources" tree
✓ Center panel shows "Add Data Source" message
✓ Bottom panel shows case messages

WHAT AUTOPSY CREATES:
• Case database file (.db)
• Configuration files
• Reports folder
• Export folder
• Cache folder
• Log files folder

TROUBLESHOOTING:
❌ If "Create New Case" is grayed out:
  → Check if another case is already open
  → Close current case first: File → Close Case

❌ If you get permission errors:
  → Run Autopsy as Administrator
  → Choose a different base directory

STATUS: Case workspace established.
Ready to add your USB drive evidence.
        """
    
    def get_add_usb_image_content(self):
        return """
>> EVIDENCE ACQUISITION INITIATED...
>> IMPORTING USB DRIVE IMAGE...

ADDING YOUR USB DRIVE IMAGE
===========================

STEP 3: IMPORT THE .DD FILE

EXACT PROCEDURE:
┌─────────────────────────────────────────────┐
│ METHOD 1: Using the Welcome Tab             │
│ 1. Look for "Add Data Source" button        │
│ 2. Click "Add Data Source"                  │
│                                             │
│ METHOD 2: Using the Menu                    │
│ 1. Click "Case" in menu bar                 │
│ 2. Select "Add Data Source"                 │
│                                             │
│ METHOD 3: Using Toolbar                     │
│ 1. Look for hard drive icon in toolbar      │
│ 2. Click the "Add Data Source" icon         │
└─────────────────────────────────────────────┘

DATA SOURCE WIZARD STEPS:
┌─────────────────────────────────────────────┐
│ STEP 3A: Select Data Source Type            │
│ 1. Choose "Disk Image or VM File"           │
│ 2. Click "Next"                             │
│                                             │
│ STEP 3B: Select Image File                  │
│ 1. Click "Browse" button                    │
│ 2. Navigate to your .dd file location       │
│ 3. Select the USB image file                │
│ 4. Click "Open"                             │
│ 5. Verify path shows in text field          │
│ 6. Click "Next"                             │
│                                             │
│ STEP 3C: Configure Settings                 │
│ 1. Time Zone: Select your local timezone    │
│ 2. Sector Size: Leave as "Auto Detect"      │
│ 3. Click "Next"                             │
└─────────────────────────────────────────────┘

FILE VERIFICATION:
• File path should end with .dd, .raw, .img, or .001
• File size should be reasonable (USB drives: 1MB-64GB+)
• Autopsy will validate the image format

COMMON FILE LOCATIONS:
• Desktop: C:\\Users\\[username]\\Desktop\\
• Downloads: C:\\Users\\[username]\\Downloads\\
• Evidence folder: C:\\Evidence\\
• Network drives: \\\\server\\share\\

STATUS: USB image file selected and verified.
Next: Configure analysis modules for deleted file recovery.
        """
    
    def get_configure_ingest_content(self):
        return """
>> INGEST MODULE CONFIGURATION...
>> OPTIMIZING FOR DELETED FILE RECOVERY...

CONFIGURING ANALYSIS MODULES
============================

STEP 4: SELECT INGEST MODULES

CRITICAL MODULES FOR DELETED FILE RECOVERY:
┌─────────────────────────────────────────────┐
│ REQUIRED MODULES (Check These):             │
│ ✓ File Type Identification                  │
│   • Identifies file types by signature      │
│   • Essential for deleted file recognition  │
│                                             │
│ ✓ Extension Mismatch Detector               │
│   • Finds files with wrong extensions       │
│   • Catches disguised deleted files         │
│                                             │
│ ✓ Embedded File Extractor                   │
│   • Extracts files from containers          │
│   • Recovers files from unallocated space   │
│                                             │
│ ✓ Hash Lookup                               │
│   • Identifies known files                  │
│   • Helps filter important vs. system files │
│                                             │
│ OPTIONAL BUT HELPFUL:                       │
│ ✓ Keyword Search                            │
│   • Indexes file content for searching      │
│                                             │
│ ✓ EXIF Extractor                            │
│   • Gets metadata from images               │
│                                             │
│ ⚠ SKIP THESE FOR NOW:                       │
│ ☐ PhotoRec Carver (advanced)                │
│ ☐ Plaso (timeline analysis)                 │
│ ☐ Android Analyzer (not needed for USB)     │
└─────────────────────────────────────────────┘

EXACT CONFIGURATION STEPS:
1. In the Ingest Modules tab, you'll see a list of modules
2. CHECK the boxes next to required modules above
3. UNCHECK any modules you don't need (saves time)
4. Click "Next" to proceed
5. Review settings on final screen
6. Click "Finish" to start processing

PROCESSING TIME ESTIMATES:
• Small USB (1-8GB): 5-15 minutes
• Medium USB (16-32GB): 15-45 minutes  
• Large USB (64GB+): 1-3 hours

WHAT'S HAPPENING BEHIND THE SCENES:
→ Autopsy scans every sector of the USB image
→ Recovers deleted file headers and metadata
→ Rebuilds file allocation table
→ Identifies recoverable deleted files
→ Indexes content for searching

STATUS: Ingest modules configured for optimal deleted file recovery.
Processing will begin when you click Finish.
        """
    
    def get_monitoring_content(self):
        return """
>> EVIDENCE PROCESSING IN PROGRESS...
>> MONITORING DELETED FILE RECOVERY...

MONITORING EVIDENCE PROCESSING
==============================

STEP 5: WATCH THE ANALYSIS PROGRESS

AFTER CLICKING "FINISH":
┌─────────────────────────────────────────────┐
│ 1. Processing starts immediately            │
│ 2. Progress shown in bottom-right panel     │
│ 3. Multiple modules run simultaneously      │
│ 4. Messages appear in bottom panel          │
│ 5. Data source appears in left tree         │
└─────────────────────────────────────────────┘

PROGRESS MONITORING LOCATIONS:
▸ BOTTOM PANEL - "Ingest Messages"
  → Shows real-time processing updates
  → Error messages appear here
  → Completion notifications

▸ BOTTOM-RIGHT CORNER - Progress Indicators  
  → Individual module progress bars
  → Overall completion percentage
  → Time remaining estimates

▸ LEFT PANEL - Data Sources Tree
  → USB image appears when processing starts
  → Folders populate as analysis progresses
  → Results organize automatically

WHAT TO LOOK FOR:
✓ "File Type Identification" completing first
✓ "Deleted Files" folder appearing in Views
✓ File counts increasing in various categories
✓ "Hash Lookup" processing known files
✓ No error messages in red text

SAMPLE PROGRESS MESSAGES:
• "Processing image sectors..."
• "Identifying file signatures..."
• "Recovering deleted file headers..."
• "Building file allocation table..."
• "Indexing file content..."
• "Analysis complete for [module name]"

DURING PROCESSING YOU CAN:
→ Browse already-processed results
→ Start examining recovered files
→ Check system performance
→ Review case notes
→ Prepare documentation

DON'T DO WHILE PROCESSING:
❌ Close Autopsy
❌ Shut down computer
❌ Remove USB image file
❌ Add more data sources

STATUS: Evidence processing active. Deleted files being recovered.
You can start examining results while processing continues.
        """
    
    def get_navigate_deleted_content(self):
        return """
>> DELETED FILE ANALYSIS READY...
>> NAVIGATING TO RECOVERY RESULTS...

FINDING DELETED FILES IN AUTOPSY
================================

STEP 6: NAVIGATE TO DELETED FILES VIEW

PRIMARY NAVIGATION PATH:
┌─────────────────────────────────────────────┐
│ LEFT PANEL NAVIGATION:                      │
│ 1. Look for "Views" section in tree         │
│ 2. Expand "Views" by clicking [+] symbol    │
│ 3. Find "File Types" and expand it          │
│ 4. Look for "Deleted Files" category        │
│ 5. Click on "Deleted Files"                 │
│                                             │
│ ALTERNATIVE PATH:                           │
│ 1. Expand your data source name             │
│ 2. Look for volume/partition                │
│ 3. Find "$OrphanFiles" folder               │
│ 4. Browse deleted files by location         │
└─────────────────────────────────────────────┘

WHAT YOU'LL SEE IN THE CENTER PANEL:
• List of all deleted files found on USB
• Files displayed with RED text (indicates deleted)
• File names, sizes, and timestamps
• Recovery status indicators
• File type icons

KEY COLUMNS TO EXAMINE:
▸ NAME: Original filename (may be partial)
▸ SIZE: File size in bytes
▸ MODIFIED: When file was last changed
▸ CREATED: When file was originally created
▸ ACCESSED: When file was last opened
▸ META TYPE: File system metadata type
▸ KNOWN: Whether file matches known hash database

DELETED FILE INDICATORS:
🔴 RED TEXT = Deleted file
📁 FOLDER ICON = Deleted directory
❓ QUESTION MARK = Partially recoverable
✓ CHECKMARK = Fully recoverable
⚠ WARNING = Potential corruption

SORTING AND FILTERING:
• Click column headers to sort
• Use "Filter" box to search filenames
• Right-click for additional options
• Double-click files to preview content

RECOVERY QUALITY INDICATORS:
→ GREEN: Fully recoverable, no overwriting
→ YELLOW: Partially recoverable, some overwriting
→ RED: Minimal recovery, heavily overwritten

STATUS: Navigation complete. Deleted files now visible.
Ready to examine specific deleted file details.
        """
    
    def get_examine_deleted_content(self):
        return """
>> DETAILED DELETED FILE ANALYSIS...
>> FORENSIC EXAMINATION PROTOCOLS...

EXAMINING DELETED FILE DETAILS
==============================

STEP 7: ANALYZE SPECIFIC DELETED FILES

DETAILED EXAMINATION PROCESS:
┌─────────────────────────────────────────────┐
│ SELECT A DELETED FILE:                      │
│ 1. Click on any red-text deleted file       │
│ 2. File details appear in right panel       │
│ 3. Content preview loads in center          │
│                                             │
│ EXAMINE THE RIGHT PANEL:                    │
│ 1. "General" tab - Basic file info          │
│ 2. "Metadata" tab - File system details     │
│ 3. "Analysis" tab - Autopsy findings        │
│ 4. "Tags" tab - Investigator annotations    │
└─────────────────────────────────────────────┘

CRITICAL METADATA TO REVIEW:
▸ ORIGINAL FILENAME: May be truncated or corrupted
▸ FILE SIZE: Compare allocated vs actual size
▸ TIMESTAMPS: Creation, modification, access times
▸ FILE SIGNATURE: Verify actual file type
▸ CLUSTER ALLOCATION: Where file was stored
▸ RECOVERY STATUS: Likelihood of full recovery

FILE CONTENT EXAMINATION:
→ TEXT FILES: Content appears in center panel
→ IMAGES: Thumbnail and full preview available
→ DOCUMENTS: Text extraction if possible
→ EXECUTABLES: Basic properties shown
→ UNKNOWN: Hex view for manual analysis

EVIDENCE VALUE ASSESSMENT:
✓ HIGH VALUE: Documents, images, databases
✓ MEDIUM VALUE: Configuration files, logs
✓ LOW VALUE: Temporary files, cache files
✓ NO VALUE: System files, known good files

RIGHT-CLICK OPTIONS:
• "Extract File" - Save deleted file to disk
• "View in New Window" - Open detailed viewer
• "Add Tag" - Mark as evidence
• "Export" - Save with metadata
• "Calculate Hash" - Verify integrity

FORENSIC CONSIDERATIONS:
⚠ Document which files were found deleted
⚠ Note timestamps relative to incident
⚠ Assess intentional vs accidental deletion
⚠ Check for file wiping or overwriting
⚠ Identify attempts to hide evidence

PRACTICAL EXAMINATION WORKFLOW:
1. Start with largest files (likely documents/media)
2. Focus on recently deleted files
3. Look for files deleted around incident time
4. Examine files with suspicious names
5. Check for encrypted or password-protected files

STATUS: Deleted file examination in progress.
Ready to recover and extract evidence files.
        """
    
    def get_recovery_content(self):
        return """
>> FILE RECOVERY OPERATIONS ACTIVE...
>> EXTRACTING DELETED EVIDENCE...

RECOVERING AND EXTRACTING FILES
===============================

STEP 8: EXTRACT DELETED FILES

INDIVIDUAL FILE EXTRACTION:
┌─────────────────────────────────────────────┐
│ METHOD 1: Right-Click Extraction            │
│ 1. Right-click on deleted file              │
│ 2. Select "Extract File(s)"                 │
│ 3. Choose destination folder                │
│ 4. Click "Save"                             │
│                                             │
│ METHOD 2: Menu Extraction                   │
│ 1. Select file in center panel              │
│ 2. Go to "Tools" menu                       │
│ 3. Choose "Extract File(s)"                 │
│ 4. Specify output location                  │
└─────────────────────────────────────────────┘

BULK EXTRACTION PROCESS:
1. Hold Ctrl key while clicking multiple files
2. All selected files highlight in blue
3. Right-click on selection
4. Choose "Extract File(s)"
5. Select destination folder
6. Autopsy extracts all files with original names

RECOMMENDED EXTRACTION FOLDER STRUCTURE:
Evidence/
├── Recovered_Documents/
├── Recovered_Images/  
├── Recovered_Videos/
├── Suspicious_Files/
└── System_Files/

EXTRACTION VERIFICATION:
✓ Files save with original timestamps preserved
✓ File sizes match metadata
✓ Hash values calculated automatically
✓ Extraction log created
✓ Chain of custody maintained

ADVANCED EXTRACTION OPTIONS:
▸ "Export with Metadata" - Includes forensic details
▸ "Export Selected Files" - Bulk extraction
▸ "Export Directory Tree" - Maintains folder structure
▸ "Generate Report" - Documents extraction process

RECOVERY SUCCESS INDICATORS:
🟢 FULL RECOVERY: File completely intact
🟡 PARTIAL RECOVERY: Some data missing
🔴 FAILED RECOVERY: File too corrupted

HANDLING CORRUPTED FILES:
• Try different viewers/editors
• Use hex editor for manual analysis
• Check file headers for partial content
• Document corruption in case notes

FORENSIC BEST PRACTICES:
→ Extract to write-protected media
→ Calculate MD5/SHA hashes
→ Document extraction process
→ Preserve original timestamps
→ Maintain chain of custody logs

LEGAL CONSIDERATIONS:
⚠ Never modify original evidence
⚠ Document all extraction procedures
⚠ Verify extracted file integrity
⚠ Maintain detailed logs
⚠ Follow organization policies

STATUS: File recovery operations complete.
Ready to document findings and create reports.
        """
    
    def get_documentation_content(self):
        return """
>> CASE DOCUMENTATION PROTOCOLS...
>> GENERATING FORENSIC REPORTS...

DOCUMENTING YOUR FINDINGS
=========================

STEP 9: CREATE PROFESSIONAL DOCUMENTATION

IMMEDIATE DOCUMENTATION TASKS:
┌─────────────────────────────────────────────┐
│ 1. TAG IMPORTANT EVIDENCE                   │
│    • Right-click files → "Add Tag"          │
│    • Use descriptive tag names              │
│    • Color-code by evidence type            │
│                                             │
│ 2. ADD CASE NOTES                           │
│    • Document investigation steps           │
│    • Record key findings                    │
│    • Note any anomalies or issues           │
│                                             │
│ 3. TAKE SCREENSHOTS                         │
│    • Capture key evidence screens           │
│    • Document file locations                │
│    • Show recovery statistics               │
└─────────────────────────────────────────────┘

GENERATE AUTOPSY REPORTS:
▸ STEP 9A: Access Report Generator
  1. Go to "Tools" menu
  2. Select "Generate Report"
  3. Choose report type (HTML recommended)

▸ STEP 9B: Configure Report Sections
  ✓ Case Information
  ✓ Data Source Summary  
  ✓ Deleted Files Results
  ✓ File Analysis Details
  ✓ Hash Values
  ✓ Extraction Log

▸ STEP 9C: Generate and Review
  1. Click "Generate Report"
  2. Wait for processing to complete
  3. Review report in web browser
  4. Check all sections for accuracy

MANUAL DOCUMENTATION CHECKLIST:
📋 INVESTIGATION SUMMARY
  • Case number and details
  • Evidence source information
  • Investigation timeline
  • Key personnel involved

📋 TECHNICAL DETAILS
  • USB image file hash values
  • Autopsy version used
  • Processing modules enabled
  • Any technical issues encountered

📋 DELETED FILE INVENTORY
  • Total number of deleted files found
  • Files successfully recovered
  • Files of evidentiary value
  • Extraction locations and hashes

📋 CHAIN OF CUSTODY
  • Evidence handling procedures
  • Who accessed the evidence when
  • File extraction documentation
  • Storage and security measures

PROFESSIONAL REPORTING TIPS:
→ Use clear, non-technical language for summaries
→ Include technical details in appendices
→ Provide context for all findings
→ Document limitations and assumptions
→ Prepare for potential court testimony

FINAL VERIFICATION STEPS:
✓ All important deleted files extracted
✓ File integrity verified with hashes
✓ Complete documentation package
✓ Secure storage of evidence
✓ Case files properly organized

CASE COMPLETION WORKFLOW:
1. Finalize all documentation
2. Secure evidence storage
3. Backup case files
4. Close Autopsy case properly
5. Archive according to policy

STATUS: Investigation complete. Professional documentation ready.
Deleted file recovery mission accomplished successfully.

CONGRATULATIONS! You've successfully completed a forensic investigation
of a USB drive image and recovered deleted files using Autopsy.
        """

def main():
    root = tk.Tk()
    
    # Set up window for proper fullscreen support
    root.state('zoomed')
    try:
        root.attributes('-zoomed', True)
    except tk.TclError:
        try:
            root.attributes('-fullscreen', True)
        except tk.TclError:
            pass
    
    root.resizable(True, True)
    
    # Dummy app object for standalone testing
    class DummyApp:
        def __init__(self):
            self.themes = {
                "dark": {
                    "bg": "#1a1a1a",
                    "fg": "#00ff00",
                    "button_bg": "#ff0000",
                    "button_fg": "#ffffff",
                    "terminal_bg": "#000000",
                    "terminal_fg": "#00ff00",
                    "active_fg": "#ffffff",
                    "disabled_fg": "#666666",
                    "card_bg": "#2d2d2d",
                    "border": "#444444"
                }
            }
            self.current_theme = "dark"
    
    dummy_app = DummyApp()
    app = AutopsyDemo(root, next_callback=lambda: None, app=dummy_app, theme=dummy_app.themes[dummy_app.current_theme], apply_theme_callback=None)
    
    def toggle_fullscreen(event=None):
        state = not root.attributes('-fullscreen')
        root.attributes('-fullscreen', state)
        
    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)
        
    root.bind('<F11>', toggle_fullscreen)
    root.bind('<Escape>', exit_fullscreen)
    
    root.mainloop()
if __name__ == "__main__":
    main()