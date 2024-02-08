from secret import ( 
    OPENAI_API_KEY, MAILGUN_API_KEY, MAILGUN_DOMAIN_NAME,
    FLASK_SECRET_KEY, DEFAULT_SUPER_ADMIN_USERNAME, 
    DEFAULT_SUPER_ADMIN_PASSWORD, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_CALL_URL, TWILIO_PHONE_NUMBERS, DEFAULT_USER_USERNAME,
    DEFAULT_USER_PASSWORD, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
    MAILGUN_TARGET_EMAIL_TEST, ELEVENLABS_API_KEY
)
import logging
import os
# System variables:
FLASK_SECRET_KEY = FLASK_SECRET_KEY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRON_JOB_PATH = os.path.join(BASE_DIR, "cron.py")

LOGGING_LEVEL = logging.DEBUG
logging.DEBUG
DEBUGGING_LOGS_TABLE_NAME = "logs_debugging"
INFO_LOGS_TABLE_NAME = "logs_info"
WARNING_LOGS_TABLE_NAME = "logs_warning"
ERROR_LOGS_TABLE_NAME = "logs_error"
CRITICAL_LOGS_TABLE_NAME = "logs_critical"
NOTSET_LOGS_TABLE_NAME = "logs_notset"
DB_PATH = os.path.join(BASE_DIR, "database", "system.db")
DEBUGGING_LOGS_TEXT_FILE_PATH = os.path.join(BASE_DIR, "logs", "logs_debugging.txt")
INFO_LOGS_TEXT_FILE_PATH = os.path.join(BASE_DIR, "logs", "logs_info.txt")
WARNING_LOGS_TEXT_FILE_PATH = os.path.join(BASE_DIR, "logs", "logs_warning.txt")
ERROR_LOGS_TEXT_FILE_PATH = os.path.join(BASE_DIR, "logs", "logs_error.txt")
CRITICAL_LOGS_TEXT_FILE_PATH = os.path.join(BASE_DIR, "logs", "logs_critical.txt")
NOTSET_LOGS_TEXT_FILE_PATH = os.path.join(BASE_DIR, "logs", "logs_notset.txt")

# Web application variables:
DEFAULT_SUPER_ADMIN_USERNAME = DEFAULT_SUPER_ADMIN_USERNAME 
DEFAULT_SUPER_ADMIN_PASSWORD = DEFAULT_SUPER_ADMIN_PASSWORD
DEFAULT_ADMIN_USERNAME = DEFAULT_ADMIN_USERNAME
DEFAULT_ADMIN_PASSWORD = DEFAULT_ADMIN_PASSWORD
DEFAULT_USER_USERNAME = DEFAULT_USER_USERNAME
DEFAULT_USER_PASSWORD = DEFAULT_USER_PASSWORD

# MAIL handling
MAX_EMAILS_TO_HANDLE = 5  # number of replies per cron run
EMAILS_DIRECTORY = os.path.join(BASE_DIR, "emails")  # root directory for all emails
MAIL_SAVE_DIR = os.path.join(BASE_DIR, "emails", "queued")  # crawled and received emails
MAIL_ARCHIVE_DIR = os.path.join(BASE_DIR, "emails", "archive")  # archive
MAIL_HANDLED_DIR = os.path.join(BASE_DIR, "emails", "handled")  # emails replied to
ADDR_SOL_PATH = os.path.join(BASE_DIR, "emails", "record.json")  # stores email addresses and names and strategies used
INBOX_MAIL = os.path.join(BASE_DIR, "emails", "inbox")  # emails received
SENT_MAIL = os.path.join(BASE_DIR, "emails", "sent")  # emails sent
READ_INBOX = os.path.join(BASE_DIR, "emails", "read")  # emails read
UNREAD_INBOX = os.path.join(BASE_DIR, "emails", "unread")  # new emails
EMAIL_TEMPLATE = os.path.join(BASE_DIR, "emailing_service", "template.html")  # email template
MAILGUN_TARGET_EMAIL_TEST = MAILGUN_TARGET_EMAIL_TEST # Email for testing to be removed in production.
UNIQUE_EMAIL_QUEUED = os.path.join(BASE_DIR, "emails", "emails_queued.txt")
UNIQUE_EMAIL_QUEUED_DUPLICATE = os.path.join(BASE_DIR, "emails", "emails_queued_duplicate.txt")
EMAIL_ARCHIVED_CLEANED_DIR = os.path.join(BASE_DIR, "emails", "archive_cleaned")
EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations")

