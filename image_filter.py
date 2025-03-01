import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, ttk, simpledialog
from PIL import Image, ImageTk
# Initialize Tkinter window
root = Tk()
root.title("Image Filter App")
root.geometry("850x750")
root.configure(bg="#2C2F33")  # Dark mode background
# Global variables
original_image = None
filtered_image = None
undo_stack = []
# Convert image to Tkinter format
def convert_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    return ImageTk.PhotoImage(img)
# Load image function
def load_image():
    global original_image, filtered_image
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        original_image = cv2.imread(file_path)
        original_image = cv2.resize(original_image, (500, 400))
        filtered_image = original_image.copy()
        update_image(original_image)
        status_label.config(text=f"Loaded: {file_path.split('/')[-1]} | {original_image.shape[1]}x{original_image.shape[0]} px")
# Apply filter function
def apply_filter(filter_name):
    global filtered_image, undo_stack
    if original_image is None:
        return
    undo_stack.append(filtered_image.copy())  # Save the current image before applying a filter
    if filter_name == "Grayscale":
        filtered_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2RGB)
    elif filter_name == "Blur":
        filtered_image = cv2.GaussianBlur(original_image, (15, 15), 0)
    elif filter_name == "Edges":
        filtered_image = cv2.Canny(original_image, 100, 200)
        filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2RGB)
    elif filter_name == "Sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        filtered_image = cv2.filter2D(original_image, -1, kernel)
    elif filter_name == "Pencil Sketch":
        gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        inv_gray = 255 - gray
        blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        filtered_image = cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)
    update_image(filtered_image)
# Undo function
def undo():
    global filtered_image
    if undo_stack:
        filtered_image = undo_stack.pop()
        update_image(filtered_image)
# Resize image function (Modified to prompt for width and height at once)
def resize_image():
    if filtered_image is None:
        return
    # Ask for width and height together
    resize_input = simpledialog.askstring("Resize Image", "Enter width and height (e.g., 800x600):")
    if resize_input:
        try:
            width, height = map(int, resize_input.split('x'))
            resized_image = cv2.resize(filtered_image, (width, height))
            update_image(resized_image)
        except ValueError:
            status_label.config(text="Invalid input! Please enter in the format width x height.")
# Adjust brightness and contrast
def adjust_brightness_contrast(brightness=1, contrast=1):
    global filtered_image
    if original_image is None:
        return
    
    adjusted_image = cv2.convertScaleAbs(original_image, alpha=contrast, beta=brightness)
    filtered_image = adjusted_image
    update_image(filtered_image)
def on_brightness_change(val):
    brightness = int(val)
    adjust_brightness_contrast(brightness=brightness)
def on_contrast_change(val):
    contrast = int(val)
    adjust_brightness_contrast(contrast=contrast)
# Reset image function
def reset_image():
    global filtered_image
    filtered_image = original_image.copy()
    update_image(filtered_image)
# Save image function
def save_image():
    if filtered_image is None:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")])
    if file_path:
        cv2.imwrite(file_path, filtered_image)
        status_label.config(text=f"Saved: {file_path.split('/')[-1]}")
# Update displayed image
def update_image(img):
    tk_img = convert_image(img)
    image_label.config(image=tk_img)
    image_label.image = tk_img
# Styling with ttk
style = ttk.Style()
style.configure("TButton", font=("Arial", 12, "bold"), padding=10, background="#333")
# UI Layout
button_frame = Frame(root, bg="#23272A")
button_frame.pack(pady=15)
buttons = [
    ("Grayscale", "#808080"),
    ("Blur", "#3498DB"),
    ("Edges", "#E74C3C"),
    ("Sharpen", "#27AE60"),
    ("Pencil Sketch", "#D4AC0D")
]
for text, color in buttons:
    btn = Button(button_frame, text=text, bg=color, fg="white", width=12, height=2, relief=RAISED,
                 font=("Arial", 12, "bold"), command=lambda t=text: apply_filter(t))
    btn.pack(side=LEFT, padx=10)
    
    # Hover effect
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="white", fg="black"))
    btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c, fg="white"))
# Buttons for Load, Save, Undo, Resize, Brightness, Contrast, and Reset (Horizontal layout)
action_button_frame = Frame(root, bg="#23272A")
action_button_frame.pack(pady=10)
Button(action_button_frame, text="Load Image", bg="#1F1F1F", fg="white", width=12, height=2,
       font=("Arial", 12, "bold"), command=load_image).pack(side=LEFT, padx=5)
Button(action_button_frame, text="Save Image", bg="#1F1F1F", fg="white", width=12, height=2,
       font=("Arial", 12, "bold"), command=save_image).pack(side=LEFT, padx=5)
Button(action_button_frame, text="Undo", bg="#1F1F1F", fg="white", width=12, height=2,
       font=("Arial", 12, "bold"), command=undo).pack(side=LEFT, padx=5)
Button(action_button_frame, text="Resize Image", bg="#1F1F1F", fg="white", width=12, height=2,
       font=("Arial", 12, "bold"), command=resize_image).pack(side=LEFT, padx=5)
# Centered frame for Brightness and Contrast sliders
slider_frame = Frame(root, bg="#2C2F33")
slider_frame.pack(pady=10)
# Centered sliders within the frame
brightness_slider = Scale(slider_frame, from_=0, to_=100, orient=HORIZONTAL, label="Brightness", command=on_brightness_change, bg="#2C2F33", fg="white", font=("Helvetica", 12))
brightness_slider.pack(side=LEFT, padx=20)
contrast_slider = Scale(slider_frame, from_=0, to_=10, orient=HORIZONTAL, label="Contrast", command=on_contrast_change, bg="#2C2F33", fg="white", font=("Helvetica", 12))
contrast_slider.pack(side=LEFT, padx=20)
# Reset image button
Button(action_button_frame, text="Reset Image", bg="#1F1F1F", fg="white", width=12, height=2,
       font=("Arial", 12, "bold"), command=reset_image).pack(side=LEFT, padx=5)
# Image display area
image_label = Label(root, bg="#2C2F33", width=500, height=400, relief="solid", bd=2)
image_label.pack(pady=20)
# Status label
status_label = Label(root, text="", bg="#2C2F33", fg="white", font=("Arial", 10))
status_label.pack(pady=5)
root.mainloop()