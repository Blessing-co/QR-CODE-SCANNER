import qrcode

# Line 1: Define what text or link you want inside the QR code
data = "https://www.cronos.com"

# Line 1: Create a QRCode configuration object
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=4
)

# Line 2: Add your data into the QR object
qr.add_data(data)
qr.make(fit=True)

#customise tge color of the qr code
img = qr.make_image(fill_color=(255, 0, 0), back_color=(255, 255, 200))

# Convert image mode to RGB so JPEG and ICO formats work properly
rgb_img = img.convert("RGB")

# Save in different file formats
rgb_img.save("red_qr.png")  # PNG
rgb_img.save("red_qr.jpg")  # JPEG
rgb_img.save("red_qr.ico")  # ICO