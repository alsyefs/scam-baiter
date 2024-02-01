from globals import MAIL_SAVE_DIR, MAILGUN_DOMAIN_NAME
import json
import os
from archiver import archive
from database.emails_table import EmailsDatabaseManager
from logs import LogManager
log = LogManager.get_logger()
from datetime import datetime

def on_receive(data):
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
    try:
        email_id = EmailsDatabaseManager.get_email_id_by_email_address_and_subject_and_body(str(data["sender"]).lower(),
                                                                                            res["bait_email"],
                                                                                            data.get("Subject", ""),
                                                                                            res["content"])
        if email_id is not None:
            EmailsDatabaseManager.set_email_inbound_by_email_id(email_id)
        else:
            is_scammer = 0
            if EmailsDatabaseManager.is_scammer_by_two_emails(str(data["sender"]).lower(), res["bait_email"]):
                is_scammer = 1
            EmailsDatabaseManager.insert_email(
                from_email=str(data["sender"]).lower(),
                to_email=res["bait_email"],
                subject=data.get("Subject", ""),
                body=res["content"],
                is_inbound=1,
                is_outbound=0,
                is_archived=0,
                is_handled=0,
                is_queued=0,
                is_scammer=is_scammer,
                replied_from=''
            )
    except Exception as e:
        log.error(f"Error while inserting email into database: {e}")
    # Store incoming email in a JSON file:
    filename = str(data["timestamp"]) + ".json"
    if not os.path.exists(MAIL_SAVE_DIR):
        os.makedirs(MAIL_SAVE_DIR)
    with open(f"{MAIL_SAVE_DIR}/{filename}", "w", encoding="utf8") as f:
        json.dump(res, f)
    archive(True, res["from"], res["bait_email"], res["title"], res["content"])