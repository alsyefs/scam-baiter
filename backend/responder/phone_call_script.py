import random
import re
from globals import (PROMPT_KEYWORDS, RESPONSE_KEYWORDS)

def generate_call_response(prompt):
    positive_keywords = []
    negative_keywords = []
    prompt_words = prompt.split()
    prompt_words = [re.sub(r'\W+', '', word.lower()) for word in prompt_words]
    for prompt_category in PROMPT_KEYWORDS:
        for word in prompt_words:
            if word in prompt_words:
                if word in PROMPT_KEYWORDS[prompt_category]:
                    positive_keywords.append(prompt_category)
                else:
                    negative_keywords.append(prompt_category)
    response = "I am sorry but I couldn't get that. Will you please repeat it back?"
    positive_response_category = ""
    if len(positive_keywords) > 0:
        positive_response_category = max(positive_keywords, key=positive_keywords.count)
        response = RESPONSE_KEYWORDS[positive_response_category][random.randint(0, len(RESPONSE_KEYWORDS[positive_response_category])-1)]
    return response

if __name__ == "__main__":
    while True:
        prompt = input("Enter a prompt: ")
        print(generate_call_response(prompt))
