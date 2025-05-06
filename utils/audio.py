import os
import time
from gtts import gTTS
from pathlib import Path
import tempfile

def convert_text_to_speech(text: str, slow=False):
    try:
        # Limit the input text to a safe length
        text = text[:2000]

        # Create a temporary file for the audio
        temp_dir = tempfile.gettempdir()
        filename = f"audio_{int(time.time())}.mp3"
        file_path = os.path.join(temp_dir, filename)

        # Generate TTS and save to temp file
        tts = gTTS(text=text, lang='en', slow=slow)
        tts.save(file_path)

        return Path(file_path).as_posix()  # Compatible path for Streamlit

    except Exception as e:
        print(f"⚠️ Error generating audio: {e}")
        return None
