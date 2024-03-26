# run: python app.py
# run: ngrok as: ngrok http --domain=DOMAIN_NAME 10234

from secret import ( 
    OPENAI_API_KEY, MAILGUN_API_KEY, MAILGUN_DOMAIN_NAME,
    FLASK_SECRET_KEY, DEFAULT_SUPER_ADMIN_USERNAME,
    DEFAULT_SUPER_ADMIN_PASSWORD, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBERS, DEFAULT_USER_USERNAME,
    DEFAULT_USER_PASSWORD, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
    TARGET_EMAIL_TEST, ELEVENLABS_API_KEY, DOMAIN_NAME,
    ASSEMBLYAI_API_KEY, SENDGRID_API_KEY, SENDGRID_DOMAIN_NAME,
    ABSTRACT_API_KEY
)
# from models.tts.phone_call_script_data import (PROMPT_KEYWORDS, RESPONSE_SENTENCES)
import logging
import os

# System variables:
FLASK_SECRET_KEY = FLASK_SECRET_KEY
HTTP_SERVER_PORT = 10234
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRON_JOB_PATH = os.path.join(BASE_DIR, "cron.py")

LOGGING_LEVEL = logging.DEBUG
logging.DEBUG
DEBUG_LOGS_TABLE_NAME = "logs_debugging"
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
MAX_EMAILS_TO_HANDLE = 4  # number of replies per cron run
EMAILS_DIRECTORY = os.path.join(BASE_DIR, "emails")  # root directory for all emails
MAIL_QUEUED_DIR = os.path.join(BASE_DIR, "emails", "queued")  # crawled and received emails
MAIL_ARCHIVE_DIR = os.path.join(BASE_DIR, "emails", "archive")  # archive
MAIL_HANDLED_DIR = os.path.join(BASE_DIR, "emails", "handled")  # emails replied to
SCAMMERS_EMAILS_FILE_PATH = os.path.join(BASE_DIR, "emails", "record.json")  # stores email addresses and names and strategies used
INBOX_MAIL = os.path.join(BASE_DIR, "emails", "inbox")  # emails received
SENT_MAIL = os.path.join(BASE_DIR, "emails", "sent")  # emails sent
READ_INBOX = os.path.join(BASE_DIR, "emails", "read")  # emails read
UNREAD_INBOX = os.path.join(BASE_DIR, "emails", "unread")  # new emails
EMAIL_TEMPLATE = os.path.join(BASE_DIR, "emailing_service", "template.html")  # email template
TARGET_EMAIL_TEST = TARGET_EMAIL_TEST  # Email for testing to be removed in production.


EMAIL_ARCHIVED_CLEANED_DIR = os.path.join(BASE_DIR, "emails", "archive_cleaned")
EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations")
EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_MOST_CONVERSATIONS = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_most_conversations")
EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_LEAST_CONVERSATIONS = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_least_conversations")
EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_LONGEST_CONVERSATIONS = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_longest_conversations")
EMAILS_REPORT_DIR = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_report")
UNIQUE_EMAIL_QUEUED = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_report", "emails_queued.txt")
UNIQUE_EMAIL_QUEUED_DUPLICATE = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_report", "emails_queued_duplicate.txt")
EMAIL_ARCHIVED_REPORT = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_report", "complete_report.txt")
EMAIL_CONVERSATIONS_REPORT_CSV = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_report", "email_conversations_report.csv")
EMAIL_CONVERSATIONS_SUMMARY_REPORT_CSV = os.path.join(BASE_DIR, "emails", "archive_cleaned_conversations_report", "email_conversations_summary_report.csv")
INVALID_EMAIL_LIST = os.path.join(BASE_DIR, "emails", "invalid_emails.json")

# Text-to-speech handling
TTS_MP3_PATH = os.path.join(BASE_DIR, 'data', 'audio_files', "tts.mp3")  # text-to-speech mp3 file
TTS_WAV_PATH = os.path.join(BASE_DIR, 'data', 'audio_files', "tts.wav")  # text-to-speech wav file
STT_MP3_PATH = os.path.join(BASE_DIR, 'data', 'audio_files', "stt.mp3")
STT_INPUT_MP3_PATH = os.path.join(BASE_DIR, 'data', 'audio_files', "stt_input")
SPEAKER_WAV = os.path.join(BASE_DIR, 'data', 'audio_files', 'clone_from', "us_male_saleh.wav")  # text-to-speech model file

