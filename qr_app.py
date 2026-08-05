"""
QR Code Studio — Scanner & Generator
--------------------------------------
An advanced Tkinter desktop app for scanning and generating QR codes.

Design decisions are documented inline as Q&A comments — this is how a
senior dev thinks through tradeoffs before writing code, and it's worth
reading these before the code itself.

Requirements (already in your venv):
    opencv-python, qrcode, pillow

Run:
    venv\\Scripts\\activate
    python qr_app.py
"""

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


# ============================================================================
# DESIGN SYSTEM
# ----------------------------------------------------------------------------
# Q: Why hardcode a color palette instead of using default Tk widget colors?
# A: Default Tk widgets look dated (grey, 90s-era). Defining a small, consistent
#    palette up front — and reusing it everywhere — is what makes an app look
#    "designed" rather than "assembled." One source of truth also means
#    changing the theme later is a one-line edit, not a hunt through the file.
# ============================================================================
class Palette:
    BG = "#12131a"          # app background — near-black, easy on the eyes
    PANEL = "#1b1d29"       # card/panel background, one step lighter than BG
    PANEL_ALT = "#242737"   # hover / secondary panel
    BORDER = "#2e3142"
    TEXT = "#f2f3f7"
    TEXT_DIM = "#9497a8"
    ACCENT = "#7c5cff"      # primary brand color (purple)
    ACCENT_HOVER = "#6a4ce0"
    SUCCESS = "#4ade80"
    DANGER = "#f87171"
    MONO_FONT = ("Consolas", 10)
    UI_FONT = ("Segoe UI", 10)
    UI_FONT_BOLD = ("Segoe UI", 10, "bold")
    HEADING_FONT = ("Segoe UI", 16, "bold")


URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


