# Phone call scripts:
# https://peaksupport.io/resource/blogs/customer-service-scripts-28-examples-and-templates-to-improve-your-customer-service-calls/#:~:text=Here%20are%20some%20examples%20of%20scripts%20you%20could,%5BCustomer%20Name%5D.%20How%20can%20I%20help%20you%20today%3F
import random
# The following is a dictionary of keywords and their corresponding categories.
# When a prompt is received, another script will search these PROMPT_KEYWORDS
# find the closest category to the keywords.
PROMPT_KEYWORDS = {
"greeting": ["hello", "hi", "hey", "good", "morning", "afternoon", "yo",
             "evening", "night", "what's", "up", "good", "how",
             "doing", "today", "today", "howdy", "greetings",
             "salutations", "welcome", "greeting", "everything", "going",
             "are"],

"help": ["problem", "issue", "can't", "troubleshoot", "assist", "help", "fix",
         "solve", "repair", "resolve", "support", "advise", "guide", "consult",
         "counsel", "aid", "assistance", "troubleshooting", "fixing",
         "solving", "repairing", "resolving", "do", "for"],

"thanks": ["thank", "thanks", "kudos", "grateful", "appreciate",
           "appreciation", "kind", "words", "glad", "gratitude", "cheers",
           "bless", "praise", "acknowledge", "recognize", "admire",
           "respect", "thankful", "thankfulness", "gratitude",
           "gratefulness", "acknowledgement", "recognition", "admiration"],

"contact": ["contact", "reach", "out", "get", "in", "touch", "call", "email",
            "message", "text", "chat", "communicate", "talk", "speak",
            "connect", "write", "mail", "to", "letter", "from"],

"business": ["company", "business", "name", "organization", "corporation",
             "firm", "enterprise", "institution", "establishment", "agency",
             "authority", "bureau", "department", "division", "section",
             "unit", "branch", "office", "service", "operation", "project",
             "initiative", "program", "scheme", "venture", "undertaking",
             "effort", "movement", "committe", "group"],

"authority": ["irs", "fbi", "police", "court", "order", "arrest warrant",
              "official", "department", "federal", "arrest",
              "warrant", "government", "agency"],

"verification": ["verify", "confirm", "identification", "case", "ID",
                 "reference", "number", "authenticate", "verification",
                 "security", "code", "validate", "validation", "check",
                 "approval", "confirmation", "certify", "certification",
                 "assure", "assurance", "guarantee", "guaranty", "warrant",
                 "warranty", "attest", "attestation", "endorse", "endorsement",
                 "authorize"],

"threats": ["legal", "action", "lawsuit", "jail", "fine", "penalty", "urgent",
            "immediate", "required", "serious", "consequence", "consequences",
            "arrest", "warrant", "court", "police", "punishment", "penalize",
            "penalization", "punished", "punish", "punishing"],

"resolution": ["resolve", "settle", "clear", "up", "payment", "fee", "fine",
               "transaction", "transfer", "money", "wire", "method",
               "finalize", "complete"],

"requestInformation": ["social", "security", "number", "bank", "account",
                       "credit", "card", "personal", "information", "address",
                       "date", "of", "birth", "phone", "email", "location",
                       "password", "username", "telephone", "cellphone",
                       "mobile", "whatsapp", "telegram", "signal", "viber",
                       "name", "full", "first", "last", "middle", "maiden",
                       "mother", "father", "parent", "guardian", "relative",
                       "friend", "family", "member", "spouse", "partner",
                       "child", "children", "son", "daughter", "brother",
                       "sister", "cousin", "aunt", "uncle", "niece", "nephew",
                       "grandparent", "grandchild", "in-law", "given",
                       "twitter", "facebook", "instagram", "linkedin",
                       "social", "media", "handle", "xbox", "playstation", "x"
                       ],

"techSupport": ["virus", "hacked", "compromised", "security", "breach",
                "malware", "spyware", "antivirus", "firewall", "phishing",
                "scam", "fraud", "identity", "theft", "stolen", "hack",
                "hacker", "hacking", "compromise", "incident", "threat",
                "cybersecurity", "cyber", "spam"],
    
"payment": ["gift", "card", "payment", "prepaid", "code", "PIN",
              "redeem", "balance", "transfer", "transaction", "money",
              "wire", "fee", "charge", "cost", "expense", "price", "rate",
              "sum", "amount", "total", "budget", "funds", "resources",
              "capital", "investment", "savings", "earnings", "income",
              "revenue", "profit", "gain", "loss", "debt", "credit",
              "debit", "statement", "financial", "economic", "apple",
              "google", "amazon", "paypal", "zelle", "venmo", "cashapp",
              "western", "union", "moneygram", "cryptocurrency", "bitcoin",
              "ethereum", "litecoin", "dogecoin", "ripple", "stellar",
              "cardano", "polkadot", "chainlink", "uniswap", "solana",
              "binance", "coinbase", "kraken", "bitfinex", "gemini",
              "bitstamp", "huobi", "kucoin", "exchange", "wallet", "digital",
              "currency", "method", "system", "bank", "account", "finance",
              "monetary", "pay", "bill", "send"],

"emotionalManipulation": ["urgent", "immediate", "fear", "threat", "worry",
                          "anxiety", "concern", "scared", "frightened",
                          "panic", "alarm", "distress", "dread", "terror",
                          "horror", "afraid", "nervous", "anxious", "worried",
                          "concerned", "terrorized", "alarmed", "panicked",
                          "distressed", "dreadful", "terrified", "horrified",
                          "harassed", "intimidated", "happy", "sad", "angry",
                          "mad", "upset", "frustrated", "depressed",
                          "stressed", "enjoy", "joy", "pleasure", "happiness",
                          "sadness"],

"financialExploitation": ["money", "transfer", "wire", "Western", "Union",
                          "PayPal", "Zelle", "cryptocurrency", "Bitcoin",
                          "Ethereum", "processing", "transaction", "banking",
                          "details", "financial", "information", "payment",
                          "crypto", "blockchain", "wallet", "digital",
                          "currency", "method", "system", "service", "bank",
                          "debit", "credit", "card", "account", "finance",
                          "economic", "monetary", "fiscal", "pay", "bill",
                          "fee", "charge", "cost", "expense", "price", "rate",
                          "sum", "amount", "total", "budget", "funds",
                          "resources", "capital", "investment", "savings",
                          "earnings", "income", "revenue", "profit", "gain",
                          "loss", "debt", "balance", "statement", "accounting"
                          ],

"AI": ["AI", "artificial", "intelligence", "machine", "learning", "model",
       "chatbot", "bot", "robot", "automated", "system", "program",
       "software", "application", "computer", "algorithm", "code",
       "script", "data", "training", "dataset", "set", "examples",
       "samples", "instances", "records", "observations", "cases",
       "points", "vectors", "patterns", "inputs", "outputs", "targets",
       "labels", "classes", "categories", "groups", "clusters",
       "partitions", "segments", "sections", "divisions", "subsets",
       "subgroups", "subclusters", "subpartitions", "subsegments",
       "subsections", "subcategories", "sub", "human", "real", "person",
       "being", "voice", "generated", "automatic", "answering"],

"lateResponse": ["late", "response", "reply", "answer", "feedback", "back",
                 "delay", "wait", "long", "time", "hours", "minutes",
                 "seconds", "days", "weeks", "months", "years", "ago",
                 "before", "since", "after", "now", "response", "respond",
                 "take", "milliseconds"],

"makeModel": ["make", "model", "laptop", "pc", "serial", "number", "brand",
              "name", "manufacturer", "company", "product", "item", "device",
              "type"],

"slowPC": ["slow", "PC", "laptop", "computer", "device", "system", "machine",
           "freeze", "software", "application", "program", "process", "keeps",
           "crashing", "crash", "crashes", "hang", "hangs", "freezing",
           "frozen", "unresponsive", "unresponsive", "unstable", "task", "job",
           "work", "operation", "function", "feature", "capability",
           "performance", "speed", "quick", "fast", "rapid", "swift",
           "sluggish", "firewall", "antivirus", "malware", "spyware", "virus",
           "trojan", "worm", "ransomware", "phishing", "no", "response",
           "infected", "space", "memory", "storage", "disk", "drive", "hard",
           "SSD", "HDD", "RAM", "CPU", "processor", "GPU", "graphics",
           "inactive", "dull", "lazy", "idle", "lagging", "lag", "delay",
           "lags", "delays", "wait", "late", "behind", "after", "last", "end",
           "finish", "complete", "done", "over", "through", "conclude",
           "accomplish", "achieve", "attain", "reach", "gain", "obtain",
           "acquire", "procure", "secure", "get", "fetch", "bring", "carry",
           "deliver", "hand", "pass", "transfer", "transmit", "send", 
           "dispatch", "old", "outdated", "obsolete", "upgrade", "update",
           "seems", "to", "be", "problem", "issue", "trouble",
           "specific", "exactly"],

"insult": ["stupid", "dumb", "idiot", "fool", "moron", "imbecile", "ignorant",
           "ignoramus", "dunce", "blockhead", "dullard", "dolt", "simpleton",
           "clod", "clot", "nitwit", "dork", "doofus", "dweeb", "nerd", "geek",
           "twit", "dipstick", "dipshit", "asshole", "dumbass", "fuck"]
}

