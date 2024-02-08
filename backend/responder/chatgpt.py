from flask import session
from openai import OpenAI
import re
from database.models import db_models
from database.gpt_table import GPTDatabaseManager
from globals import (
  OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS, GPT_STOP_SEQUENCES,
  GPT_PRESENCE_PENALTY, GPT_FREQUENCY_PENALTY
)
from logs import LogManager
log = LogManager.get_logger()
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_text(gpt_model, messages, temperature=0.2, top_p=0.2):
    # log.info(f"Generating from messages: {messages}")
    general_message = "Apologies, but I do not know what do you mean by that."
    prompt = None
    completion = None
    gpt_instructions = None
    stop_sequences_str = ';'.join(GPT_STOP_SEQUENCES)
    username = None
    try:
        username = session.get('username', 'system')
    except Exception:
        print("Error getting username from session")
        pass
    try:
        gpt_instructions = None
        prompt = None
        for message in messages:
            if message['role'] == 'system':
                gpt_instructions = message['content']
            elif message['role'] == 'user':
                prompt = message['content']
        if gpt_instructions is None:
            gpt_instructions = ""
        if prompt is None:
            prompt = ""
        completion = client.chat.completions.create(model=gpt_model, messages=messages, temperature=temperature, top_p=top_p, stop=GPT_STOP_SEQUENCES, presence_penalty=GPT_PRESENCE_PENALTY, frequency_penalty=GPT_FREQUENCY_PENALTY)
        GPTDatabaseManager.insert_gpt(prompt, completion.choices[0].message.content, gpt_instructions, gpt_model, temperature, MAX_TOKENS, stop_sequences_str, top_p, GPT_PRESENCE_PENALTY, GPT_FREQUENCY_PENALTY, username)
    except Exception as e:
        log.error(f"GPT error when generating text: {e}")
    if completion is not None:
        res = completion.choices[0].message.content
        if res == "":
            return general_message
        res = re.sub("AI", "", res)
        res = re.sub("\[.*?\]", "", res)
        return res
    else:
        return general_message
    
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a human."},
        {"role": "user", "content": "I am a human."}
    ]
    print(generate_text(gpt_model = "gpt-3.5-turbo", messages=messages))