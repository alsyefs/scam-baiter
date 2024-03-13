import asyncio
import websockets
import json
from backend.models.tts.tts_openai_async_model import tts_openai_async


async def stream_audio(text, websocket, path):
    if not text:
        text = "Hello there! Is this a good time to talk?"
    async for message in websocket:
        data = json.loads(message)
        if data.get('event') == 'connected':
            print("Twilio connected")
            # Here, fetch or generate your audio data
            audio_data = await tts_openai_async(text)
            # Stream audio data back to Twilio
            await websocket.send(audio_data)
        elif data.get('event') == 'start':
            print("Stream started")
        elif data.get('event') == 'media':
            # Handle incoming media, if necessary
            pass
        elif data.get('event') == 'stop':
            print("Stream stopped")
            break

start_server = websockets.serve(stream_audio, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
