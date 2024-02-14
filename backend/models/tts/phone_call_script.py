import random
# Phone call scripts:
# https://peaksupport.io/resource/blogs/customer-service-scripts-28-examples-and-templates-to-improve-your-customer-service-calls/#:~:text=Here%20are%20some%20examples%20of%20scripts%20you%20could,%5BCustomer%20Name%5D.%20How%20can%20I%20help%20you%20today%3F
PROMPT_KEYWORDS = {
    "greeting": ["hello", "hi", "hey", "good", "morning", "afternoon", "evening", "night"],
    "help": ["problem", "issue", "can't", "troubleshoot", "assist", "help"],
    "thanks": ["thank you", "thanks", "kudos"],
    "contact": ["contact", "reach out", "get in touch"],
    "business": ["company", "business", "name"],
    "AI": ["AI", "artificial", "intelligence", "machine", "learning", "model", "chatbot", "bot"]
}
RESPONSE_KEYWORDS = {
    "greeting": ["Hello there! How are you doing today?",
                 "Good day! How are you doing today?",
                 "Hi there! How are you doing today?",
                 "Hey there! What's up?",
                 "Hello!",
                 "Good day! I would like some help.",
                 "Hi! I would like some help."],
    "help": ["I am having a problem with my "+ random.choice(["PC.", "laptop.", "computer."]),
             "I am experiencing an issue with my "+ random.choice(["PC.", "laptop.", "computer."]),
             "I can't seem to troubleshoot my "+ random.choice(["PC.", "laptop.", "computer."])],
    "thanks": ["Thank you for your kind words!",
               "Thanks for your help!",
               "Kudos to you!"],
    "contact": ["Sure, I can reach out.",
                "Sure, I can reach out at any time.",
                "Sure, I can get in touch.",
                "Sure, I can get in touch at any time."],
    "business": ["I am not affiliated with any company. I am just a regular person."],
    "AI": ["Actually, I am not an AI. I am a human.",
           "I am not an AI. I am a human",
           "I am not an AI. I am a person.",
           "Why would think I am an AI? I am a human.",
           "I am not a bot. I am a person."]
}