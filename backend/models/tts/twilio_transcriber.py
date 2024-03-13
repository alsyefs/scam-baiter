import os
from flask import request
import assemblyai as aai
from globals import ASSEMBLYAI_API_KEY, FINAL_TRANSCRIPTIONS, DOMAIN_NAME
import asyncio
from backend.models.tts.tts_openai_model import tts_openai

aai.settings.api_key = ASSEMBLYAI_API_KEY
TWILIO_SAMPLE_RATE = 8000 # Hz

def on_open(session_opened: aai.RealtimeSessionOpened):
    "Called when the connection has been established."
    print("Session ID:", session_opened.session_id)
    FINAL_TRANSCRIPTIONS.clear()

def on_data(transcript: aai.RealtimeTranscript):
    "Called when a new transcript has been received."
    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        FINAL_TRANSCRIPTIONS.clear()
        print(f"isinstance: {transcript.text}", end="\r\n")
        FINAL_TRANSCRIPTIONS.append(transcript.text)
        # tts_openai(transcript.text)
        # asyncio.create_task(tts_openai_async(transcript.text))
        # request.get(f'http://{DOMAIN_NAME}/tts_play_async').content
    else:
        print(f"not instance: {transcript.text}", end="\r")

def on_error(error: aai.RealtimeError):
    "Called when the connection has been closed."
    print("An error occured:", error)

def on_close():
    "Called when the connection has been closed."
    print("Closing Session")

class TwilioTranscriber(aai.RealtimeTranscriber):
    def __init__(self):
        super().__init__(
            on_data=on_data,
            on_error=on_error,
            on_open=on_open, # optional
            on_close=on_close, # optional
            sample_rate=TWILIO_SAMPLE_RATE,
            encoding=aai.AudioEncoding.pcm_mulaw
        )