# ============================================================================
# CAMERA THREAD
# ----------------------------------------------------------------------------
# Q: Why not just call cv2.VideoCapture().read() inside the Tkinter after()
#    loop, like a beginner version would?
# A: read() blocks until a frame is ready. On a slow camera or USB webcam,
#    that block can stall the GUI thread long enough to feel laggy or freeze
#    entirely. Running capture on its own thread means frame grabbing never
#    competes with the UI for time — the GUI just asks "what's the latest
#    frame?" and gets an instant answer.
#
# Q: Why a queue of size 1 (always drop old frames) instead of a normal queue?
# A: We only ever care about the *latest* frame for a live preview. If the UI
#    thread is briefly busy, we don't want frames queuing up and then playing
#    back in slow motion — we want it to always show what the camera sees
#    *right now*.
# ============================================================================
class CameraThread(threading.Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.frame_queue = queue.Queue(maxsize=1)
        self.error_queue = queue.Queue(maxsize=1)
        self._running = threading.Event()
        self.cap = None
        self.actual_fps = 0.0

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.error_queue.put("Could not open webcam. Is it in use by another app?")
            return

        self._running.set()
        last_tick = time.time()

        while self._running.is_set():
            ok, frame = self.cap.read()
            if not ok:
                continue

            now = time.time()
            instant_fps = 1.0 / max(now - last_tick, 1e-6)
            self.actual_fps = (self.actual_fps * 0.9) + (instant_fps * 0.1)
            last_tick = now

            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put(frame)

        self.cap.release()

    def stop(self):
        self._running.clear()


# ============================================================================
# MAIN APPLICATION
# ============================================================================
class QRStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Studio")
        self.root.geometry("880x640")
        self.root.minsize(760, 560)
        self.root.configure(bg=Palette.BG)

        self.camera_thread = None
        self.camera_active = False
        self.last_decoded = None
        self.last_decoded_time = 0
        self.qr_detector = cv2.QRCodeDetector()
        self.generated_pil_img = None
        self.fill_color = "#000000"
        self.back_color = "#ffffff"

        self._configure_styles()
        self._build_layout()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------
    # STYLING
    # ------------------------------------------------------------------
    # Q: ttk widgets don't respect bg= the way plain tk widgets do — why
    #    bother with ttk at all instead of just using tk everywhere?
    # A: ttk gives us native-looking, theme-able widgets (Notebook tabs,
    #    Treeview list, buttons with hover states). Plain tk widgets are
    #    easier to color directly but look flat and dated. The right call
    #    is: ttk for structural widgets (tabs, tables, comboboxes), plain
    #    tk for anything needing full custom coloring (buttons, labels).
    # ------------------------------------------------------------------
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=Palette.BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=Palette.PANEL,
            foreground=Palette.TEXT_DIM,
            padding=(16, 10),
            font=Palette.UI_FONT_BOLD,
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", Palette.ACCENT)],
            foreground=[("selected", "#ffffff")],
        )

        style.configure(
            "Treeview",
            background=Palette.PANEL,
            fieldbackground=Palette.PANEL,
            foreground=Palette.TEXT,
            rowheight=26,
            borderwidth=0,
            font=Palette.UI_FONT,
        )
        style.configure(
            "Treeview.Heading",
            background=Palette.PANEL_ALT,
            foreground=Palette.TEXT_DIM,
            borderwidth=0,
            font=Palette.UI_FONT_BOLD,
        )
        style.map("Treeview", background=[("selected", Palette.ACCENT)])

        style.configure(
            "TCombobox",
            fieldbackground=Palette.PANEL_ALT,
            background=Palette.PANEL_ALT,
            foreground=Palette.TEXT,
            arrowcolor=Palette.TEXT,
        )

    def _make_button(self, parent, text, command, kind="primary"):
        """A small factory so every button in the app looks consistent."""
        colors = {
            "primary": (Palette.ACCENT, Palette.ACCENT_HOVER, "#ffffff"),
            "danger": (Palette.DANGER, "#e05555", "#ffffff"),
            "ghost": (Palette.PANEL_ALT, Palette.BORDER, Palette.TEXT),
        }
        bg, hover, fg = colors.get(kind, colors["primary"])

        btn = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=hover, activeforeground=fg,
            font=Palette.UI_FONT_BOLD, relief="flat", bd=0,
            padx=16, pady=8, cursor="hand2",
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------
    def _build_layout(self):
        header = tk.Frame(self.root, bg=Palette.BG)
        header.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(
            header, text="QR Code Studio", font=Palette.HEADING_FONT,
            bg=Palette.BG, fg=Palette.TEXT,
        ).pack(side="left")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.scan_tab = tk.Frame(notebook, bg=Palette.BG)
        self.generate_tab = tk.Frame(notebook, bg=Palette.BG)
        notebook.add(self.scan_tab, text="  Scan  ")
        notebook.add(self.generate_tab, text="  Generate  ")

        self._build_scan_tab()
        self._build_generate_tab()

    # ------------------------------------------------------------------
    # SCAN TAB
    # ------------------------------------------------------------------
    def _build_scan_tab(self):
        container = tk.Frame(self.scan_tab, bg=Palette.BG)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        left = tk.Frame(container, bg=Palette.PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.video_label = tk.Label(left, bg="#000000")
        self.video_label.pack(padx=16, pady=16, fill="both", expand=True)

        controls = tk.Frame(left, bg=Palette.PANEL)
        controls.pack(pady=(0, 16))

        self.toggle_btn = self._make_button(controls, "Start Camera", self.toggle_camera)
        self.toggle_btn.pack(side="left", padx=6)

        self.fps_var = tk.StringVar(value="")
        tk.Label(
            controls, textvariable=self.fps_var, bg=Palette.PANEL,
            fg=Palette.TEXT_DIM, font=Palette.MONO_FONT,
        ).pack(side="left", padx=12)

        right = tk.Frame(container, bg=Palette.PANEL)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            right, text="Scan History", font=Palette.UI_FONT_BOLD,
            bg=Palette.PANEL, fg=Palette.TEXT,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        columns = ("time", "content")
        self.history_tree = ttk.Treeview(
            right, columns=columns, show="headings", height=12
        )
        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("content", text="Content")
        self.history_tree.column("time", width=70, anchor="w")
        self.history_tree.column("content", width=200, anchor="w")
        self.history_tree.pack(fill="both", expand=True, padx=16)
        self.history_tree.bind("<Double-1>", self._on_history_double_click)

        action_row = tk.Frame(right, bg=Palette.PANEL)
        action_row.pack(fill="x", padx=16, pady=12)
        self._make_button(action_row, "Copy", self._copy_selected, kind="ghost").pack(side="left")
        self._make_button(action_row, "Open Link", self._open_selected, kind="ghost").pack(side="left", padx=8)

        tk.Label(
            right, text="Double-click an entry to copy it, or open it if it's a link.",
            bg=Palette.PANEL, fg=Palette.TEXT_DIM, font=("Segoe UI", 8),
            wraplength=220, justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Maps Treeview row id -> full decoded string (cells truncate visually)
        self.scan_records = {}

    def toggle_camera(self):
        if not self.camera_active:
            self.camera_thread = CameraThread(camera_index=0)
            self.camera_thread.start()
            self.camera_active = True
            self.toggle_btn.config(text="Stop Camera")
            self.root.after(200, self._check_camera_started)
        else:
            self._stop_camera()

    def _check_camera_started(self):
        """Give the thread a moment to report a startup error, if any."""
        if not self.camera_thread.error_queue.empty():
            err = self.camera_thread.error_queue.get_nowait()
            messagebox.showerror("Camera Error", err)
            self._stop_camera()
            return
        self._poll_camera()

    def _stop_camera(self):
        self.camera_active = False
        self.toggle_btn.config(text="Start Camera")
        if self.camera_thread:
            self.camera_thread.stop()
        self.video_label.config(image="")
        self.fps_var.set("")

    def _poll_camera(self):
        """Runs on the main/UI thread. Pulls the latest frame, decodes,
        updates the preview — then reschedules itself. This is the bridge
        between the background camera thread and the Tkinter event loop."""
        if not self.camera_active:
            return

        try:
            frame = self.camera_thread.frame_queue.get_nowait()
        except queue.Empty:
            frame = None

        if frame is not None:
            data, points, _ = self.qr_detector.detectAndDecode(frame)

            if points is not None:
                pts = points.astype(int).reshape(-1, 2)
                for i in range(len(pts)):
                    cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % len(pts)]), (124, 92, 255), 3)

            if data:
                self._register_scan(data)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((520, 400))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

            self.fps_var.set(f"{self.camera_thread.actual_fps:4.1f} fps")

        self.root.after(15, self._poll_camera)

    def _register_scan(self, data):
        """Add a decoded value to history, but debounce so the same QR
        code held in frame for several seconds doesn't spam 100 entries."""
        now = time.time()
        if data == self.last_decoded and (now - self.last_decoded_time) < 3:
            return
        self.last_decoded = data
        self.last_decoded_time = now

        timestamp = datetime.now().strftime("%H:%M:%S")
        preview = data if len(data) <= 40 else data[:37] + "..."
        row_id = self.history_tree.insert("", 0, values=(timestamp, preview))
        self.scan_records[row_id] = data

    def _on_history_double_click(self, event):
        selected = self.history_tree.focus()
        if not selected:
            return
        data = self.scan_records.get(selected, "")
        if URL_PATTERN.match(data):
            self._open_selected()
        else:
            self._copy_selected()

    def _copy_selected(self):
        selected = self.history_tree.focus()
        if not selected:
            return
        data = self.scan_records.get(selected, "")
        self.root.clipboard_clear()
        self.root.clipboard_append(data)
        messagebox.showinfo("Copied", "Copied to clipboard.")

    def _open_selected(self):
        selected = self.history_tree.focus()
        if not selected:
            return
        data = self.scan_records.get(selected, "")
        if URL_PATTERN.match(data):
            webbrowser.open(data)
        else:
            messagebox.showinfo("Not a link", "This scan result isn't a URL.")

    # ------------------------------------------------------------------
    # GENERATE TAB
    # ------------------------------------------------------------------
    def _build_generate_tab(self):
        container = tk.Frame(self.generate_tab, bg=Palette.BG)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        left = tk.Frame(container, bg=Palette.PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        pad = {"padx": 16, "pady": (14, 4)}

        tk.Label(left, text="Text or URL", font=Palette.UI_FONT_BOLD,
                 bg=Palette.PANEL, fg=Palette.TEXT).pack(anchor="w", **pad)
        self.input_entry = tk.Entry(
            left, font=Palette.UI_FONT, bg=Palette.PANEL_ALT, fg=Palette.TEXT,
            insertbackground=Palette.TEXT, relief="flat",
        )
        self.input_entry.pack(fill="x", padx=16, ipady=6)

        tk.Label(left, text="Error Correction", font=Palette.UI_FONT_BOLD,
                 bg=Palette.PANEL, fg=Palette.TEXT).pack(anchor="w", **pad)
        # Q: why expose error-correction level at all?
        # A: Higher correction (H) lets the code still scan even if ~30% of it
        #    is damaged/obscured — useful if you plan to put a logo in the
        #    middle. Lower correction (L) makes a visually simpler, denser-
        #    looking code. Worth letting the user choose rather than hardcoding.
        self.ec_var = tk.StringVar(value="M (15% recovery)")
        ec_options = [
            "L (7% recovery)", "M (15% recovery)",
            "Q (25% recovery)", "H (30% recovery)",
        ]
        ec_combo = ttk.Combobox(
            left, textvariable=self.ec_var, values=ec_options,
            state="readonly", font=Palette.UI_FONT,
        )
        ec_combo.pack(fill="x", padx=16)

        color_row = tk.Frame(left, bg=Palette.PANEL)
        color_row.pack(fill="x", padx=16, pady=(14, 4))

        fill_col = tk.Frame(color_row, bg=Palette.PANEL)
        fill_col.pack(side="left", expand=True, fill="x")
        tk.Label(fill_col, text="Foreground", font=Palette.UI_FONT_BOLD,
                 bg=Palette.PANEL, fg=Palette.TEXT).pack(anchor="w")
        self.fill_swatch = tk.Button(
            fill_col, bg=self.fill_color, width=8, relief="flat",
            command=lambda: self._pick_color("fill"),
        )
        self.fill_swatch.pack(anchor="w", pady=4)

        back_col = tk.Frame(color_row, bg=Palette.PANEL)
        back_col.pack(side="left", expand=True, fill="x")
        tk.Label(back_col, text="Background", font=Palette.UI_FONT_BOLD,
                 bg=Palette.PANEL, fg=Palette.TEXT).pack(anchor="w")
        self.back_swatch = tk.Button(
            back_col, bg=self.back_color, width=8, relief="flat",
            command=lambda: self._pick_color("back"),
        )
        self.back_swatch.pack(anchor="w", pady=4)

        btn_row = tk.Frame(left, bg=Palette.PANEL)
        btn_row.pack(fill="x", padx=16, pady=20)
        self._make_button(btn_row, "Generate", self.generate_qr).pack(side="left")
        self.save_btn = self._make_button(btn_row, "Save PNG...", self.save_qr, kind="ghost")
        self.save_btn.pack(side="left", padx=8)
        self.save_btn.config(state="disabled")

        right = tk.Frame(container, bg=Palette.PANEL)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Preview", font=Palette.UI_FONT_BOLD,
                 bg=Palette.PANEL, fg=Palette.TEXT).pack(anchor="w", padx=16, pady=(16, 8))
        self.qr_image_label = tk.Label(right, bg=Palette.PANEL)
        self.qr_image_label.pack(expand=True)

    def _pick_color(self, which):
        current = self.fill_color if which == "fill" else self.back_color
        _, hex_color = colorchooser.askcolor(color=current)
        if not hex_color:
            return
        if which == "fill":
            self.fill_color = hex_color
            self.fill_swatch.config(bg=hex_color)
        else:
            self.back_color = hex_color
            self.back_swatch.config(bg=hex_color)

    def generate_qr(self):
        text = self.input_entry.get().strip()
        if not text:
            messagebox.showwarning("Empty input", "Type some text or a URL first.")
            return

        ec_map = {
            "L (7% recovery)": qrcode.constants.ERROR_CORRECT_L,
            "M (15% recovery)": qrcode.constants.ERROR_CORRECT_M,
            "Q (25% recovery)": qrcode.constants.ERROR_CORRECT_Q,
            "H (30% recovery)": qrcode.constants.ERROR_CORRECT_H,
        }
        ec_level = ec_map.get(self.ec_var.get(), qrcode.constants.ERROR_CORRECT_M)

        qr = qrcode.QRCode(box_size=8, border=4, error_correction=ec_level)
        qr.add_data(text)
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color).convert("RGB")

        self.generated_pil_img = pil_img
        preview = pil_img.copy()
        preview.thumbnail((320, 320))
        display_img = ImageTk.PhotoImage(preview)
        self.qr_image_label.imgtk = display_img
        self.qr_image_label.config(image=display_img)
        self.save_btn.config(state="normal")

    def save_qr(self):
        if self.generated_pil_img is None:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG image", "*.png")],
        )
        if filepath:
            self.generated_pil_img.save(filepath)
            messagebox.showinfo("Saved", f"QR code saved to:\n{filepath}")

    # ------------------------------------------------------------------
    def on_close(self):
        if self.camera_thread:
            self.camera_thread.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = QRStudioApp(root)
    root.mainloop()
