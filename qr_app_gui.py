import os
import cv2
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import qrcode

# ==========================================
# MODEL: Data & Processing Engine
# ========
class QRModel:
    def __init__(self):
        self.history_log = []
        self.fill_color = "#000000"
        self.back_color = "#FFFFFF"
        self.current_image = None
        self.qr_detector = cv2.QRCodeDetector()

    def generate_qr(self, data):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color).convert("RGB")
        self.current_image = img
        return img

    def save_image(self, file_path):
        if self.current_image:
            self.current_image.save(file_path)
            return True
        return False

    def scan_static_image(self, file_path):
        read_img = cv2.imread(file_path)
        data, bbox, _ = self.qr_detector.detectAndDecode(read_img)
        return data

    def decode_frame(self, frame):
        data, bbox, _ = self.qr_detector.detectAndDecode(frame)
        return data

    def create_log_entry(self, event_type, payload):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry_text = f"[{timestamp}] [{event_type}] {payload}"
        self.history_log.append(entry_text)
        return entry_text


# ==========================================
# VIEW: Frontend Dashboard
# ==========================================
class QRView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("QR Code Utility Suite")
        self.root.geometry("520x660")
        
        # UI Colors
        self.c_red = "#DC3545"
        self.c_brown = "#8B4513"
        self.c_green = "#28A745"
        self.c_blue = "#0056B3"
        self.c_white = "#FFFFFF"
        self.c_black = "#000000"

        self._load_icons()
        self._build_ui()

    def _load_icons(self):
        try:
            self.photo1 = ImageTk.PhotoImage(Image.open(os.path.join("img", "app1_icon.png")).resize((32, 32)))
            self.root.iconphoto(False, self.photo1)
            self.photo2 = ImageTk.PhotoImage(Image.open(os.path.join("img", "generator_icon.png")).resize((20, 20)))
        except Exception:
            self.photo2 = None

    def _build_ui(self):
        tabs = ttk.Notebook(self.root)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab Frames
        self.tab1 = tk.Frame(tabs)
        self.tab2 = tk.Frame(tabs)
        self.tab3 = tk.Frame(tabs, bg=self.c_white)
        
        tabs.add(self.tab1, text="QR Generator")
        tabs.add(self.tab2, text="QR Scanner")
        tabs.add(self.tab3, text="History & Logs")

        self._build_generator_tab()
        self._build_scanner_tab()
        self._build_history_tab()

    def _build_generator_tab(self):
        upper_frame = tk.Frame(self.tab1, bg=self.c_blue)
        upper_frame.pack(side="top", fill="both", expand=True)
        lower_frame = tk.Frame(self.tab1, bg=self.c_brown)
        lower_frame.pack(side="bottom", fill="both", expand=True)

        tk.Label(upper_frame, text="Enter Text or URL:", bg=self.c_blue, fg=self.c_white, font=("Arial", 11, "bold")).pack(pady=(15, 5))
        self.entry = ttk.Entry(upper_frame, width=40)
        self.entry.pack(pady=5)

        color_frame = tk.Frame(upper_frame, bg=self.c_blue)
        color_frame.pack(pady=5)
        self.fill_btn = tk.Button(color_frame, text="QR Color", bg=self.c_black, fg=self.c_white, width=12, command=self.controller.choose_fill, relief="flat")
        self.fill_btn.grid(row=0, column=0, padx=5)
        self.back_btn = tk.Button(color_frame, text="Background", bg=self.c_white, fg=self.c_black, width=12, command=self.controller.choose_back, relief="flat")
        self.back_btn.grid(row=0, column=1, padx=5)

        holder = tk.Frame(upper_frame, bg=self.c_blue)
        holder.pack(pady=10)
        tk.Button(holder, text=" Generate QR Code", image=self.photo2, compound="left", bg=self.c_green, fg=self.c_white, font=("Arial", 10, "bold"), command=self.controller.generate, relief="flat", padx=10, pady=3).grid(row=0, column=0, padx=5)
        tk.Button(holder, text="Clear", bg=self.c_red, fg=self.c_white, font=("Arial", 10, "bold"), command=self.controller.clear_generator, relief="flat", padx=10, pady=3).grid(row=0, column=1, padx=5)

        self.status_label = tk.Label(lower_frame, text="Enter text and click generate", font=("Arial", 10, "italic"), bg=self.c_brown, fg=self.c_white)
        self.status_label.pack(pady=5)
        self.qr_display = tk.Label(lower_frame, bg=self.c_brown)
        self.qr_display.pack(pady=5)
        tk.Button(lower_frame, text="Save QR Code", bg=self.c_green, fg=self.c_white, font=("Arial", 10, "bold"), command=self.controller.save_qr, relief="flat", padx=15, pady=5).pack(pady=10)

    def _build_scanner_tab(self):
        upper_frame = tk.Frame(self.tab2, bg=self.c_white)
        upper_frame.pack(side="top", fill="both", expand=True)
        lower_frame = tk.Frame(self.tab2, bg=self.c_blue)
        lower_frame.pack(side="bottom", fill="both", expand=True)

        tk.Button(upper_frame, text="Scan Image File", bg=self.c_red, fg=self.c_white, font=("Arial", 10, "bold"), command=self.controller.scan_file, relief="flat", padx=15, pady=5).pack(pady=20)
        tk.Button(upper_frame, text="Scan with Webcam", bg=self.c_red, fg=self.c_white, font=("Arial", 10, "bold"), command=self.controller.scan_live, relief="flat", padx=15, pady=5).pack(pady=10)

        action_frame = tk.Frame(lower_frame, bg=self.c_blue)
        action_frame.pack(pady=10)
        self.copy_btn = tk.Button(action_frame, text="Copy to Clipboard", state="disabled", bg=self.c_green, fg=self.c_white, font=("Arial", 9, "bold"), command=self.controller.copy_result, relief="flat", padx=8, pady=3)
        self.copy_btn.grid(row=0, column=0, padx=5)
        self.url_btn = tk.Button(action_frame, text="Open Link in Browser", state="disabled", bg=self.c_blue, fg=self.c_white, font=("Arial", 9, "bold"), command=self.controller.open_result, relief="flat", padx=8, pady=3)
        self.url_btn.grid(row=0, column=1, padx=5)

        self.scan_result_label = tk.Label(lower_frame, text="No QR code scanned yet", font=("Arial", 12, "bold"), wraplength=420, justify="center", bg=self.c_blue, fg=self.c_white)
        self.scan_result_label.pack(pady=20)

    def _build_history_tab(self):
        self.history_listbox = tk.Listbox(self.tab3, font=("Consolas", 9), selectmode=tk.SINGLE)
        self.history_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(self.tab3, text="Export History (.txt)", bg=self.c_brown, fg=self.c_white, font=("Arial", 10, "bold"), command=self.controller.export_logs, relief="flat", padx=15, pady=5).pack(pady=(0, 10))

    # View Updaters
    def update_qr_image(self, img_tk):
        self.qr_display.config(image=img_tk)
        self.qr_display.image = img_tk

    def clear_qr_image(self):
        self.qr_display.config(image="")
        self.qr_display.image = None

    def update_scan_text(self, text, is_url=False):
        self.scan_result_label.config(text=f"Scanned Result:\n{text}")
        self.copy_btn.config(state="normal")
        self.url_btn.config(state="normal" if is_url else "disabled")


