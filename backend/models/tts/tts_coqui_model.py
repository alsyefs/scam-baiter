from globals import (TTS_MP3_PATH, SPEAKER_WAV)
import torch
from TTS.api import TTS # https://github.com/coqui-ai/TTS
import os
from logs import LogManager
log = LogManager.get_logger()

if not os.path.exists(os.path.dirname(TTS_MP3_PATH)):
    os.makedirs(os.path.dirname(TTS_MP3_PATH))
if not os.path.exists(os.path.dirname(SPEAKER_WAV)):
    os.makedirs(os.path.dirname(SPEAKER_WAV))
device = "cuda" if torch.cuda.is_available() else "cpu" # Get device
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device) # Init TTS

def tts_coqui(text: str):
    try:
        tts.tts_to_file(text=text, speaker_wav=SPEAKER_WAV, language="en", file_path=TTS_MP3_PATH)
        return True
    except Exception as e:
        print("Error in tts_coqui:", e)
        log.error(f"Error in tts_coqui: {e}")
        return False

def user_prompt():
    # prompt the user to type something and take that input and call tts_coqui(text=input) and play the mp3 file
    input_text = input("Type something to convert to audio or '0' to exit: ") # get the input from the user
    if input_text == "0":
        exit(0)
    else:
        tts_coqui(text=input_text) # call the tts_coqui function with the input text
        os.system(f"start {TTS_MP3_PATH}")
    user_prompt()

if __name__ == "__main__":
    text = "No, I'm not a model. I'm just an ordinary person. How about you? Are you into modeling?"
    tts_coqui(text=text)
    user_prompt()
    