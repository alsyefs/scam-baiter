import io
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
from globals import OPENAI_API_KEY, TTS_MP3_PATH, TTS_WAV_PATH
import httpx
import os
import requests
from time import time
import wave
import audioop
import base64
from pathlib import Path
# import pyaudio

def downsample_wav():
    outrate=8000
    src_path = TTS_WAV_PATH
    dst_path = Path(TTS_WAV_PATH).with_stem(Path(TTS_WAV_PATH).stem + "_downsampled")
    with wave.open(str(src_path), 'rb') as src_wave:
        nchannels, sampwidth, framerate, nframes, comptype, compname = src_wave.getparams()
        if nchannels != 1:  # Ensure the file is mono
            raise ValueError("Audio file must be mono")
        data = src_wave.readframes(nframes)  # Read frames and convert to bytes
        converted = audioop.ratecv(data, sampwidth, nchannels, framerate, outrate, None)[0]
        with wave.open(str(dst_path), 'wb') as dst_wave:  # Ensure dst_path is a string
            dst_wave.setnchannels(nchannels)
            dst_wave.setsampwidth(sampwidth)
            dst_wave.setframerate(outrate)
            dst_wave.writeframes(converted)
    os.replace(str(dst_path), str(TTS_WAV_PATH))
    # Convert downsampled WAV to mu-law encoding
    with wave.open(str(TTS_WAV_PATH), 'rb') as wav_file:
        nchannels, sampwidth, framerate, nframes, comptype, compname = wav_file.getparams()
        frames = wav_file.readframes(nframes)
        # Convert PCM frames to mu-law
        mu_law_frames = audioop.lin2ulaw(frames, sampwidth)
        # Base64 encode the mu-law frames
        audio_base64 = base64.b64encode(mu_law_frames).decode('utf-8')
    return audio_base64

async def tts_openai_async(text: str = "I am sorry, but I could not get that.", voice: str = "alloy"):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f'Bearer {OPENAI_API_KEY}'}
    data = {"model": "tts-1", "input": text, "voice": voice, "response_format": "wav"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Here, instead of playing the audio, we return it as a BytesIO object
            return io.BytesIO(response.content)
        else:
            # Handle error or unsuccessful response
            print(f"Error: {response.status_code}")
            return None
    # start_time = time()
    # response = requests.post(url, headers=headers, json=data, stream=True)
    # if response.status_code == 200:
    #     print(f"Time to first byte: {int((time() - start_time) * 1000)} ms")
    #     p = pyaudio.PyAudio()
    #     stream = p.open(format=8, channels=1, rate=24000, output=True)
    #     for chunk in response.iter_content(chunk_size=1024):
    #         stream.write(chunk)
    #     print(f"Time to complete: {int((time() - start_time) * 1000)} ms")