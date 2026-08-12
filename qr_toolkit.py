import os
import re
import qrcode
import cv2

# ===================================================
# Q1 CODE: HELPER FUNCTION FOR SAFE FILENAMES
# ===================================================
def sanitize_filename(text: str) -> str:
    """
    Cleans an input URL or text string so it can be safely used as a filename.
    """
    # Step 1: Remove URL protocol headers
    clean = text.replace("https://", "").replace("http://", "")
    
    # Step 2: Replace any invalid filename character with an underscore
    clean = re.sub(r'[^\w\.-]', '_', clean)
    
    # Step 3: Limit length to 30 characters and add extension
    return clean[:30] + ".png"


# ===================================================
# Q2 CODE: GENERATOR FUNCTION WITH FOLDER SAVING
# ===================================================
def generate_qr_code(data: str, folder_name: str = "my_qr_codes", fill_color="black", back_color="white"):
    """
    Generates a QR code and saves it inside a specified folder using a clean filename.
    """
    # Validation check
    if not data.strip():
        print("Error: Input text cannot be empty.")
        return False

    # Q2: Create folder automatically if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)

    # Q1: Convert raw input text into a safe filename
    filename = sanitize_filename(data)

    # Q2: Combine folder path and filename into one complete path
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

    # Render image and save to full_path
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    rgb_img = img.convert("RGB")
    rgb_img.save(full_path)

    print(f"Success: Saved QR code to '{full_path}'")
    return full_path


# ===================================================
# SCANNER FUNCTION 1: SCAN FROM IMAGE FILE
# ===================================================
def scan_qr_from_file(image_path: str):
    """
    Scans and decodes a QR code from a saved image file.
    """
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return None

    img = cv2.imread(image_path)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        print(f"Decoded Data: {data}")
        return data
    else:
        print("No QR code detected in image.")
        return None


# ===================================================
# SCANNER FUNCTION 2: SCAN FROM WEBCAM
# ===================================================
def scan_qr_from_webcam():
    """
    Opens the webcam and scans QR codes live.
    Only prints new/different QR codes to prevent repeating.
    """
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    last_scanned = ""
    latest_result = None

    print("Camera active. Press 'q' on the camera window to exit.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Could not access camera.")
            break

        data, bbox, _ = detector.detectAndDecode(frame)

        if data and data != last_scanned:
            print(f"New Scan Detected: {data}")
            last_scanned = data
            latest_result = data

        cv2.imshow("Live QR Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return latest_result


# ===================================================
# MAIN MENU
# ===================================================
if __name__ == "__main__":
    print("\n--- QR CODE TOOLKIT ---")
    print("1. Generate QR Code")
    print("2. Scan Image File")
    print("3. Scan via Webcam")

    choice = input("\nSelect an option (1-3): ")

    if choice == "1":
        user_text = input("Enter text or URL to encode: ")
        generate_qr_code(user_text, folder_name="my_qr_codes")
    elif choice == "2":
        file_path = input("Enter image file path (e.g. my_qr_codes/www.google.com.png): ")
        scan_qr_from_file(file_path)
    elif choice == "3":
        scan_qr_from_webcam()
    else:
        print("Invalid choice.")