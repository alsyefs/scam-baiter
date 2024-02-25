import random
import re
import traceback
from globals import (PROMPT_KEYWORDS, RESPONSE_SENTENCES)
from logs import LogManager
log = LogManager.get_logger()

def generate_call_response(prompt):
    positive_keywords = []
    negative_keywords = []
    try:
        prompt_words = prompt.split()
        prompt_words = [re.sub(r'\W+', '', word.lower()) for word in prompt_words]
        for prompt_category in PROMPT_KEYWORDS:
            for word in prompt_words:
                if word in prompt_words:
                    if word in PROMPT_KEYWORDS[prompt_category]:
                        positive_keywords.append(prompt_category) # Search for matching keywords.
                    else:
                        negative_keywords.append(prompt_category)
        response = "I am sorry but I couldn't get that. Will you please repeat it back?" # This will not be used as the final response.
        positive_response_category = "" # Initialize the positive response category.
        votes_per_category = {category: positive_keywords.count(category) for category in positive_keywords}
        print(f"prompt: ({prompt}).")
        if len(positive_keywords) > 0:
            positive_response_category = max(positive_keywords, key=positive_keywords.count) # Get the most frequent positive response category.
            response = RESPONSE_SENTENCES[positive_response_category][random.randint(0, len(RESPONSE_SENTENCES[positive_response_category])-1)]
        else:
            positive_response_category = "default"
            response = RESPONSE_SENTENCES["default"][random.randint(0, len(RESPONSE_SENTENCES["default"])-1)]
        print(f"Call prompt: ({prompt}).\nPrompt category: ({positive_response_category})\nvotes: ({votes_per_category}). \nGenerated response: ({response}).")
        log.info(f"Call prompt: ({prompt}).\nPrompt category: ({positive_response_category})\nvotes: ({votes_per_category}). \nGenerated response: ({response}).")
        return response
    except Exception as e:
        response = "I am sorry but I couldn't get that. Will you please repeat it back?"
        log.error(f"An error occurred: {str(e)}. Traceback: {traceback.format_exc()}")
        return response

if __name__ == "__main__":
    while True:
        prompt = input("Enter a prompt: ")
        print(generate_call_response(prompt))