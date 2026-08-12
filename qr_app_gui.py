# Imports for gui and computer vision
import os
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode

# Paths to icon files
path1 = os.path.join("img", "app1_icon.png")
path2 = os.path.join("img", "generator_icon.png")

# Global image storage variable
image = None

# Main window setup
window = tk.Tk()
window.title("QR Code Utility Suite")
window.geometry("500x620")

# Set titlebar icon photo
try:
    photo1 = ImageTk.PhotoImage(Image.open(path1).resize((32, 32)))
    window.iconphoto(False, photo1)
except Exception:
    pass

# Function to generate qr code
def make():
    global image
    data = entry.get().strip()
    if not data:
        label2.config(text="Please enter text first", foreground="red")
        return
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    photo = ImageTk.PhotoImage(image.resize((200, 200)))
    label3.config(image=photo)
    label3.image = photo
    label2.config(text="Here is your QR code", foreground="green")

# Function to clear user input
def clear():
    global image
    entry.delete(0, tk.END)
    label3.config(image="")
    label3.image = None
    image = None
    label2.config(text="Enter text and click generate", foreground="black")

# Function to save image file
def save():
    global image
    if image is None:
        messagebox.showwarning("Warning", "Generate QR code first")
        return
    file = filedialog.asksaveasfilename(defaultextension=".png")
    if file:
        image.save(file)
        label2.config(text="Saved successfully", foreground="blue")

# Function to scan image file
def scan():
    file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if file:
        full = os.path.abspath(file)
        read = cv2.imread(full)
        tool = cv2.QRCodeDetector()
        data, bbox, _ = tool.detectAndDecode(read)
        if data:
            label4.config(text=f"Scanned Result:\n{data}", foreground="green")
        else:
            label4.config(text="No QR code found in image", foreground="red")

# Function to scan live webcam
def live():
    camera = cv2.VideoCapture(0)
    tool = cv2.QRCodeDetector()
    status = "No QR code scanned"
    while True:
        check, frame = camera.read()
        if not check:
            break
        data, bbox, _ = tool.detectAndDecode(frame)
        if data:
            status = data
            label4.config(text=f"Scanned Result:\n{data}", foreground="green")
            break
        cv2.imshow("Live QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty("Live QR Scanner", cv2.WND_PROP_VISIBLE) < 1:
            break
    camera.release()
    cv2.destroyAllWindows()

# Notebook and tab setup
tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, padx=10, pady=10)
tab1 = ttk.Frame(tabs)
tabs.add(tab1, text="QR Generator")
tab2 = ttk.Frame(tabs)
tabs.add(tab2, text="QR Scanner")

# Widgets for generator tab
label1 = ttk.Label(tab1, text="Enter Text or URL:")
label1.pack(pady=(15, 5))

entry = ttk.Entry(tab1, width=40)
entry.pack(pady=5)

frame = ttk.Frame(tab1)
frame.pack(pady=10)

try:
    photo2 = ImageTk.PhotoImage(Image.open(path2).resize((20, 20)))
except Exception:
    photo2 = None

button1 = ttk.Button(frame, text=" Generate QR Code", image=photo2, compound="left", command=make)
button1.grid(row=0, column=0, padx=5)

button2 = ttk.Button(frame, text="Clear", command=clear)
button2.grid(row=0, column=1, padx=5)

label2 = ttk.Label(tab1, text="Enter text and click generate", font=("Arial", 10, "italic"))
label2.pack(pady=5)

label3 = ttk.Label(tab1)
label3.pack(pady=5)

button3 = ttk.Button(tab1, text="Save QR Code", command=save)
button3.pack(pady=10)

# Widgets for scanner tab
button4 = ttk.Button(tab2, text="Scan Image File", command=scan)
button4.pack(pady=20)

button5 = ttk.Button(tab2, text="Scan with Webcam", command=live)
button5.pack(pady=10)

label4 = ttk.Label(tab2, text="No QR code scanned yet", font=("Arial", 10, "italic"), wraplength=400, justify="center")
label4.pack(pady=30)

# Start main event loop
window.mainloop()