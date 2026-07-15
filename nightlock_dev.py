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
            # Grammar-constrained decoding: the recognizer can only ever
            # output "night lock" or [unk], which makes the small model
            # behave like a keyword spotter.
            rec = vosk.KaldiRecognizer(model, samplerate, '["night lock", "[unk]"]')

            while True:
                data = q.get()

                # Check if it accepted a full phrase
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get('text', '').lower()
                    if text.strip():
                        print(f"Full Result: '{text}'")

                    if "night lock" in text:
                        lock_workstation()
                else:
                    # Look at partial text while you are speaking
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '').lower()

                    if partial_text.strip():
                        # Using \r overwrites the line so it updates in real time cleanly
                        print(f"Partial: '{partial_text}'", end='\r')

                        if "night lock" in partial_text:
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
