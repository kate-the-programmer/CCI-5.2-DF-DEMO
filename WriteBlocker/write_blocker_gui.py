import tkinter as tk
from PIL import Image, ImageTk
import subprocess

FOREGROUND_COLOR = '#BF33C9'
BACKGROUND_COLOR = '#2B092E'

BUTTON_COLOR = '#4A154B'
BUTTON_TEXT_COLOR = '#FFFFFF'

TERMINAL_BG = '#1E1E1E'
TERMINAL_FG = '#BF33C9'

FONT = 'Courier'


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f'[ERROR] {e.stderr.strip()}'


class WriteBlockerIntro:
    def __init__(self, root, switch_to_main):
        self.root = root
        self.switch_to_main = switch_to_main

        # Main frame
        self.frame = tk.Frame(root, bg=BACKGROUND_COLOR, width=1280, height=720)
        self.frame.pack(fill='both', expand=True)

        # Content frame (top half: side-by-side)
        content_frame = tk.Frame(self.frame, bg=BACKGROUND_COLOR)
        content_frame.pack(pady=40, expand=True)

        # Text area (left side)
        text_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
        text_frame.pack(side='left', padx=40, anchor='n')

        title = tk.Label(text_frame, text='🔒 What is a Write Blocker?', fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, font=(FONT, 20))
        title.pack(pady=(0, 20), anchor='w')

        intro_text = (
            "🧰 What is a Write Blocker?\n"
            " A write blocker is a device or software that prevents any write access to a digital storage device.\n\n"
            "🛠️ Why is it needed?\n"
            "This is essential in forensic investigations to ensure evidence is not modified during examination.\n\n"
            "🧪 What will we do?\n"
            "This demo will walk through checking if an SSD is write-protected using various Linux commands."
        )

        label = tk.Label(text_frame, text=intro_text, fg=TERMINAL_FG, bg=BACKGROUND_COLOR, font=(FONT, 14), justify='left', wraplength=500)
        label.pack(anchor='w')

        # Image area (right side)
        image_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
        image_frame.pack(side='right', padx=40, anchor='n')

        try:
            image = Image.open("lock.png")  # Change file name if needed
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

        start_btn = tk.Button(button_frame, text='▶ Start Demo', bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, font=(FONT, 14), width=20, command=self.switch_to_main)
        start_btn.pack()

        self.try_create_secret_file()

    def try_create_secret_file(self):
        try:
            with open('/mnt/ssd/evidence.txt', 'w') as f:
                f.write('This is secret content\n')
            print('[INFO] Secret evidence file created successfully.')
        except Exception as e:
            print(f'[ERROR] Could not create secret evidence file: {e}')


class WriteBlockerDemo:
    def __init__(self, root):
        self.root = root
        self.root.title('🔒 Write Blocker Demo')
        self.root.configure(width=1280, height=720, bg=BACKGROUND_COLOR)

        label = tk.Label(root, text='🧪 Write Blocker Demo',
                         fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR,
                         font=(FONT, 18))
        label.place(relx=0.5, y=20, anchor='n')

        self.terminal_output = tk.Text(root, bg=TERMINAL_BG, fg=TERMINAL_FG,
                                       insertbackground=TERMINAL_FG, font=(FONT, 12),
                                       wrap='word', width=100, height=20)
        self.terminal_output.place(relx=0.5, rely=0.55, anchor='center')
        self.terminal_output.config(state='disabled')

        self.add_buttons()

    def append_terminal_text(self, message):
        self.terminal_output.config(state='normal')
        self.terminal_output.insert(tk.END, message + '\n')
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state='disabled')

    def add_buttons(self):
        btn_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        btn_frame.place(relx=0.5, rely=0.2, anchor='center')

        tk.Button(btn_frame, text='🧩 Check SSD Connection', bg=BUTTON_COLOR,
                  fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30,
                  command=self.check_ssd).grid(row=0, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text='🪵 View dmesg Logs', bg=BUTTON_COLOR,
                  fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30,
                  command=self.check_dmesg).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(btn_frame, text='🔎 Check RO Flag (lsblk)', bg=BUTTON_COLOR,
                  fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30,
                  command=self.check_ro_flag).grid(row=1, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text='📄 Check Mount Options', bg=BUTTON_COLOR,
                  fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=30,
                  command=self.check_mount).grid(row=1, column=1, padx=10, pady=5)

        tk.Button(btn_frame, text='✍️ Try Write to /mnt/ssd/evidence.txt', bg=BUTTON_COLOR,
                  fg=BUTTON_TEXT_COLOR, font=(FONT, 12), width=62,
                  command=self.try_write_to_evidence).grid(row=2, column=0, columnspan=2, pady=10)

    def check_ssd(self):
        self.append_terminal_text('🧩 Checking SSD connection...')
        output = run_command('lsblk')
        self.append_terminal_text(output)

    def check_dmesg(self):
        self.append_terminal_text('🪵 Checking kernel messages...')
        output = run_command('sudo dmesg | tail')
        self.append_terminal_text(output)

    def check_ro_flag(self):
        self.append_terminal_text('🔎 Checking read-only status (lsblk)...')
        output = run_command('lsblk -o NAME,RO,SIZE,MOUNTPOINT')
        self.append_terminal_text(output)

    def check_mount(self):
        self.append_terminal_text('📄 Checking mount options...')
        output = run_command('mount | grep /mnt/ssd')
        self.append_terminal_text(output if output else '⚠️ /mnt/ssd not mounted?')

    def try_write_to_evidence(self):
        self.append_terminal_text('✍️ Attempting to write to /mnt/ssd/evidence.txt...')
        try:
            with open('/mnt/ssd/evidence.txt', 'w') as f:
                f.write('Test write to evidence file.\n')
            self.append_terminal_text('✅ Write succeeded. The device may NOT be write-protected.')
        except PermissionError:
            self.append_terminal_text('🚫 PermissionError: Device is likely write-protected.')
        except OSError as e:
            self.append_terminal_text(f'❌ {e}')


def main():
    root = tk.Tk()
    root.geometry('1280x720')
    root.configure(bg=BACKGROUND_COLOR)

    def switch_to_main():
        for widget in root.winfo_children():
            widget.destroy()
        WriteBlockerDemo(root)

    WriteBlockerIntro(root, switch_to_main)
    root.mainloop()


if __name__ == '__main__':
    main()
