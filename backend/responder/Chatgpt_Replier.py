import os
import openai
import tiktoken
import json
import re
from globals import(
  OPENAI_API_KEY,
  GPT_CHAT_1_INSTRUCTIONS, GPT_CHAT_2_INSTRUCTIONS,
  GPT_CHAT_3_INSTRUCTIONS, GPT_CHAT_4_INSTRUCTIONS,
  GPT_CHAT_5_INSTRUCTIONS, GPT_CHAT_6_INSTRUCTIONS,
  GPT_CHAT_TTS_INSTRUCTIONS
)
from .chatgpt import generate_text
from .chatgpt_async import generate_text_async
from logs import LogManager
log = LogManager.get_logger()

openai.api_key = OPENAI_API_KEY


def extract_content(text, tag):
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start_index = text.find(start_tag) + len(start_tag)
    end_index = text.find(end_tag)
    if start_index > -1 and end_index > -1:
        return text[start_index:end_index].strip()
    else:
        return ""
    
def attempt_to_get_reply_and_summary(prompt, gpt_model="gpt-4", instructions="", max_attempts=3):
    gpt_model = "gpt-4"
    instructions = instructions
    prompt = prompt
    attempt = 0
    try:
      while attempt < max_attempts:
          messages = [{"role": "system", "content": instructions}, {"role": "user", "content": prompt}]
          log.info(f"Attempt ({attempt+1} / {max_attempts}) to generate a response with the required tags")
          res = generate_text(gpt_model, messages, 0.7, 1.0)
          generated_response = extract_content(res, "Reply")
          new_summary_context = extract_content(res, "Summary")
          if generated_response and new_summary_context:
              return generated_response, new_summary_context
          if not generated_response:
              log.error(f"Failed to generate a response with the required tags. No <Reply> tag found.")
          if not new_summary_context:
              log.error(f"Failed to generate a response with the required tags. No <Summary> tag found.")
          attempt += 1
    except Exception as e:
        log.error(f"Error in attempt_to_get_reply_and_summary. Failed to generate a response with the required tags ({max_attempts}) attempts: {e}")
    return "Apologies, but I did not understand what you meant.", ""
   

def gen_text_1(prompt, old_summary_context: str = ""):
  gpt_model = "gpt-4"
  instructions = GPT_CHAT_1_INSTRUCTIONS
  prompt = "Reply without any signature: " + prompt
  messages=[{"role": "system", "content": instructions}, {"role": "user", "content": prompt}]
  generated_response = generate_text(gpt_model, messages, 0.7, 1.0)
  new_summary_context = ""
  return generated_response, new_summary_context

def gen_text_2(prompt, old_summary_context: str = ""):
  gpt_model = "gpt-4"
  instructions = GPT_CHAT_2_INSTRUCTIONS
  prompt = f"This is the context so far: {old_summary_context} Use <Reply> </Reply> tags to reply to the following email and use <Summary> </Summary> tags to create an updated summary of the whole interaction and reply without any signature: {prompt}"
  generated_response, new_summary_context = attempt_to_get_reply_and_summary(prompt, gpt_model, instructions, max_attempts=3)
  return generated_response, new_summary_context

def gen_text_3(prompt, old_summary_context: str = ""):
  gpt_model = "gpt-4"
  instructions = GPT_CHAT_3_INSTRUCTIONS
  prompt = "This is the context so far: " + old_summary_context + " Use <Reply> </Reply> tags to reply to the following email and use <Summary> </Summary> tags to create an updated summary of the whole interaction and reply without any signature: " + prompt
  generated_response, new_summary_context = attempt_to_get_reply_and_summary(prompt, gpt_model, instructions, max_attempts=3)
  return generated_response, new_summary_context

def gen_text_4(prompt, old_summary_context: str = ""):
  gpt_model = "gpt-4"
  instructions = GPT_CHAT_4_INSTRUCTIONS
  prompt = "This is the context so far: " + old_summary_context + " Use <Reply> </Reply> tags to reply to the following email and use <Summary> </Summary> tags to create an updated summary of the whole interaction and reply without any signature: " + prompt
  generated_response, new_summary_context = attempt_to_get_reply_and_summary(prompt, gpt_model, instructions, max_attempts=3)
  return generated_response, new_summary_context

def gen_text_5(prompt, old_summary_context: str = ""):
  gpt_model = "gpt-4"
  instructions = GPT_CHAT_5_INSTRUCTIONS
  prompt = "This is the context so far: " + old_summary_context + " Use <Reply> </Reply> tags to reply to the following email and use <Summary> </Summary> tags to create an updated summary of the whole interaction and reply without any signature: " + prompt
  generated_response, new_summary_context = attempt_to_get_reply_and_summary(prompt, gpt_model, instructions, max_attempts=3)
  return generated_response, new_summary_context

def gen_text_6(prompt, old_summary_context: str = ""):
  gpt_model = "gpt-4"
  instructions = GPT_CHAT_6_INSTRUCTIONS
  prompt = "This is the context so far: " + old_summary_context + " Use <Reply> </Reply> tags to reply to the following email and use <Summary> </Summary> tags to create an updated summary of the whole interaction and reply without any signature: " + prompt
  generated_response, new_summary_context = attempt_to_get_reply_and_summary(prompt, gpt_model, instructions, max_attempts=3)
  return generated_response, new_summary_context



############################################################################################################
def gen_text_tts(prompt):
  gpt_model = "gpt-3.5-turbo"
  messages=[{"role": "system", "content": GPT_CHAT_TTS_INSTRUCTIONS}, {"role": "user", "content": prompt}]
  res = generate_text(gpt_model, messages, 0.2, 0.2)
  return res

async def gen_text_tts_async(prompt):
  gpt_model = "gpt-3.5-turbo"
  messages=[{"role": "system", "content": GPT_CHAT_TTS_INSTRUCTIONS}, {"role": "user", "content": prompt}]
  res = await generate_text_async(gpt_model, messages, 0.2, 0.2)
  return res