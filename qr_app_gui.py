# Imports for GUI tools
import os
import cv2
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import qrcode

# Setup main app colors
color_red = "#DC3545"
color_brown = "#8B4513"
color_green = "#28A745"
color_blue = "#0056B3"
color_white = "#FFFFFF"
color_black = "#000000"
fill_color = "#000000"
back_color = "#FFFFFF"

# Paths to icon files
path1 = os.path.join("img", "app1_icon.png")
path2 = os.path.join("img", "generator_icon.png")


# Global variables
image = None
history_log = []

# Main root window
root = tk.Tk()
root.title("QR Code Utility Suite")
root.geometry("520x660")

# Set app icon photo
try:
    photo1 = ImageTk.PhotoImage(Image.open(path1).resize((32, 32)))
    root.iconphoto(False, photo1)
except Exception:
    pass

# Keeps track of log history
def log_event(event_type, payload):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_text = f"[{timestamp}] [{event_type}] {payload}"
# Choose QR code colordef choose_fill_color():
def choose_fill_color():
    global fill_color
    chosen = colorchooser.askcolor(title="Select QR Code Color")
    if chosen[1]:
        fill_color = chosen[1]
        fill_btn.config(bg=fill_color)

          
def choose_back_color():
    global back_color
    chosen = colorchooser.askcolor(title="Select Background Color")
    if chosen[1]:
        back_color = chosen[1]
        back_btn.config(bg=back_color)

# Choose         

# Function to make QR
def make():
    global image
    data = entry.get().strip()
    if not data:
        label2.config(text="Please enter text first", fg=color_white)
        return
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    qr_code = ImageTk.PhotoImage(image.resize((200, 200)))
    label3.config(image=qr_code)
    label3.image = qr_code
    label2.config(text="Here is your QR code", fg=color_white)
    log_event("GENERATED", data)

# Clear the user input
def clear():
    global image
    entry.delete(0, tk.END)
    label3.config(image="")
    label3.image = None
    image = None
    label2.config(text="Enter text and click generate", fg=color_white)

# Save the image file
def save():
    global image
    if image is None:
        messagebox.showwarning("Warning", "Generate QR code first")
        return
    file = filedialog.asksaveasfilename(defaultextension=".png")
    if file:
        image.save(file)
        label2.config(text="Saved successfully", fg=color_white)

# Update UI with scanned results
def update_scanned_result(data):
    label4.config(text=f"Scanned Result:\n{data}", fg=color_white)
    copy_btn.config(state="normal")
    if data.startswith("http://") or data.startswith("https://"):
        open_url_btn.config(state="normal")
    else:
        open_url_btn.config(state="disabled")
    log_event("SCANNED", data)

# Scan an image file
def scan():
    file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if file:
        full = os.path.abspath(file)
        read = cv2.imread(full)
        tool = cv2.QRCodeDetector()
        data, bbox, _ = tool.detectAndDecode(read)
        if data:
            update_scanned_result(data)
        else:
            label4.config(text="No QR code found in image", fg=color_white)

# Save to clipboard
def copy_to_clipboard():
    text = label4.cget("text").replace("Scanned Result:\n", "")
    if text and text != "No QR code scanned yet":
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("Copied", "Result copied to clipboard!")

# Open in browser
def open_in_browser():
    text = label4.cget("text").replace("Scanned Result:\n", "")
    if text.startswith("http://") or text.startswith("https://"):
        webbrowser.open(text)

