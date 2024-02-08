import os
from pathlib import Path
from openai import OpenAI
from globals import TTS_MP3_PATH, OPENAI_API_KEY
from logs import LogManager
log = LogManager.get_logger()

def tts_openai(text: str, gender: int = 1, accent: str = "us"):    
    client = OpenAI(api_key=OPENAI_API_KEY)
    voices = ["nova", "shimmer", "echo", "onyx", "fable", "alloy"]
    if gender == 1 and accent == "us":
        voices = ["echo", "onyx"]
    elif gender == 1 and accent == "uk":
        voices = ["fable"]
    elif gender == 2 and accent == "us":
        voices = ["alloy", "nova", "shimmer"]
    else:
        voices = ["alloy"]
    response = client.audio.speech.create(
    model="tts-1", # or "tts-1-hd" but double the price and slower
    voice=voices[0],
    input=text
    )
    response.stream_to_file(TTS_MP3_PATH)
    
if __name__ == "__main__":
    print("Testing tts_openai")
    tts_openai("Today is a wonderful day to build something people love!", gender=1, accent="us")
    os.system(f"start {TTS_MP3_PATH}")
    print("Test complete")