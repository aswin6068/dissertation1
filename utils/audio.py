import os
import time
import platform
import subprocess
from gtts import gTTS
from pathlib import Path

def convert_text_to_speech(text: str, slow=False):
    text = text[:2000]
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.join(output_folder, f"audio_{int(time.time())}.mp3")
    tts = gTTS(text=text, lang='en', slow=slow)
    tts.save(filename)
    full_path = str(Path(filename).absolute())

    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(full_path)
        elif system == "Darwin":
            subprocess.run(["open", full_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", full_path])
        else:
            print("⚠️ Unsupported OS for audio playback.")
    except Exception as e:
        print(f"⚠️ Audio play failed: {e}")