# Scan live webcam feed
def live():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        messagebox.showerror("Error", "Could not access the webcam.")
        return
    tool = cv2.QRCodeDetector()
    while True:
        check, frame = camera.read()
        if not check:
            break
        data, bbox, _ = tool.detectAndDecode(frame)
        if data:
            update_scanned_result(data)
            break
        cv2.imshow("Live QR Scanner (Press 'q' to exit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty("Live QR Scanner (Press 'q' to exit)", cv2.WND_PROP_VISIBLE) < 1:
            break
    camera.release()
    cv2.destroyAllWindows()

# Export history log
def export_history():
    if not history_log:
        messagebox.showinfo("History", "No history available to export.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
    if file:
        with open(file, "w") as f:
            f.write("\n".join(history_log))
        messagebox.showinfo("Export Success", "History exported successfully!")    

# --- TABS LAYOUT ---
tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

tab1 = tk.Frame(tabs)
tabs.add(tab1, text="QR Generator")

tab2 = tk.Frame(tabs)
tabs.add(tab2, text="QR Scanner")

tab3 = tk.Frame(tabs, bg=color_white)
tabs.add(tab3, text="History & Logs")

# Colored frame sections
upper_frame_1 = tk.Frame(tab1, bg=color_blue)
upper_frame_1.pack(side="top", fill="both", expand=True)

lower_frame_1 = tk.Frame(tab1, bg=color_brown)
lower_frame_1.pack(side="bottom", fill="both", expand=True)

upper_frame_2 = tk.Frame(tab2, bg=color_white)
upper_frame_2.pack(side="top", fill="both", expand=True)

lower_frame_2 = tk.Frame(tab2, bg=color_blue)
lower_frame_2.pack(side="bottom", fill="both", expand=True)

# --- TAB 1: GENERATOR WIDGETS ---
label1 = tk.Label(upper_frame_1, text="Enter Text or URL:", bg=color_blue, fg=color_white, font=("Arial", 11, "bold"))
label1.pack(pady=(15, 5))

entry = ttk.Entry(upper_frame_1, width=40)
entry.pack(pady=5)

color_frame = tk.Frame(upper_frame_1, bg=color_blue)
color_frame.pack(pady=5)

fill_btn = tk.Button(color_frame, text="QR Color", bg=fill_color, fg=color_white, width=12, command=choose_fill_color, relief="flat")
fill_btn.grid(row=0, column=0, padx=5)

back_btn = tk.Button(color_frame, text="Background", bg=back_color, fg=color_black, width=12, command=choose_back_color, relief="flat")
back_btn.grid(row=0, column=1, padx=5)

holder = tk.Frame(upper_frame_1, bg=color_blue)
holder.pack(pady=10)

try:
    photo2 = ImageTk.PhotoImage(Image.open(path2).resize((20, 20)))
except Exception:
    photo2 = None

# Green Generate Button
button1 = tk.Button(holder, text=" Generate QR Code", image=photo2, compound="left", bg=color_green, fg=color_white, font=("Arial", 10, "bold"), command=make, relief="flat", padx=10, pady=3)
button1.grid(row=0, column=0, padx=5)

# Red Clear Button
button2 = tk.Button(holder, text="Clear", bg=color_red, fg=color_white, font=("Arial", 10, "bold"), command=clear, relief="flat", padx=10, pady=3)
button2.grid(row=0, column=1, padx=5)

# Generator Bottom Frame (Brown)
label2 = tk.Label(lower_frame_1, text="Enter text and click generate", font=("Arial", 10, "italic"), bg=color_brown, fg=color_white)
label2.pack(pady=5)

label3 = tk.Label(lower_frame_1, bg=color_brown)
label3.pack(pady=5)

# Green Save Button
button3 = tk.Button(lower_frame_1, text="Save QR Code", bg=color_green, fg=color_white, font=("Arial", 10, "bold"), command=save, relief="flat", padx=15, pady=5)
button3.pack(pady=10)

# --- TAB 2: SCANNER WIDGETS ---
button4 = tk.Button(upper_frame_2, text="Scan Image File", bg=color_red, fg=color_white, font=("Arial", 10, "bold"), command=scan, relief="flat", padx=15, pady=5)
button4.pack(pady=20)

button5 = tk.Button(upper_frame_2, text="Scan with Webcam", bg=color_red, fg=color_white, font=("Arial", 10, "bold"), command=live, relief="flat", padx=15, pady=5)
button5.pack(pady=10)

action_frame = tk.Frame(lower_frame_2, bg=color_blue)
action_frame.pack(pady=10)

copy_btn = tk.Button(action_frame, text="Copy to Clipboard", state="disabled", bg=color_green, fg=color_white, font=("Arial", 9, "bold"), command=copy_to_clipboard, relief="flat", padx=8, pady=3)
copy_btn.grid(row=0, column=0, padx=5)

open_url_btn = tk.Button(action_frame, text="Open Link in Browser", state="disabled", bg=color_blue, fg=color_white, font=("Arial", 9, "bold"), command=open_in_browser, relief="flat", padx=8, pady=3)
open_url_btn.grid(row=0, column=1, padx=5)

label4 = tk.Label(lower_frame_2, text="No QR code scanned yet", font=("Arial", 12, "bold"), wraplength=420, justify="center", bg=color_blue, fg=color_white)
label4.pack(pady=20)

# --- TAB 3: HISTORY WIDGETS ---
history_listbox = tk.Listbox(tab3, font=("Consolas", 9), selectmode=tk.SINGLE)
history_listbox.pack(fill="both", expand=True, padx=10, pady=10)

export_btn = tk.Button(tab3, text="Export History (.txt)", bg=color_brown, fg=color_white, font=("Arial", 10, "bold"), command=export_history, relief="flat", padx=15, pady=5)
export_btn.pack(pady=(0, 10))

# Run main event loop
root.mainloop()