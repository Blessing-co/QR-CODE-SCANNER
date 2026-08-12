#import tkinter as tk
#from tkinter import messagebox  # New: Brings in the pop-up alert tool
#import cv2
#import qrcode
#from PIL import Image, ImageTk



import re
import time
import queue
import threading
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import cv2
import qrcode
from PIL import Image, ImageTk

URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)

class CameraThread(threading.Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.frame_queue = queue.Queue(maxsize=1)
        self.error_queue = queue.Queue(maxsize=1)
        self._running = threading.Event()
        self.actual_fps = 0.0

    def run(self):
       self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
       if not self.cap.isOpened():
           self.error_queue.put("Could not open webcam...")
           return
       self._running.set()  
       while self._running.is_set():
           ok, frame = self.cap.read()
           if not ok:
              continue
           if self.frame_queue.full():
              try:
                 self.frame_queue.get_nowait()
              except queue.Empty:
                 pass
           self.frame_queue.put(frame)

       self.cap.release()    

    def stop(self):
        self._running.clear()       
              




class Palette:
    BG = "#12131a"

class SimpleQRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My QR App")
        self.root.geometry("500x700")
        self.root.configure(bg=Palette.BG)

        # --- SCANNER SECTION ---
        self.scan_label = tk.Label(root, text="Camera Preview Will Appear Here", bg="grey", width=50, height=15)
        self.scan_label.pack(pady=10)

        self.start_btn = tk.Button(root, text="Start Camera", command=self.start_camera)
        self.start_btn.pack(pady=5)

        self.result_label = tk.Label(root, text="Scanned Data: None", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=10)

        #--Camera thread--
        self.camera_thread = None
        self.camera_active = False

        #--  --
        self.last_decoded = None
        self.last_decoded_time = 0

        # --- GENERATOR SECTION ---
        self.input_box = tk.Entry(root, width=40)
        self.input_box.pack(pady=20)

        self.gen_btn = tk.Button(root, text="Generate QR", command=self.generate_qr)
        self.gen_btn.pack(pady=5)

        self.qr_display = tk.Label(root, text="Generated QR Will Appear Here")
        self.qr_display.pack(pady=10)

        # Variables to hold camera and detector
        self.cap = None
        self.detector = cv2.QRCodeDetector()

    def start_camera(self):
        # Open the default webcam
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        # Read the current frame from the webcam
        if self.cap is not None:
            success, frame = self.cap.read()
            
            if success:
                # 1. Look for a QR code in the frame
                data, _, _ = self.detector.detectAndDecode(frame)
                
                # If we found data, update the text on screen
                if data:
                    self.result_label.config(text="Scanned Data: " + data)

                # 2. Convert the image so Tkinter can display it
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                # Resize so it fits nicely
                img = img.resize((300, 200))
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.scan_label.imgtk = imgtk
                self.scan_label.config(image=imgtk)

            # Loop this function every 50 milliseconds
            self.root.after(50, self.update_frame)

    def generate_qr(self):
        # Get the text from the input box
        user_text = self.input_box.get()
        
        # --- NEW CODE START ---
        # Check if the string is completely empty
        if user_text == "":
            messagebox.showwarning("Empty Input", "Please type something before generating!")
            return 
        # --- NEW CODE END ---
        
        # Create the QR code
        qr_img = qrcode.make(user_text)
        qr_img = qr_img.resize((200, 200))
        
        # Convert to Tkinter image
        imgtk = ImageTk.PhotoImage(image=qr_img)
        
        self.qr_display.imgtk = imgtk
        self.qr_display.config(image=imgtk)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleQRApp(root)
    root.mainloop()