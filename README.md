# QR Code Utility Suite

A desktop app built with Python and Tkinter for generating and scanning QR codes, with a built-in history log. Includes a color picker for customizing generated QR codes and support for scanning via image file or live webcam.

## Layout
has three tabs
-Generate qrcode tab
-Scan qrcode tab
_History tab

## UI
-has colourful ui designs
- Uses tkinter interface

## Features

**QR Generator**
- Enter any text or URL and generate a QR code
- Customize the QR code's foreground and background colors
- Save generated QR codes as PNG files on ur laptop
colorful colored  buttons

**QR Scanner**
- Scan QR codes from an image file
- Scan QR codes live using your webcam
- Copy scanned results to clipboard
- Open scanned URLs directly in your browser
linked to ur webbrowser

**History & Logs**
- Every generated and scanned code is logged with a timestamp
- Export the full history to a `.txt` file

## Requirements

- Python 3.9+
- A webcam (optional, only needed for live scanning)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Blessing-co/QR-CODE-SCANNER.git
   cd QR-CODE-SCANNER
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the app:
```bash
python qr_app_gui.py
```

- **Generate a QR code:** Go to the *QR Generator* tab, type your text or URL, optionally pick custom colors, then click **Generate QR Code**. Click **Save QR Code** to export it as a PNG.
- **Scan a QR code:** Go to the *QR Scanner* tab and either upload an image file or use your webcam to scan live.
- **View history:** Go to the *History & Logs* tab to see a timestamped log of everything generated and scanned. Click **Export History** to save it as a text file.

## Project Structure

```
QR-CODE-SCANNER/
├── qr_app_gui.py       # Main application
├── requirements.txt    # Python dependencies
├── .gitignore
├── img/                 # App icons
└── README.md
```

## Built With

- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI framework
- [OpenCV](https://opencv.org/) — QR code detection and webcam access
- [qrcode](https://pypi.org/project/qrcode/) — QR code generation
- [Pillow](https://python-pillow.org/) — image handling

## Notes

- Live webcam scanning requires a connected camera; the app will show an error if none is available.
- Press `q` while the webcam window is active to exit live scanning.