laptop = random.choice(["PC", "laptop", "computer", "device", "system",
                        "machine"])
greeting = random.choice(["Hi there!", "Hello there!", "Hey there!", "Hello!",
                          "Hi!", "Hey!", "What's up?", "Good day!",
                          "Hey there! What's up?"])

# The following is a dictionary of categories and their corresponding
# responses. Based on the PROMPT_KEYWORDS category, RESPONSE_SENTENCES will
# use a random sentence to respond to the prompt with the mathcing category.
RESPONSE_SENTENCES = {
"startCall": [greeting + random.choice([" Is this the technical support?",
                                        " Is this a good time to talk?"])],

"greeting": [greeting + random.choice([" How are you doing today?",
                                       " I would like some help.",
                                       " How are you?"])],

"help": [random.choice(["I need help with my ",
                        "I think am having a problem with my ",
                        "I think am experiencing an issue with my ",
                        "I can't seem to troubleshoot my "])
         + laptop + random.choice([".", ". Can you help me?"])],

"thanks": ["Thank you for your kind words!",
           "Thanks for your help!",
           "Kudos to you!",
           "I am grateful for your assistance!",
           "I appreciate your support!",
           "I am glad for your help!",
           "You're welcome!"],

"contact": ["Sure, I can " + random.choice(["reach out.", "get in touch."])
            + random.choice([".", " at any time."])],

"business": ["I am not affiliated with any company. I am just a regular person."],
    
"authority": ["I don't know why you're mentioning that but ok",
              "I am not affiliated with any government agency. I am just a regular person."],

"verification": ["How do I verify that?",
                 "I need to know more about the request.",
                 "Why do I need to confirm that?",
                 "Please, bare with me. I need to know more about the request."],

"threats": ["Oh my god! what did I do wrong!",
              "Please, don't do anything to me!",
              "Let's calm down and talk about this.",
              "I would like to resolve this issue peacefully."],

"resolution": ["I need to know more about the request.",
               "Sure, but how do I do that?"],

"requestInformation": ["Why do you need that information?", "I need to know more about the request.",
                       "I need to know more about the request."],

"techSupport": ["Is this serious?",
                "I need to know more about this.",
                "I don't know what to do.",
                "Then please help me!"],

"payment": ["Before making any payment, please verify the authenticity of the request.",
            "Before this, I need to know more about the request.",
            "Ok... I don't know what to do.",
            "How do I do that?"],

"emotionalManipulation": ["I understand this is urgent, but let's ensure we're doing this correctly.",
                          "It's important to remain calm and collected. How can I verify this information?",
                          "I'm feeling quite overwhelmed. Can we step back and explain what's going on again?"],

"financialExploitation":["Before proceeding with any payment, I need to consult with someone I trust.",
                            "Can you provide me with more information on why this specific payment method is required?",
                            "I'm not comfortable proceeding without further verification. Can we discuss alternative solutions?"],

"AI": [random.choice(["Actually, I am not", "I am not ",
                      "Why would think I am ", "I am not"])
       + random.choice(["an AI.", "a bot.", "a chatbot.",
                        "an automated system.", "a machine."])
       + " I am a "
       + random.choice(["human.", "person.", "real person.", "real human.",
                        "real human being."])],

"lateResponse": ["I " + random.choice(["think", "believe", "suspect", "assume", "notice"])
                 + " that there's "
                 + random.choice(["a delay", "a problem", "a glitch", "an issue", "a hiccup"])
                 + " in our call, " + "I'm not sure what's " + random.choice(["the problem.", "going on.", "the issue."])],

"makeModel": ["well, it's a laptop but I'm not sure... I think it's Lenovo or Asus "
              + laptop
              + " or something else but I'm not really sure. Why does that matter?",
              "Let me check that for you... wait, how do I check that?",
              "Why do you need to know that? I'm not sure how to get the details of my " 
              + laptop + ".",
              "Wait, how can I know that?",
              "Did you just ask me to check the make and model of my "
              + laptop + "." + "?"],

"slowPC": [
    random.choice(["I think I have a slow ",
                   "I think I have some weird problems with my ",
                   "I can't seem to troubleshoot my "])
    + laptop + ". "
    + random.choice(["It is slow.", "It is sluggish.", "It is unresponsive.",
                     "It is freezing.", "It has been acting up."])
    + " Can you help me?"],

"insult": ["I'm sorry, I don't understand why you're saying that.",
           "I'm not sure why you're saying that.",
           "I'm not sure what you're trying to say."],

"default": ["I am sorry but I couldn't get that. Will you please repeat it back?",
              "Apologies, but I couldn't understand that. Can you repeat it back?",
              "I'm sorry, what?",
              "Would you mind repeating that? I didn't quite catch that.",
              "I'm having trouble understanding you. Can you repeat that?",
              "What was the last thing you said? Can you repeat it?"]
}