# ==========================================
# CONTROLLER: The Bridge
# ==========================================
class QRController:
    def __init__(self, root):
        self.model = QRModel()
        self.view = QRView(root, self)

    def log_and_update(self, event_type, payload):
        entry = self.model.create_log_entry(event_type, payload)
        self.view.history_listbox.insert(tk.END, entry)
        self.view.history_listbox.yview(tk.END)

    def choose_fill(self):
        chosen = colorchooser.askcolor(title="Select QR Code Color")
        if chosen[1]:
            self.model.fill_color = chosen[1]
            self.view.fill_btn.config(bg=chosen[1])

    def choose_back(self):
        chosen = colorchooser.askcolor(title="Select Background Color")
        if chosen[1]:
            self.model.back_color = chosen[1]
            self.view.back_btn.config(bg=chosen[1])

    def generate(self):
        data = self.view.entry.get().strip()
        if not data:
            self.view.status_label.config(text="Please enter text first")
            return
        
        raw_img = self.model.generate_qr(data)
        img_tk = ImageTk.PhotoImage(raw_img.resize((300, 200)))
        self.view.update_qr_image(img_tk)
        self.view.status_label.config(text="Here is your QR code")
        self.log_and_update("GENERATED", data)

    def clear_generator(self):
        self.view.entry.delete(0, tk.END)
        self.view.clear_qr_image()
        self.model.current_image = None
        self.view.status_label.config(text="Enter text and click generate")

    def save_qr(self):
        if not self.model.current_image:
            messagebox.showwarning("Warning", "Generate QR code first")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            self.model.save_image(file_path)
            self.view.status_label.config(text="Saved successfully")

    def process_scan_result(self, data):
        if data:
            is_url = data.startswith("http://") or data.startswith("https://")
            self.view.update_scan_text(data, is_url)
            self.log_and_update("SCANNED", data)
        else:
            self.view.scan_result_label.config(text="No QR code found")

    def scan_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            data = self.model.scan_static_image(os.path.abspath(file_path))
            self.process_scan_result(data)

    def scan_live(self):
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            messagebox.showerror("Error", "Could not access the webcam.")
            return
            
        while True:
            check, frame = camera.read()
            if not check:
                break
                
            data = self.model.decode_frame(frame)
            if data:
                self.process_scan_result(data)
                break
                
            cv2.imshow("Live QR Scanner (Press 'q' to exit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty("Live QR Scanner (Press 'q' to exit)", cv2.WND_PROP_VISIBLE) < 1:
                break
                
        camera.release()
        cv2.destroyAllWindows()

    def copy_result(self):
        text = self.view.scan_result_label.cget("text").replace("Scanned Result:\n", "")
        if text and text != "No QR code scanned yet":
            self.view.root.clipboard_clear()
            self.view.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Result copied to clipboard!")

    def open_result(self):
        text = self.view.scan_result_label.cget("text").replace("Scanned Result:\n", "")
        webbrowser.open(text)

    def export_logs(self):
        if not self.model.history_log:
            messagebox.showinfo("History", "No history available to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("\n".join(self.model.history_log))
            messagebox.showinfo("Export Success", "History exported successfully!")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = QRController(root)
    root.mainloop()