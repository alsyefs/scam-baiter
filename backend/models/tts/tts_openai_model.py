import io
import os
from pathlib import Path
from openai import OpenAI
from globals import OPENAI_API_KEY, TTS_WAV_PATH, TTS_MP3_PATH
from logs import LogManager
import wave
import audioop
import base64
log = LogManager.get_logger()

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

def tts_openai(text: str = "I am sorry, but I could not get that.", voice: str = "alloy"):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.audio.speech.create(model="tts-1", voice=voice, input=text, response_format="wav")
    response.stream_to_file(TTS_WAV_PATH)
    audio_base64 = downsample_wav()
    return audio_base64


def downsample_and_encode_audio(data, sampwidth, nchannels, framerate, outrate=8000):
    # Convert to mono if necessary
    if nchannels > 1:
        data = audioop.tomono(data, sampwidth, 1, 1)
    # Downsample the audio
    converted, _ = audioop.ratecv(data, sampwidth, nchannels, framerate, outrate, None)
    # Convert PCM frames to mu-law
    mu_law_frames = audioop.lin2ulaw(converted, sampwidth)
    # Base64 encode the mu-law frames
    audio_base64 = base64.b64encode(mu_law_frames).decode('utf-8')
    return audio_base64

def tts_openai_audio(text: str, voice: str = "alloy"):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.audio.speech.create(model="tts-1", voice=voice, input=text, response_format="wav")
    # Assuming response.audio contains the binary audio data:
    audio_data = response.content  # This line needs to be adjusted based on how OpenAI actually returns the audio data
    # Use io.BytesIO as an in-memory file
    with io.BytesIO(audio_data) as audio_file:
        with wave.open(audio_file, 'rb') as wav_file:
            nchannels, sampwidth, framerate, nframes, comptype, compname = wav_file.getparams()
            frames = wav_file.readframes(nframes)
            return downsample_and_encode_audio(frames, sampwidth, nchannels, framerate)

    

if __name__ == "__main__":
    print("Testing tts_openai")
    tts_openai("Today is a wonderful day to build something people love!", gender=1, accent="us")
    os.system(f"start {TTS_MP3_PATH}")
    print("Test complete")