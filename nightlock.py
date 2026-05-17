import os
import sys
import queue
import json
import ctypes
import threading
import pystray
from PIL import Image, ImageDraw
import sounddevice as sd
import vosk

# Queue for audio data
q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        pass # Ignore status prints
    q.put(bytes(indata))

def lock_workstation():
    ctypes.windll.user32.LockWorkStation()

def listen_loop(model_path, stop_event):
    if not os.path.exists(model_path):
        return

    # Disable vosk logging to console
    vosk.SetLogLevel(-1)

    model = vosk.Model(model_path)
    samplerate = 16000

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)

            while not stop_event.is_set():
                try:
                    data = q.get(timeout=0.5)
                except queue.Empty:
                    continue

                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get('text', '').lower()

                    # Watch for variations of the word.
                    # This voice model is trash so,
                    # lots of acceptable variations.
                    trigger_words = [
                        "nightlock", "night lock", "knight lock",
                        "knightlock", "night log", "knight log",
                        "may look", "natal arc", "new york", "matlock",
                        "malik", "they look", "network", "nine o'clock",
                        "naik walk", "now ugh", "they like", "nighthawk",
                        "night mark", "nate lot", "nioc",
                        "night org", "nine log", "now what", "nine or"
                    ]
                    if any(trigger in text for trigger in trigger_words):
                        lock_workstation()
                else:
                    # We rely on full results to avoid false positives
                    pass

    except Exception as e:
        with open("error.log", "a") as f:
            f.write(f"Audio error: {e}\n")

def create_image():
    # Generate a padlock icon for the tray
    image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    dc = ImageDraw.Draw(image)

    # Padlock body
    dc.rectangle((16, 32, 48, 56), fill=(220, 50, 50))
    # Padlock shackle
    dc.arc((20, 16, 44, 40), start=180, end=0, fill=(200, 200, 200), width=6)
    # Keyhole
    dc.ellipse((28, 40, 36, 48), fill=(0, 0, 0))

    return image

def setup_tray(stop_event):
    def on_quit(icon, item):
        stop_event.set()
        icon.stop()

    icon = pystray.Icon("Nightlock")
    icon.menu = pystray.Menu(pystray.MenuItem("Quit Nightlock", on_quit))
    icon.icon = create_image()
    icon.title = "Nightlock - Listening..."

    icon.run()

def main():
    # Make sure we're in the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    model_path = "model"
    stop_event = threading.Event()

    listener_thread = threading.Thread(target=listen_loop, args=(model_path, stop_event), daemon=True)
    listener_thread.start()

    setup_tray(stop_event)

if __name__ == "__main__":
    main()
