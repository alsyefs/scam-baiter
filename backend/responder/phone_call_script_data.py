import random
# Phone call scripts:
# https://peaksupport.io/resource/blogs/customer-service-scripts-28-examples-and-templates-to-improve-your-customer-service-calls/#:~:text=Here%20are%20some%20examples%20of%20scripts%20you%20could,%5BCustomer%20Name%5D.%20How%20can%20I%20help%20you%20today%3F
# The following is a dictionary of keywords and their corresponding categories.
# https://www.merriam-webster.com/thesaurus
# When a prompt is received, another script will search these PROMPT_KEYWORDS
# find the closest category to the keywords.
def find_keyword_category():
    PROMPT_KEYWORDS = {
    "greetingMe": ["hello", "hi", "hey", "good", "morning", "afternoon", "yo",
                "evening", "night", "what's", "today", "howdy", "greetings",
                "salutations", "welcome", "greeting", "bonjour", "hola",
                "namaste", "hallo", "salam", "shalom", "salute", "regards",
                "respects", "hail", "civilities", "ave", "pleasure", "meet",
                "pleasantries", "wishes", "amenities", "farewell"],

    "askingHowAmI": ["how", "doing", "howdy", "everything", "going", "are",
                    "what's", "up", "good", "well", "fine", "great", "awesome",
                    "g'day"],
    
    "whatAmIDoing": ["what", "doing", "up", "today", "now"],

    "whatIsTheWeather": ["weather", "temperature", "forecast", "rain", "sun", "clouds",
                    "wind", "humidity", "precipitation", "snow", "sleet", "hail",
                    "storm", "thunder", "lightning", "fog", "mist", "smog",
                    "haze", "dew", "frost", "ice", "heat", "cold", "warm", "cool",
                    "hot", "chilly", "breezy", "windy", "gusty", "calm", "still",
                    "mild", "moderate", "fair", "cloudy", "overcast", "clear",
                    "sunny", "bright", "freezing",
                    "frosty", "icy", "snowy", "rainy", "stormy", "thunderous",
                    "foggy", "misty", "smoggy", "hazy", "dewy",
                    "humid", "dry", "wet", "damp", "moist", "muggy", "soggy",
                    "saturated", "soaked", "drenched", "sweaty", "sticky",
                    "clammy", "steamy", "sultry", "sweltering", "scorching",
                    "what", "the", "is", "like", "outside", "outdoors"],

    "offeringHelp": ["problem", "issue", "can't", "troubleshoot", "assist", "help",
                    "fix", "solve", "repair", "resolve", "support", "advise",
                    "guide", "consult", "counsel", "aid", "assistance",
                    "troubleshooting", "fixing", "solving", "repairing",
                    "resolving", "do", "for",  "supporting", "facilitate",
                    "enable", "clarify", "enlighten", "how", "can", "I", "you"],

    "thankingMe": ["thank", "thanks", "kudos", "grateful", "appreciate",
            "appreciation", "kind", "words", "glad", "gratitude", "cheers",
            "bless", "praise", "acknowledge", "recognize", "admire", "respect",
            "thankful", "thankfulness", "gratefulness", "acknowledgement",
            "recognition", "admiration", "thanking"],

    "askingForContactInformation": ["contact", "reach", "out", "get", "in",
                                    "touch", "call", "email", "message", "text",
                                    "chat", "communicate", "talk", "speak",
                                    "connect", "write", "mail", "to", "letter",
                                    "from", "liaise", "network", "interact",
                                    "correspond", "engage"],

    "askingForMyBusinessDetails": ["company", "business", "name", "organization",
                                "corporation", "firm", "enterprise",
                                "institution", "establishment", "agency",
                "authority", "bureau", "department", "division", "section",
                "unit", "branch", "office", "service", "operation", "project",
                "initiative", "program", "scheme", "venture", "undertaking",
                "effort", "movement", "committe", "group",
                "commerce", "trade", "partnership", "deal"],

    "askingIfWorkWithTheAuthority": ["irs", "fbi", "police", "court", "order",
                "official", "department", "federal", "arrest",
                "warrant", "government", "agency",
                "regulator", "supervisor", "enforcer", "administrator",
                "manager"],

    "requestingVerification": ["verify", "confirm", "identification", "case", "ID",
                    "reference", "number", "authenticate", "verification",
                    "security", "code", "validate", "validation", "check",
                    "approval", "confirmation", "certify", "certification",
                    "assure", "assurance", "guarantee", "guaranty", "warrant",
                    "warranty", "attest", "attestation", "endorse", "endorsement",
                    "authorize",
                    "proof", "evidence", "substantiate", "corroborate"],

    "threateningMe": ["legal", "action", "lawsuit", "jail", "fine", "penalty", "urgent",
                "immediate", "required", "serious", "consequence", "consequences",
                "arrest", "warrant", "court", "police", "punishment", "penalize",
                "penalization", "punished", "punish", "punishing", "intimidate",
                "menace", "blackmail", "coerce", "threaten"],

    "resolution": ["resolve", "settle", "clear", "up", "payment", "fee", "fine",
                "transaction", "transfer", "money", "wire", "method",
                "finalize", "complete", "conclude", "finish", "rectify",
                "remedy", "amend"],

    "requestingInformation": ["social", "security", "number", "bank", "account",
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
                        "social", "media", "handle", "xbox", "playstation", "x",
                        "inquire", "query", "question", "ask", "solicit"
                        ],

    "theyAreTechSupport": ["virus", "hacked", "compromised", "security", "breach",
                    "malware", "spyware", "antivirus", "firewall", "phishing",
                    "scam", "fraud", "identity", "theft", "stolen", "hack",
                    "hacker", "hacking", "compromise", "incident", "threat",
                    "cybersecurity", "cyber", "spam", "technical", "IT", "support",
                    "helpdesk", "service", "what", "is", "it", "problem", "issue"],
        
    "requestingPayment": ["gift", "card", "payment", "prepaid", "code", "PIN",
                        "redeem", "balance", "transfer", "transaction", "money",
                        "wire", "fee", "charge", "cost", "expense", "price",
                        "rate", "sum", "amount", "total", "budget", "funds",
                        "resources", "capital", "investment", "savings",
                        "earnings", "income", "revenue", "profit", "gain",
                        "loss", "debt", "credit", "debit", "statement",
                        "financial", "economic", "apple", "google", "amazon",
                        "paypal", "zelle", "venmo", "cashapp", "western",
                        "union", "moneygram", "cryptocurrency", "bitcoin",
                        "ethereum", "litecoin", "dogecoin", "ripple", "stellar",
                        "cardano", "polkadot", "chainlink", "uniswap", "solana",
                        "binance", "coinbase", "kraken", "bitfinex", "gemini",
                        "bitstamp", "huobi", "kucoin", "exchange", "wallet",
                        "digital", "currency", "method", "system", "bank",
                        "account", "finance", "monetary", "pay", "bill", "send",
                        "reimburse", "settle", "compensate", "remunerate",
                        "payoff", "processing",  "banking", "details",
                        "information", "crypto", "blockchain", "service", "card",
                        "fiscal", "accounting", "exploit", "manipulate", "abuse",
                        "use", "misuse"
                        ],

    "emotionalManipulatingMe": ["urgent", "immediate", "fear", "threat", "worry",
                            "anxiety", "concern", "scared", "frightened",
                            "panic", "alarm", "distress", "dread", "terror",
                            "horror", "afraid", "nervous", "anxious", "worried",
                            "concerned", "terrorized", "alarmed", "panicked",
                            "distressed", "dreadful", "terrified", "horrified",
                            "harassed", "intimidated", "happy", "sad", "angry",
                            "mad", "upset", "frustrated", "depressed",
                            "stressed", "enjoy", "joy", "pleasure", "happiness",
                            "sadness", "manipulate", "exploit", "play",
                            "mislead", "deceive"],

    "askingIfIAMAI": ["AI", "artificial", "intelligence", "machine", "learning", "model",
        "chatbot", "bot", "robot", "automated", "system", "program",
        "software", "application", "computer", "algorithm", "code",
        "script", "data", "training", "dataset", "set", "examples",
        "samples", "instances", "records", "observations", "cases",
        "points", "vectors", "patterns", "inputs", "outputs", "targets",
        "labels", "classes", "categories", "groups", "clusters",
        "partitions", "segments", "sections", "divisions", "subsets",
        "subgroups", "subclusters", "subpartitions", "subsegments",
        "subsections", "subcategories", "sub", "human", "real", "person",
        "being", "voice", "generated", "automatic", "answering", "neural",
        "network", "deep", "cognitive"],

    "askingAboutCallLateResponse": ["late", "response", "reply", "answer", "feedback", "back",
                    "delay", "wait", "long", "time", "hours", "minutes",
                    "seconds", "days", "weeks", "months", "years", "ago",
                    "before", "since", "after", "now", "response", "respond",
                    "take", "milliseconds", "overdue", "prolonged", "tardy",
                    "delayed", "behind"],

    "askingAboutMakeAndModelOfMyDevice": ["make", "model", "laptop", "pc", "serial", "number", "brand",
                "name", "manufacturer", "company", "product", "item", "device",
                "type"],

    "askingIfIHaveSlowPC": ["slow", "PC", "laptop", "computer", "device", "system", "machine",
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

    "insultingMe": ["stupid", "dumb", "idiot", "fool", "moron", "imbecile", "ignorant",
            "ignoramus", "dunce", "blockhead", "dullard", "dolt", "simpleton",
            "clod", "clot", "nitwit", "dork", "doofus", "dweeb", "nerd", "geek",
            "twit", "dipstick", "dipshit", "asshole", "dumbass", "fuck"]
    }
    return PROMPT_KEYWORDS

# The following is a dictionary of categories and their corresponding
# responses. Based on the PROMPT_KEYWORDS category, RESPONSE_SENTENCES will
# use a random sentence to respond to the prompt with the mathcing category.
def get_response_sentence(category):
    laptop = random.choice(["PC", "laptop", "computer", "device", "system",
                            "machine"])
    greeting = random.choice(["Hi there!", "Hello there!", "Hey there!",
                              "Hello!", "Hi!", "Hey!", "What's up?",
                              "Good day!", "Hey there! What's up?"])
    howAmIDoingfollow_ups = random.choice([
        " I'm doing well. How are you doing today?",
        " I'm doing good. I would like some help.",
        " I'm doing fine. How are you?"])
    
    iNeedHelp = random.choice(["I need help with my ",
                            "I think am having a problem with my ",
                            "I think am experiencing an issue with my ",
                            "I can't seem to troubleshoot my "])
    
    whatAmIDoing = random.choice(["Nothing much, really. ",
                                "Really, I am not doing much. ",
                                "I am just here, waiting for help. "])

    whatAreYouDoing = random.choice(["What are you doing?", "What are you up to?",
                                    "What are you doing right now?",
                                    "What are you doing today?"])
    
    whatIsTheWeather = random.choice(["I am not sure about the weather. I am indoors. ",
                        "I don't really know. I've been indoors for the whole day. ",
                        "I am not sure. I haven't been outside today. "])
    whatIsTheWeatherFollowUp = random.choice(["Why don't check and tell me?",
                                              "What's the weather like where you are?",
                                              "Can you check and tell me?"])
    
    RESPONSE_SENTENCES = {
    "startCall": [greeting + random.choice([" Is this the technical support?",
                                            " Is this a good time to talk?"])],

    "greetingMe": [greeting + random.choice([" It is a pleasure talking to you.", "."])],

    "askingHowAmI": [greeting + howAmIDoingfollow_ups],

    "whatAmIDoing": [whatAmIDoing + whatAreYouDoing],

    "whatIsTheWeather": [whatIsTheWeather + whatIsTheWeatherFollowUp],

    "offeringHelp": [iNeedHelp + laptop +
                     random.choice([".", ". Can you help me?"])],

    "thankingMe": ["Thank you for your kind words!",
            "Thanks for your help!",
            "Kudos to you!",
            "I am grateful for your assistance!",
            "I appreciate your support!",
            "I am glad for your help!",
            "You're welcome!"],

    "askingForContactInformation": ["Sure, I can " + random.choice(
        ["reach out.", "get in touch."])
        + random.choice([".", " at any time."])],

    "askingForMyBusinessDetails": ["I am not affiliated with any company. I am just a regular person."],
        
    "askingIfWorkWithTheAuthority": ["I don't know why you're mentioning that but ok",
                "I am not affiliated with any government agency. I am just a regular person."],

    "requestingVerification": ["How do I verify that?",
                    "I need to know more about the request.",
                    "Why do I need to confirm that?",
                    "Please, bare with me. I need to know more about the request."],

    "threateningMe": ["Oh my god! what did I do wrong!",
                "Please, don't do anything to me!",
                "Let's calm down and talk about this.",
                "I would like to resolve this issue peacefully."],

    "resolution": ["I need to know more about the request.",
                "Sure, but how do I do that?"],

    "requestingInformation": ["Why do you need that information?", "I need to know more about the request.",
                        "I need to know more about the request."],

    "theyAreTechSupport": ["Is this serious?",
                    "I need to know more about this.",
                    "I don't know what to do.",
                    "Then please help me!"],

    "requestingPayment": ["Before making any payment, please verify the authenticity of the request.",
                "Before this, I need to know more about the request.",
                "Ok... I don't know what to do.",
                "How do I do that?",
                "Before proceeding with any payment, I need to consult with someone I trust.",
                "Can you provide me with more information on why this specific payment method is required?",
                "I'm not comfortable proceeding without further verification. Can we discuss alternative solutions?"],

    "emotionalManipulatingMe": ["I understand this is urgent, but let's ensure we're doing this correctly.",
                            "It's important to remain calm and collected. How can I verify this information?",
                            "I'm feeling quite overwhelmed. Can we step back and explain what's going on again?"],

    "askingIfIAMAI": [random.choice(["Actually, I am not", "I am not ",
                        "Why would think I am ", "I am not"])
        + random.choice(["an AI.", "a bot.", "a chatbot.",
                            "an automated system.", "a machine."])
        + " I am a "
        + random.choice(["human.", "person.", "real person.", "real human.",
                            "real human being."])],

    "askingAboutCallLateResponse": ["I " + random.choice(["think", "believe", "suspect", "assume", "notice"])
                    + " that there's "
                    + random.choice(["a delay", "a problem", "a glitch", "an issue", "a hiccup"])
                    + " in our call, " + "I'm not sure what's " + random.choice(["the problem.", "going on.", "the issue."])],

    "askingAboutMakeAndModelOfMyDevice": ["well, it's a laptop but I'm not sure... I think it's Lenovo or Asus "
                + laptop
                + " or something else but I'm not really sure. Why does that matter?",
                "Let me check that for you... wait, how do I check that?",
                "Why do you need to know that? I'm not sure how to get the details of my " 
                + laptop + ".",
                "Wait, how can I know that?",
                "Did you just ask me to check the make and model of my "
                + laptop + "." + "?"],

    "askingIfIHaveSlowPC": [
        random.choice(["I think I have a slow ",
                    "I think I have some weird problems with my ",
                    "I can't seem to troubleshoot my "])
        + laptop + ". "
        + random.choice(["It is slow.", "It is sluggish.", "It is unresponsive.",
                        "It is freezing.", "It has been acting up."])
        + " Can you help me?"],

    "insultingMe": ["I'm sorry, I don't understand why you're saying that.",
            "I'm not sure why you're saying that.",
            "I'm not sure what you're trying to say."],
    # Default response when no category was found for the response:
    "default": ["I am sorry but I couldn't get that. Will you please repeat it back?",
                "Apologies, but I couldn't understand that. Can you repeat it back?",
                "I'm sorry, what?",
                "Would you mind repeating that? I didn't quite catch that.",
                "I'm having trouble understanding you. Can you repeat that?",
                "What was the last thing you said? Can you repeat it?",
                "Apologies, but I didn't understand that. Can you repeat it?",
                "I'm sorry, I didn't catch that. Can you repeat it?",
                "What was that? Can you repeat it?"]
    }
    return RESPONSE_SENTENCES