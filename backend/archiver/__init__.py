from globals import MAIL_ARCHIVE_DIR
import os
import time
import json
from logs import LogManager
log = LogManager.get_logger()
from database.emails_table import EmailsDatabaseManager
def archive(is_inbound, scam_email, bait_email, subject, body):
    if not os.path.exists(MAIL_ARCHIVE_DIR):
        log.info(f"Creating directory {MAIL_ARCHIVE_DIR}")
        os.makedirs(MAIL_ARCHIVE_DIR)
    from_email = scam_email if is_inbound else bait_email
    to_email = bait_email if is_inbound else scam_email
    archive_content_json = {
        "time": int(time.time()),
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "body": body,
        "direction": "Inbound" if is_inbound else "Outbound"
    }
    archive_name_json = f"{scam_email}.json"
    with open(os.path.join(MAIL_ARCHIVE_DIR, archive_name_json), "a", encoding="utf8") as f:
        log.info(f"Writing to {archive_name_json}")
        json.dump(archive_content_json, f)
        f.write("\n")
    
    try:
        email_id = EmailsDatabaseManager.get_email_id_by_email_address_and_subject_and_body(from_email, to_email, subject, body)
        if email_id is not None:
            EmailsDatabaseManager.set_email_archived_by_email_id(email_id)
            if EmailsDatabaseManager.is_scammer_by_two_emails(from_email, to_email):
                EmailsDatabaseManager.set_email_scammer_by_email_id(email_id)
        else:
            is_scammer = 0
            if EmailsDatabaseManager.is_scammer_by_two_emails(from_email, to_email) or from_email == 'CRAWLER' or to_email == 'CRAWLER':
                is_scammer = 1
            EmailsDatabaseManager.insert_email(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                body=body,
                is_inbound=1 if is_inbound else 0,
                is_outbound=0 if is_inbound else 1,
                is_archived=1,
                is_handled=0,
                is_queued=0,
                is_scammer=is_scammer,
                replied_from=''
            )
    except Exception as e:
        log.error(f"Error while inserting email into database: {e}")
    archive_content_txt = \
        f'TIME: {int(time.time())}\n' \
        f'FROM: {scam_email if is_inbound else bait_email}\n' \
        f'TO: {bait_email if is_inbound else scam_email}\n' \
        f'SUBJECT: {subject}\n' \
        f'\n{body}\n' \
        f'\n# {"Inbound" if is_inbound else "Outbound"}\n'
    archive_name_txt = f"{scam_email}.txt"
    with open(os.path.join(MAIL_ARCHIVE_DIR, archive_name_txt), "a", encoding="utf8") as f:
        log.info(f"Writing to {archive_name_txt}")
        f.write(archive_content_txt)
    history_filename_json = f"{scam_email}_history.json"
    history_content = {
        "type": "scam" if is_inbound else "bait",
        "body": body
    }
    with open(os.path.join(MAIL_ARCHIVE_DIR, history_filename_json), "a", encoding="utf8") as f:
        log.info(f"Writing to {history_filename_json}")
        json.dump(history_content, f)
        f.write("\n")
    history_filename_txt = f"{scam_email}_history.txt"
    history_content_txt = f"[{'scam' if is_inbound else 'bait'}_start]\n{body}\n[{'scam' if is_inbound else 'bait'}_end]\n"
    with open(os.path.join(MAIL_ARCHIVE_DIR, history_filename_txt), "a", encoding="utf8") as f:
        log.info(f"Writing to {history_filename_txt}")
        f.write(history_content_txt)