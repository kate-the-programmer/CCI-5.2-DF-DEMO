import tkinter as tk
import subprocess
from PIL import Image, ImageTk

FOREGROUND_COLOR = '#BF33C9'
BACKGROUND_COLOR = '#2B092E'

BUTTON_COLOR = '#4A154B'
BUTTON_TEXT_COLOR = '#FFFFFF'

TERMINAL_BG = '#1E1E1E'
TERMINAL_FG = '#BF33C9'

FONT = 'Courier'

# --- Utility Functions ---

def append_terminal_text(text_widget, message):
    text_widget.config(state='normal')
    text_widget.insert(tk.END, message + '\n')
    text_widget.see(tk.END)
    text_widget.config(state='disabled')

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f'[ERROR] {e.stderr.strip()}'

class IntroScreen:
    def __init__(self, root, switch_callback):
        self.root = root
        self.switch_callback = switch_callback

        # Main frame
        self.frame = tk.Frame(root, bg=BACKGROUND_COLOR, width=1280, height=720)
        self.frame.pack(fill='both', expand=True)

        # Content frame (top half: side-by-side)
        content_frame = tk.Frame(self.frame, bg=BACKGROUND_COLOR)
        content_frame.pack(pady=40, expand=True)

        # Text area (left side)
        text_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
        text_frame.pack(side='left', padx=40, anchor='n')

        title = tk.Label(text_frame, text='🔐 Introduction to Password Hash Cracking', fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, font=(FONT, 20))
        title.pack(pady=(0, 20), anchor='w')

        intro_text = (
            "🧩 What is a Hash?\n"
            "A hash is a fixed-length string that represents data. It's used to securely store passwords.\n\n"
            "🔓 What is Password Cracking?\n"
            "Cracking means trying to recover the original password by guessing or using a wordlist.\n\n"
            "🛠️ What is John the Ripper?\n"
            "John the Ripper is a powerful password cracking tool used by ethical hackers and security pros."
            "It can crack password hashes from zip files, Linux shadow files, and more.\n\n"
            "In the next screen, you’ll try some real cracking using John!"
        )

        label = tk.Label(text_frame, text=intro_text, fg=TERMINAL_FG, bg=BACKGROUND_COLOR, font=(FONT, 14), justify='left', wraplength=500)
        label.pack(anchor='w')

        # Image area (right side)
        image_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
        image_frame.pack(side='right', padx=40, anchor='n')

        try:
            image = Image.open("infographic.jpg")  # Change file name if needed
            image = image.resize((400, 400), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(image)
            image_label = tk.Label(image_frame, image=self.tk_image, bg=BACKGROUND_COLOR)
            image_label.pack()
        except Exception as e:
            error_label = tk.Label(image_frame, text=f"[IMAGE ERROR] {e}", fg='red', bg=BACKGROUND_COLOR, font=(FONT, 12))
            error_label.pack()

        # Bottom button
        button_frame = tk.Frame(self.frame, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=20)

        start_btn = tk.Button(button_frame, text='▶ Start Demo', bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, font=(FONT, 14), width=20, command=self.switch_callback)
        start_btn.pack()

    def destroy(self):
        self.frame.destroy()

# --- John the Ripper Demo Screen ---

class JohnDemo:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg=BACKGROUND_COLOR, width=1280, height=720)
        self.frame.pack()

        label = tk.Label(self.frame, text='🛠️ John the Ripper Password Cracking Demo', fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, font=(FONT, 18))
        label.place(relx=0.5, y=20, anchor='n')

        self.terminal_output = tk.Text(self.frame, bg=TERMINAL_BG, fg=TERMINAL_FG, insertbackground=TERMINAL_FG, font=(FONT, 12), wrap='word', width=100, height=20)
        self.terminal_output.place(relx=0.5, rely=0.5, anchor='center')
        self.terminal_output.config(state='disabled')

        btn1 = tk.Button(self.frame, text='📘 Basic john usage', bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30, command=self.basic_john)
        btn1.place(relx=0.25, rely=0.2, anchor='center')

        btn2 = tk.Button(self.frame, text='🗂️ Zip File Hash Cracking', bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30, command=self.zip_crack)
        btn2.place(relx=0.5, rely=0.2, anchor='center')

        btn3 = tk.Button(self.frame, text='🔓 Show Cracked Passwords', bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30, command=self.show_cracked)
        btn3.place(relx=0.75, rely=0.2, anchor='center')

    def basic_john(self):
        append_terminal_text(self.terminal_output, '[STEP 1] Learning the basics of John the Ripper...')
        append_terminal_text(self.terminal_output, '> john --help')
        output = run_command('john --help')
        append_terminal_text(self.terminal_output, output)

    def zip_crack(self):
        run_command("rm ~/.john/john.pot")
        append_terminal_text(self.terminal_output, '[STEP 2] Extracting hash from encrypted zip file...')
        append_terminal_text(self.terminal_output, '> zip2john secret.zip > zip_hash.txt')
        output = run_command("zip2john secret.zip > zip_hash.txt")
        append_terminal_text(self.terminal_output, '[INFO] Hash saved to zip_hash.txt')
        append_terminal_text(self.terminal_output, '[STEP 3] Cracking password using a wordlist...')
        append_terminal_text(self.terminal_output, '> john --wordlist=/usr/share/wordlists/john.lst zip_hash.txt')
        output = run_command("john --wordlist=/usr/share/wordlists/john.lst zip_hash.txt")
        append_terminal_text(self.terminal_output, output)

    def show_cracked(self):
        append_terminal_text(self.terminal_output, '[STEP 4] Displaying cracked passwords...')
        append_terminal_text(self.terminal_output, '> john --show zip_hash.txt')
        output = run_command('john --show zip_hash.txt')
        append_terminal_text(self.terminal_output, output)

    def destroy(self):
        self.frame.destroy()

# --- Main Application Control ---

def main():
    root = tk.Tk()
    root.title('Hash Cracking Tutorial')
    root.geometry('1280x720')
    root.configure(bg=BACKGROUND_COLOR)

    intro = None
    demo = None

    def switch_to_demo():
        nonlocal intro, demo
        if intro:
            intro.destroy()
        demo = JohnDemo(root)

    intro = IntroScreen(root, switch_to_demo)
    root.mainloop()

if __name__ == '__main__':
    main()
