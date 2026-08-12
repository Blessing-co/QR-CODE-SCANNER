import cv2

# Line 1: Connect to your default computer camera (0 = built-in webcam)
cap = cv2.VideoCapture(0)

# Line 2: Create the QR Code Detector
detector = cv2.QRCodeDetector()

print("Camera active. Hold a QR code up to the camera. Press 'q' to quit.")

#variable to store qrcode
scanned_qrcode = ""

# Line 3: Continuous loop to read live camera frames
while True:
    # Line 4: Capture a single frame (picture) from the camera
    success, frame = cap.read()

    # Line 5: Stop if the camera isn't working
    if not success:
        print("Could not read from webcam.")
        break

    # Line 6: Look for a QR code in the current frame
    data, bbox, _ = detector.detectAndDecode(frame)


# Only print if a QR code is found AND it is different from the last one
    if data and data != scanned_qrcode:
        print(f"Scanned New QR Code: {data}")
        scanned_qrcode = data  # Update the scanned QR code

    # Line 8: Show the live camera feed in a window
    cv2.imshow("QR Scanner Window", frame)

    # Line 9: Check every 1ms if the 'q' key was pressed to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Line 10: Turn off the camera and close the window
cap.release()
cv2.destroyAllWindows()