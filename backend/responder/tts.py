from gtts import gTTS
import pygame
import io
import os
from globals import TTS_MP3_PATH

if not os.path.exists(os.path.dirname(TTS_MP3_PATH)):
    os.makedirs(os.path.dirname(TTS_MP3_PATH))

def play_text(text):
    pygame.mixer.init()
    tts_io = io.BytesIO() 
    # tts = gTTS(text, lang='en', tld='co.uk', slow=False)  # English UK
    tts = gTTS(text, lang='en', tld='us')  # English USA
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    pygame.mixer.music.load(tts_io)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

def get_audio(text):
    pygame.mixer.init()
    tts_io = io.BytesIO()
    # tts = gTTS(text, lang='en', tld='co.uk', slow=False)  # English UK
    tts = gTTS(text, lang='en', tld='us') # English USA
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    pygame.mixer.music.load(tts_io)
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    return tts_io

def set_mp3_from_text(text):
    # tts = gTTS(text, lang='en', tld='co.uk', slow=False)  # English UK
    tts = gTTS(text, lang='en', tld='us')  # English USA
    tts.save(TTS_MP3_PATH)

if __name__ == '__main__':
    set_mp3_from_text('Hello, how are you?')
    # play_text('Hello, how are you?')
