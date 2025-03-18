import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Import Pillow for image handling

def on_button_click():
    user_input = entry.get()
    messagebox.showinfo("Message", f"You entered: {user_input}")

def open_next_page():
    root.destroy()  # Close the previous page
    create_window("Next Page", "Welcome to the Hacker Terminal!", "write blocker/IMG_1055.jpg", open_third_page)

def open_third_page():
    create_window("Final Page", "You have reached the final level!", "write blocker/IMG_1055.jpg", None)

def create_window(title, label_text, image_path, next_command):
    new_window = tk.Tk()
    new_window.title(title)
    new_window.attributes('-fullscreen', True)  # Make full screen
    new_window.configure(bg="black")  # Set background color
    
    label = tk.Label(new_window, text=label_text, fg="green", bg="black", font=("Courier", 18))
    label.pack(pady=20)
    
    # Load and display an image
    try:
        image = Image.open(image_path)  
        image = image.resize((500, 300))  # Resize if necessary
        photo = ImageTk.PhotoImage(image)
        
        image_label = tk.Label(new_window, image=photo, bg="black")
        image_label.image = photo  # Keep a reference to prevent garbage collection
        image_label.pack(pady=20)
    except Exception as e:
        error_label = tk.Label(new_window, text=f"Error loading image: {e}", fg="red", bg="black")
        error_label.pack(pady=10)
    
    # Add menu
    menu_bar = tk.Menu(new_window)
    new_window.config(menu=menu_bar)
    
    page_menu = tk.Menu(menu_bar, tearoff=0)
    page_menu.add_command(label="Main Page", command=lambda: restart_application(new_window))
    page_menu.add_command(label="Second Page", command=lambda: switch_page(new_window, open_next_page))
    page_menu.add_command(label="Final Page", command=lambda: switch_page(new_window, open_third_page))
    menu_bar.add_cascade(label="Navigate", menu=page_menu)
    
    # Next button (if applicable)
    if next_command:
        next_button = tk.Button(new_window, text="Next", command=lambda: switch_page(new_window, next_command), fg="black", bg="green", font=("Courier", 14))
        next_button.pack(pady=10)
    
    close_button = tk.Button(new_window, text="Close", command=new_window.destroy, fg="black", bg="green", font=("Courier", 14))
    close_button.pack(pady=10)
    
    new_window.mainloop()

def switch_page(current_window, next_function):
    current_window.destroy()
    next_function()

def restart_application(current_window):
    current_window.destroy()
    main()

def main():
    global root
    root = tk.Tk()
    root.title("Write Blocker Demo")
    root.attributes('-fullscreen', True)  # Make full screen
    root.configure(bg="black")  # Set background color

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
    page_menu = tk.Menu(menu_bar, tearoff=0)
    page_menu.add_command(label="Second Page", command=lambda: switch_page(root, open_next_page))
    page_menu.add_command(label="Final Page", command=lambda: switch_page(root, open_third_page))
    menu_bar.add_cascade(label="Navigate", menu=page_menu)
    
    label = tk.Label(root, text="Write Blocker Demo", fg="green", bg="black", font=("Courier", 18))
    label.pack(pady=20)
    
    next_button = tk.Button(root, text="Next", command=open_next_page, fg="black", bg="green", font=("Courier", 14))
    next_button.pack(pady=10)
    
    root.mainloop()

# Start the application
main()
