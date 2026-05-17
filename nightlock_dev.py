import os
import sys
import queue
import json
import ctypes
import sounddevice as sd
import vosk

# Queue for audio data
q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(f"Status Warning: {status}", file=sys.stderr)
    q.put(bytes(indata))

def lock_workstation():
    print("\n>>> TRIGGER WORD DETECTED! Locking Workstation... <<<\n")
    ctypes.windll.user32.LockWorkStation()

def main():
    model_path = "model"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}.")
        return
    
    # Get information about the default microphone to confirm
    try:
        device_info = sd.query_devices(kind='input')
        print("\n" + "="*50)
        print(f"Microphone Selected: {device_info['name']}")
        print("="*50 + "\n")
    except Exception as e:
        print(f"Could not query default microphone: {e}")

    print("Loading model...")
    model = vosk.Model(model_path)
    
    # 16000 Hz is standard for speech recognition models
    samplerate = 16000 
    
    try:
        # device=None tells sounddevice to use the default input device
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, dtype='int16',
                               channels=1, callback=callback):
            
            print("Listening for 'nightlock'... (Speak into your mic!)")
            rec = vosk.KaldiRecognizer(model, samplerate)
            
            while True:
                data = q.get()
                
                # Check if it accepted a full phrase
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get('text', '').lower()
                    if text.strip():
                        print(f"Full Result: '{text}'")
                    
                    trigger_words = [
                        "nightlock", "night lock", "knight lock", 
                        "knightlock", "night log", "knight log",
                        "may look", "natal arc", "new york", "matlock",
                        "malik", "they look", "network", "nine o'clock",
                        "naik walk", "now ugh", "they like", "nighthawk",
                        "night mark", "milk", "nate lot", "nioc",
                        "night org", "nine log", "now what", "nine or"
                    ]
                    
                    if any(trigger in text for trigger in trigger_words):
                        lock_workstation()
                else:
                    # Look at partial text while you are speaking
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').lower()
                    
                    if partial_text.strip():
                        # Using \r overwrites the line so it updates in real time cleanly
                        print(f"Partial: '{partial_text}'", end='\r')
                        
                        trigger_words = [
                            "nightlock", "night lock", "knight lock", 
                            "knightlock", "night log", "knight log",
                            "may look", "natal arc", "new york", "matlock",
                            "malik", "they look", "network", "nine o'clock",
                            "naik walk", "now ugh", "they like", "nighthawk",
                            "night mark", "milk", "nate lot", "nioc",
                            "night org", "nine log", "now what", "nine or"
                        ]
                        
                        if any(trigger in partial_text for trigger in trigger_words):
                            print() # Break the line
                            lock_workstation()
                            # Reset recognizer so it doesn't trigger again immediately on the same partial
                            rec.Reset()
                    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Audio error: {e}")

if __name__ == "__main__":
    main()
