import openai
import sys
import os
import re
from globals import OPENAI_API_KEY, GPT_MODEL
from logs import LogManager
log = LogManager.get_logger()

openai.api_key = OPENAI_API_KEY
responder_path = os.path.join(os.path.dirname(__file__), 'responder')
sys.path.insert(0, responder_path)

def test_generate_text(gpt_instructions, gpt_prompt):
    messages = [{"role": "system", "content": gpt_instructions}, {"role": "user","content": prompt_message}]
    response = generate_text(GPT_MODEL, messages, temperature=0.2, top_p=0.2, presence_penalty=0.5, frequency_penalty=0.5)
    print("\n"+"-" * 15 +"Using (" + GPT_MODEL + ") model: " + "-" * 15 + "\n" + "-" * 50 + "\nPrompt message:\n" + prompt_message + "\n" + "-" * 50)
    print("-" * 50 + "\nGenerated Text:\n" + response + "\n" + "-" * 50 + "\n")

def generate_text(GPT_MODEL=GPT_MODEL, messages, temperature=0.2, top_p=0.2, presence_penalty=0.5, frequency_penalty=0.5):
    completion = None
    general_message = "Apologies, but I do not know why do you need to know that."
    try:
        completion = openai.ChatCompletion.create(model=GPT_MODEL, messages=messages, temperature=temperature, top_p=top_p, presence_penalty=0.5, frequency_penalty=0.5)
    except Exception as e:
        log.error(f"Error: {e}")
    except:
        log.error("Unknown GPT error when generating text")
    if completion is not None:
        res = completion.choices[0].message.content
        if res == "":
            return general_message
        res = re.sub("\[.*?\]", "", res)
        return res
    else:
        return general_message

if __name__ == "__main__":
    gpt_instructions = """You are good at pattern following. You are a person and not a language model. Do not call them a scam."""
    gpt_prompt = "Are you from UK ?"
    test_generate_text(gpt_instructions, gpt_prompt)