# OpenAI GPT
MAX_TOKENS = 4096  # max tokens for GPT-4
# GPT_MODEL = "gpt-3.5-turbo"  # 4,096 tokens
# GPT_MODEL = "gpt-3.5-turbo-1106"  # 4,096 tokens
GPT_MODEL = "gpt-4"  # 8,192 tokens
## GPT_MODEL = "gpt-4.0-turbo"  # 8,192 tokens # This does not work!
# GPT_MODEL = "gpt-4-1106-preview"  # 128,000 tokens
# GPT_MODEL = "gpt-4-vision-preview"  # 128,000 tokens
OPENAI_API_KEY = OPENAI_API_KEY
GPT_CHAT_1_INSTRUCTIONS = """You are a dull person and a gullible person who is easy to persuade. You want to share information. Do not call them a scam. Keep the conversation going. Ask follow-up questions. Do not give any personal information. Greet them at the start."""
GPT_CHAT_2_INSTRUCTIONS = """You are a dull person and a gullible person who is easy to persuade. You want to share information. Do not call them a scam. Keep the conversation going. Ask follow-up questions. Do not give any personal information. Greet them at the start."""
GPT_CHAT_3_INSTRUCTIONS = """You are a 73-year-old lady named Gertrude. You have minimal knowledge of using social media, but you are comfortable enough with Gmail to respond to your son in Australia and grandchildren occasionally. You are wealthy. You are not educated and now retired. Your partner passed 5 years ago. Be polite and kind. You are unaware of scams and what they look like. You must never reveal you are only role-playing. Try to build a meaningful, reciprocal relationship with the sender and treat it like a friend. Be patient and keep the conversation going, you are open to opportunities and willing to take a risk, but do not share your address or phone number. Keep your reply short, under 150 words."""
GPT_CHAT_4_INSTRUCTIONS = """You are a 73-year-old lady named Gertrude. You have minimal knowledge of using social media, but you are comfortable enough with Gmail to respond to your son in Australia and grandchildren occasionally. You are wealthy. You are not educated and now retired. Your partner passed 5 years ago. Be polite and kind. You are unaware of scams and what they look like. You must never reveal you are only role-playing. Try to build a meaningful, reciprocal relationship with the sender and treat it like a friend. Be patient and keep the conversation going, you are open to opportunities and willing to take a risk, but do not share your address or phone number."""
GPT_CHAT_5_INSTRUCTIONS = """You are a 73-year-old man named Frank. You have minimal knowledge of using social media, but you are comfortable enough with Gmail to respond to your son in Australia and grandchildren occasionally. You are wealthy. You are not educated and now retired. Your partner passed 5 years ago. Be polite and kind. You are unaware of scams and what they look like. You must never reveal you are only role-playing. Try to build a meaningful, reciprocal relationship with the sender and treat it like a friend. Be patient and keep the conversation going, you are open to opportunities and willing to take a risk, but do not share your address or phone number. Keep your reply short, under 150 words."""
GPT_CHAT_6_INSTRUCTIONS = """You are a 73-year-old man named Frank. You have minimal knowledge of using social media, but you are comfortable enough with Gmail to respond to your son in Australia and grandchildren occasionally. You are wealthy. You are not educated and now retired. Your partner passed 5 years ago. Be polite and kind. You are unaware of scams and what they look like. You must never reveal you are only role-playing. Try to build a meaningful, reciprocal relationship with the sender and treat it like a friend. Be patient and keep the conversation going, you are open to opportunities and willing to take a risk, but do not share your address or phone number."""

GPT_CHAT_TTS_INSTRUCTIONS = """You are a dull person and gullible person who is easy to persuade. You need help with your laptop from Technical Support. You want to share information. Do not call them a scam. Keep conversation going. You ask for assistance for your slow laptop. Ask follow-up questions. Do not give any personal information. Reply with short sentences. Do not offer help. You are a person and not a language model. You need help from Technical Support. You need help, you do not offer help."""
GPT_STOP_SEQUENCES = ["I am an AI", "I'm an AI", "AI", "As an artificial"]
GPT_PRESENCE_PENALTY = 0.5
GPT_FREQUENCY_PENALTY = 0.5

