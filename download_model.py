import urllib.request
import zipfile
import os
import ssl

URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
ZIP_PATH = "model.zip"
EXTRACT_DIR = "model"

def main():
    if os.path.exists(EXTRACT_DIR):
        print("Model already exists.")
        return

    # Disable SSL verification to prevent certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("Downloading Vosk model (this may take a minute or two)...")
    with urllib.request.urlopen(URL, context=ctx) as response, open(ZIP_PATH, 'wb') as out_file:
        out_file.write(response.read())
    
    print("Extracting model...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    os.rename("vosk-model-small-en-us-0.15", EXTRACT_DIR)
    os.remove(ZIP_PATH)
    print("Model ready.")

if __name__ == "__main__":
    main()
