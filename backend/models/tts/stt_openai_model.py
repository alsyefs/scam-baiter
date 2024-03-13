import os
from openai import OpenAI
from globals import STT_MP3_PATH, OPENAI_API_KEY
from logs import LogManager
log = LogManager.get_logger()
import subprocess

def check_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log.error("ffmpeg is not installed or not found in PATH.")
        return False
    
def convert_to_supported_format(input_path, output_path):
    # command = ['ffmpeg', '-i', input_path, '-acodec', 'libmp3lame', output_path]
    command = ['ffmpeg', '-v', 'error', '-i', input_path, '-acodec', 'libmp3lame', output_path]
    subprocess.run(command, check=True)

def stt_openai_decoded_audio(decoded_audio):
    if not check_ffmpeg_installed():
        return "FFmpeg is required for conversion."
    audio_filename = STT_MP3_PATH
    converted_audio_path = audio_filename.replace(".mp3", "_converted.mp3")
    with open(audio_filename, "wb") as audio_file:
        audio_file.write(decoded_audio)
    convert_to_supported_format(audio_filename, converted_audio_path)
    with open(converted_audio_path, "rb") as audio_file:
        client = OpenAI(api_key=OPENAI_API_KEY)
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text"
        )
    print(transcription.text)
    return transcription.text

def stt_openai_audio_file(audio_file_path):
    client = OpenAI(api_key=OPENAI_API_KEY)
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=STT_MP3_PATH, 
    response_format="text"
    )
    print(transcription.text)
    return transcription.text