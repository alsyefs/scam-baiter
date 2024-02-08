# JOSEPH_UK_VOICE_ID = 'Zlb1dXrM653N07WRdFW3'
# MICHAEL_US_VOICE_ID = 'flq6f7yk4E4fJM5XTYuZ'
# To change the voice, check this and copy the voice ID string: https://api.elevenlabs.io/v1/voices
from globals import (ELEVENLABS_API_KEY, TTS_MP3_PATH, ELEVENLABS_PREMADE_VOICES)
import json
import requests
import random
import os

if not os.path.exists(os.path.dirname(TTS_MP3_PATH)):
    os.makedirs(os.path.dirname(TTS_MP3_PATH))

def text_to_speech_mp3(text: str, voice_accent: int, voice_gender: int, voice_age: int):
    with open(ELEVENLABS_PREMADE_VOICES, "r") as f:
        voices = json.load(f)
    accent_labels = {"1": "british", "2": "american"}
    gender_labels = {"1": "male", "2": "female"}
    age_labels = {"1": "young", "2": "middle aged", "3": "old"}
    filtered_voices = [voice for voice in voices["voices"] if
              voice["labels"]["accent"] == accent_labels[str(voice_accent)] and
              voice["labels"]["gender"] == gender_labels[str(voice_gender)] and
              voice["labels"]["age"] == age_labels[str(voice_age)]]
    # sometimes the age is not available, so we need to filter it out
    if not filtered_voices:
        filtered_voices = [voice for voice in voices["voices"] if
                  voice["labels"]["accent"] == accent_labels[str(voice_accent)] and
                  voice["labels"]["gender"] == gender_labels[str(voice_gender)]]
    filtered_voice = filtered_voices[0] # Select a voice from the filtered list
    # filtered_voice = random.choice(filtered_voices) # select a random voice:
    voice_id = filtered_voice["voice_id"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "voice_settings": {
            "similarity_boost": 1,
            "stability": 1
        }
    }
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    with open(TTS_MP3_PATH, "wb") as f:
        f.write(response.content)
    return response.content

if __name__ == "__main__":
    text = "It is me. Or, actually, I mean you. Yes, I represent your voice."
    # ages = {'young': 1, 'middle aged': 2, 'old': 3}
    text_to_speech_mp3(text, 1, 1, 2) # british male
    # text_to_speech(text, 1, 2, 2) # british female
    # text_to_speech(text, 2, 1, 2) # american male
    # text_to_speech(text, 2, 2, 2) # american female