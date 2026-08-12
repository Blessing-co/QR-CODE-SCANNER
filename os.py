import os
if os.path.exists("my_qr_codes"):
    print("Folder is ready!")
else:
    print("folder not found)")    

full_path = os.path.abspath("my_qr_codes/google.png")
print(full_path)
# Output: "C:\Users\YourName\Projects\my_qr_codes\google.png"

print(os.getcwd())

files = os.listdir("QRcodescsnner")
print(files)
# Output: ['www_google_com.png', 'www_github_com.png']