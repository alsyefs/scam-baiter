from globals import MAIL_QUEUED_DIR, MAILGUN_DOMAIN_NAME
import json
import os
from archiver import archive
from database.emails_table import EmailsDatabaseManager
from logs import LogManager
log = LogManager.get_logger()
from datetime import datetime

# def on_receive(data):  # SendGrid setup
#     content = data.get("text", data.get("html", ""))  # Attempt to use 'text' content; fallback to 'html' if 'text' is not available.
#     from_field = str(data.get("from", "")).lower()
#     sender_email = from_field[from_field.find('<')+1:from_field.rfind('>')] if '<' in from_field and '>' in from_field else from_field
#     envelope = json.loads(data.get("envelope", "{}"))  # Parsing 'envelope' for recipient information.
#     recipient_emails = envelope.get("to", [])
#     bait_email = ""
#     for email in recipient_emails:
#         if email.endswith(MAILGUN_DOMAIN_NAME):  # Replace with your actual domain variable.
#             bait_email = email
#             break
#     res = {  # Constructing the result dictionary.
#         "from": sender_email,
#         "title": data.get("subject", ""),
#         "content": content.strip(),  # Stripping leading/trailing whitespace.
#         "bait_email": bait_email
#     }
#     filename = str(data.get("timestamp", "")) + ".json"
#     if not os.path.exists(MAIL_QUEUED_DIR):
#         os.makedirs(MAIL_QUEUED_DIR)
#     with open(f"{MAIL_QUEUED_DIR}/{filename}", "w", encoding="utf8") as f:
#         json.dump(res, f)
#     store_inbound_email_database(sender_email, bait_email, data.get("subject", ""), res["content"])
#     archive(True, res["from"], bait_email, res["title"], res["content"])

def on_receive(data):  # Mailgun setup
    stripped_text = data.get("stripped-text", "")
    stripped_signature = data.get("stripped-signature", "")
    content = stripped_text
    if stripped_signature:
        content += "\n" + stripped_signature
    res = {
        "from": str(data["sender"]).lower(),
        "title": data.get("Subject", ""),
        "content": content
    }
    raw_rec = str(data["recipient"])
    if "," in raw_rec:
        for rec in raw_rec.split(","):
            if rec.endswith(MAILGUN_DOMAIN_NAME):
                res["bait_email"] = rec
                break
    else:
        res["bait_email"] = raw_rec
    filename = str(data["timestamp"]) + ".json"
    if not os.path.exists(MAIL_QUEUED_DIR):
        os.makedirs(MAIL_QUEUED_DIR)
    with open(f"{MAIL_QUEUED_DIR}/{filename}", "w", encoding="utf8") as f:
        json.dump(res, f) # Store incoming email in a JSON file: {timestamp}.json
    store_inbound_email_database(str(data["sender"]).lower(), res["bait_email"],data.get("Subject", ""),res["content"])
    archive(True, res["from"], res["bait_email"], res["title"], res["content"])

def store_inbound_email_database(from_email, to_email, subject, body):
    try:
        EmailsDatabaseManager.insert_email(
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body,
            is_inbound=1,
            is_outbound=0,
            is_archived=1,
            is_handled=0,
            is_queued=1,
            is_scammer=0,
            replied_from=''
        )
    except Exception as e:
        log.error(f"Error while inserting email into database: {e}")