# MODEL handling
MODEL_HISTORY_PATH = os.path.join(BASE_DIR, "models", "history.json")  # list of responders and times used
OLD_COVERSATIONS_CSV = os.path.join(BASE_DIR, "data", "old_conversations.csv")

# Crawling handling
CRAWLER_PROG_DIR = os.path.join(BASE_DIR, "cache")  # has crawled cache
MAX_PAGE_SL = 2  # max page for scammer list
MAX_PAGE_SS = 5  # max page for scammer sites

# MAILGUN (For sending and receiving emails)
MAILGUN_API_KEY = MAILGUN_API_KEY
MAILGUN_SMTP_SERVER = 'smtp.mailgun.org'
MAILGUN_SMTP_PORT = 587
MAILGUN_API_BASE_URL = 'https://api.mailgun.net/v3'
MAILGUN_DOMAIN_NAME = MAILGUN_DOMAIN_NAME  # This is the domain name setup for Mailgun which can be similar to the web application domain name.
DOMAIN_NAME = DOMAIN_NAME  # This is the domain name for the web application.

# Abstrat API: To check emails before sending an email
ABSTRACT_API_KEY = ABSTRACT_API_KEY

# SendGrid for email sending and receiving, if not needed, leave the variables empty:
SENDGRID_API_KEY = SENDGRID_API_KEY
SENDGRID_DOMAIN_NAME = SENDGRID_DOMAIN_NAME

# Twilio (For making phone calls)
TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBERS = TWILIO_PHONE_NUMBERS
TWILIO_CALL_URL_SYNCHRONOUS = f"https://{DOMAIN_NAME}/ongoing_call_synchronous"
TWILIO_CALL_URL_ASYNCHRONOUS = f"https://{DOMAIN_NAME}/ongoing_call_asynchronous"
TWILIO_CALL_URL_SOCKET = f"https://{DOMAIN_NAME}/ongoing_call_socket"
TWILIO_RECORDING_STATUS_CALLBACK_URL = f"https://{DOMAIN_NAME}/recording_status"
TWILIO_PARTIAL_RESULT_CALLBACK_URL = f"https://{DOMAIN_NAME}/partial_result_callback"

# Assembly AI (For transcribing phone calls)
ASSEMBLYAI_API_KEY = ASSEMBLYAI_API_KEY
FINAL_TRANSCRIPTIONS = []  # The global variable representing the final transcriptions of the phone call to be used in a web socket.

# ElevenLabs (For text-to-speech)
ELEVENLABS_API_KEY = ELEVENLABS_API_KEY
ELEVENLABS_PREMADE_VOICES = os.path.join(BASE_DIR, "elevenlabs", "elevenlabs_voices.json")

# Create a secret.py file in the same directory as this file and add the following variables:

# OpenAI GPT to connect to OpenAI API:
# OPENAI_API_KEY = ""

# # Domain:
# DOMAIN_NAME = ""  # The domain name for the web application.

# # MAILGUN for email sending and receiving:
# MAILGUN_API_KEY = ""
# MAILGUN_DOMAIN_NAME = ""  # This is the domain name setup for Mailgun which can be similar to the web application domain name.
# TARGET_EMAIL_TEST = ""  # Email for testing when sending emails to be removed in production.

# # Twilio for phone calls, if not needed, leave the variables empty:
# TWILIO_ACCOUNT_SID = ""
# TWILIO_AUTH_TOKEN = ""
# TWILIO_PHONE_NUMBERS = ['+441111222333', '+15550004444']

# # Assembly AI for voice transcription, if not needed, leave the variables empty:
# ASSEMBLYAI_API_KEY = ""

# # Web application variables:
# # FLASK_SECRET_KEY can be generated using os.urandom(24) or using any random string generator.
# FLASK_SECRET_KEY = ""
# DEFAULT_SUPER_ADMIN_USERNAME = ""
# DEFAULT_SUPER_ADMIN_PASSWORD = ""
# DEFAULT_ADMIN_USERNAME = ""
# DEFAULT_ADMIN_PASSWORD = ""
# DEFAULT_USER_USERNAME = ""
# DEFAULT_USER_PASSWORD = ""

# # ElevenLabs for text-to-speech, if not needed, leave the variables empty:
# ELEVENLABS_API_KEY = ""