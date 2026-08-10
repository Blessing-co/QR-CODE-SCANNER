import os
import re
import qrcode
import cv2

# ===================================================
# HELPER FUNCTION: SAFE FILENAME CREATION (Q1)
# ===================================================
def sanitize_filename(text: str) -> str:
    """
    Converts a URL or text string into a clean, safe filename.
    Removes http/https headers and replaces invalid OS characters with '_'.
    """
    clean = text.replace("https://", "").replace("http://", "")
    clean = re.sub(r'[^\w\.-]', '_', clean)
    return clean[:30] + ".png"


# ===================================================
# FEATURE 1: QR CODE GENERATOR (Q1 & Q2)
# ===================================================
def generate_qr_code(data: str, folder_name: str = "my_qr_codes", fill_color="black", back_color="white"):
    """
    Generates a QR code and saves it inside a specified folder with a safe filename.
    """
    if not data.strip():
        print("Error: Input text cannot be empty.")
        return False

    # Create destination folder if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)

    # Derive clean filename and build full path
    filename = sanitize_filename(data)
    full_path = os.path.join(folder_name, filename)

    # Configure QR Matrix
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Generate image, convert to RGB, and save
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    rgb_img = img.convert("RGB")
    rgb_img.save(full_path)

    print(f"Success: Saved QR code to '{full_path}'")
    return full_path


# ===================================================
# FEATURE 2: SCAN FROM IMAGE FILE (Q3)
# ===================================================
def scan_qr_from_file(image_path: str):
    """
    Scans and decodes a QR code from any image file path (relative or absolute).
    """
    full_path = os.path.abspath(image_path)

    if not os.path.exists(full_path):
        print(f"Error: File not found at '{full_path}'")
        return None

    img = cv2.imread(full_path)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        print(f"Decoded Data: {data}")
        return data
    else:
        print(f"No QR code detected in '{full_path}'.")
        return None


# ===================================================
# FEATURE 3: LIVE WEBCAM SCANNER (Q5)
# ===================================================
def scan_qr_from_webcam():
    """
    Opens the webcam and scans QR codes live in a video feed.
    Only prints new QR codes to prevent spamming.
    Closes on 'q' key or when clicking the window's 'X' exit button.
    """
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    last_scanned = ""
    latest_result = None
    window_name = "Live QR Scanner"

    print("Camera active. Press 'q' or click the 'X' button on the camera window to exit.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Could not access camera.")
            break

        data, bbox, _ = detector.detectAndDecode(frame)

        # Print only if a new/different QR code is detected
        if data and data != last_scanned:
            print(f"New Scan Detected: {data}")
            last_scanned = data
            latest_result = data

        cv2.imshow(window_name, frame)

        # Exit condition 1: User pressed 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Exit condition 2: User clicked the window's 'X' close button
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()
    return latest_result


# ===================================================
# FEATURE 4: PERSISTENT INTERACTIVE MENU (Q4)
# ===================================================
if __name__ == "__main__":
    while True:
        print("\n--- QR CODE TOOLKIT MENU ---")
        print("1. Generate QR Code")
        print("2. Scan Image File")
        print("3. Scan via Webcam")
        print("4. Exit Program")

        choice = input("\nSelect an option (1-4): ")

        if choice == "1":
            user_text = input("Enter text or URL to encode: ")
            folder = input("Enter folder name (press Enter for 'my_qr_codes'): ").strip()
            folder = folder if folder else "my_qr_codes"
            generate_qr_code(user_text, folder_name=folder)

        elif choice == "2":
            path = input("Enter image file path (e.g., my_qr_codes/www.google.com.png): ")
            scan_qr_from_file(path)

        elif choice == "3":
            scan_qr_from_webcam()

        elif choice == "4":
            print("Exiting QR Code Toolkit. Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")