# Text-to-speech handling
TTS_MP3_PATH = os.path.join(BASE_DIR, 'data', 'audio_files', "tts.mp3")  # text-to-speech mp3 file
SPEAKER_WAV = os.path.join(BASE_DIR, 'data', 'audio_files', 'clone_from', "us_male_saleh.wav")  # text-to-speech model file

# OpenAI GPT
MAX_TOKENS = 4096  # max tokens for GPT-4
GPT_MODEL = "gpt-3.5-turbo"  # 4,096 tokens
# GPT_MODEL = "gpt-3.5-turbo-1106"  # 4,096 tokens

# GPT_MODEL = "gpt-4"  # 8,192 tokens

## GPT_MODEL = "gpt-4.0-turbo"  # 8,192 tokens # This does not work!
# GPT_MODEL = "gpt-4-1106-preview"  # 128,000 tokens
# GPT_MODEL = "gpt-4-vision-preview"  # 128,000 tokens
OPENAI_API_KEY = OPENAI_API_KEY
GPT_CHAT_1_INSTRUCTIONS = """You are a dull person and gullible person who is easy to persuade.
You want to share information. Do not call them a scam. Keep conversation going.
Ask follow-up questions. Do not give any personal information. Greet them in the start."""
GPT_CHAT_2_INSTRUCTIONS = """You are good at pattern following.
You are a person and not a language model. Do not call them a scam."""
GPT_CHAT_3_INSTRUCTIONS = """You are a dull person and gullible person who is easy to persuade.
You want to share information. Do not call them a scam. Keep conversation going.
Ask follow-up questions. Do not give any personal information. Reply with short sentences.
You are a person and not a language model."""
GPT_STOP_SEQUENCES = ["I am an AI", "I'm an AI", "AI", "As an artificial"]
GPT_PRESENCE_PENALTY = 0.5
GPT_FREQUENCY_PENALTY = 0.5

# MODEL handling
MODEL_HISTORY_PATH = os.path.join(BASE_DIR, "models", "history.json")  # list of responders and times used
CLASSIFIER_PATH = os.path.join(BASE_DIR, "models", "classifier", "final-model.pt")
FILENAME1 = os.path.join(BASE_DIR, "data", "eliza_dane_green_days.json")
FILENAME2 = os.path.join(BASE_DIR, "data", "tushie-blessing.json")
FILENAME3 = os.path.join(BASE_DIR, "data", "noogie_california_dreamin.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "responder", "templates")
CONTENT = "I am writing to inform you that your compensation/winning payment of $10 was approved today by the Board and Directors of United Nation Committee on Rewards and Compensation. You are therefore advised to reconfirm your details to enable the financial department release your payment to you without any delay. Thus, reconfirm the following: 1. Your Full Name: 2. Your residential address: 3. Your direct phone number: We look forward to your prompt response.  Thank you. George McConnell, citibankmanagingd@gmail.com Director of Payments, United Nations Ministry of Foreign Affair"
OLD_COVERSATIONS_CSV = os.path.join(BASE_DIR, "data", "old_conversations.csv")
# CRAWLER CONF
CRAWLER_PROG_DIR = os.path.join(BASE_DIR, "cache")  # has crawled cache
MAX_PAGE_SL = 2 # max page for scammer list
MAX_PAGE_SS = 100 # max page for scammer sites

# MAILGUN
MAILGUN_API_KEY = MAILGUN_API_KEY
MAILGUN_SMTP_SERVER = 'smtp.mailgun.org'
MAILGUN_SMTP_PORT = 587
MAILGUN_API_BASE_URL = 'https://api.mailgun.net/v3'
MAILGUN_DOMAIN_NAME = MAILGUN_DOMAIN_NAME

# Twilio
TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBERS = TWILIO_PHONE_NUMBERS
TWILIO_CALL_URL = TWILIO_CALL_URL

# ElevenLabs
ELEVENLABS_API_KEY = ELEVENLABS_API_KEY
ELEVENLABS_PREMADE_VOICES = os.path.join(BASE_DIR, "elevenlabs", "elevenlabs_voices.json")