# NightLock

NightLock is a lightweight, voice-activated security utility for Windows. It continuously monitors your microphone for the trigger word **"Nightlock"** and immediately initiates a system workstation lock when detected. 

Built with privacy in mind, NightLock uses **Vosk** for fully offline, on-device speech recognition. No audio data is ever sent to the cloud.

## Target Platform
- **Windows 10 / Windows 11** (relies on `user32.dll` to lock the workstation)

## Features
- **Hands-Free Security:** Instantly lock your PC by simply saying "Nightlock".
- **Privacy-First (Offline):** Voice recognition runs locally on your machine.
- **System Tray Integration:** Runs silently in the background with a convenient system tray icon for easy management.
- **Low Resource Usage:** Uses the lightweight `vosk-model-small-en-us` model.

## Prerequisites
- Python 3.8+
- A working microphone

## Setup Instructions

1. **Clone or Download** this repository.
2. **Create a virtual environment** (recommended):
   ```cmd
   python -m venv venv
   ```
3. **Activate the virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
4. **Install the required dependencies**:
   ```cmd
   pip install vosk sounddevice pystray Pillow
   ```
5. **Download the Voice Model**:
   Run the included script to automatically download and extract the required offline voice model:
   ```cmd
   python download_model.py
   ```

## Usage

There are two main ways to run NightLock:

### 1. Background Mode (Recommended)
Double-click the `start_hidden.vbs` file.
This will start NightLock completely in the background without opening a command prompt window. You will see a small red padlock icon appear in your Windows System Tray. Right-click this icon to quit the application.

### 2. Developer Mode
Double-click the `start_dev.bat` file.
This will open a command prompt window, activate the virtual environment, and run the developer version (`nightlock_dev.py`), which outputs recognition logs to the console. Useful for testing microphone sensitivity and debugging.

## How It Works
Once running, just say **"Nightlock"** near your microphone. The application constantly processes chunks of audio and checks against a list of acoustic approximations (to account for the small offline model's accuracy quirks). When a match is found, it calls the native Windows API (`LockWorkStation`) to instantly secure your PC.
