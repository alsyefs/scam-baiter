from globals import MAIL_ARCHIVE_DIR
import os
import time
import json
import hashlib
from logs import LogManager
log = LogManager.get_logger()
from database.emails_table import EmailsDatabaseManager


def email_content_hash(from_email, to_email, subject, body, direction):
    unique_content = json.dumps([from_email, to_email, subject, body, direction])
    return hashlib.md5(unique_content.encode('utf-8')).hexdigest()

def is_hash_indexed(hash_value, scam_email):
    hash_index_file_path = os.path.join(MAIL_ARCHIVE_DIR, f"{scam_email}_hash_index.txt")
    if os.path.exists(hash_index_file_path):
        with open(hash_index_file_path, "r", encoding="utf8") as f:
            if hash_value in f.read().splitlines():
                return True
    with open(hash_index_file_path, "a", encoding="utf8") as f:  # Hash not found, append it to the index file.
        f.write(hash_value + "\n")
    return False


def archive(is_inbound, scam_email, bait_email, subject, body):
    if not os.path.exists(MAIL_ARCHIVE_DIR):
        log.info(f"Creating directory {MAIL_ARCHIVE_DIR}")
        os.makedirs(MAIL_ARCHIVE_DIR)
    from_email = scam_email if is_inbound else bait_email
    to_email = bait_email if is_inbound else scam_email
    archive_content_json = {
        "type": "scam" if is_inbound else "bait",
        "time": int(time.time()),
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "body": body,
        "direction": "Inbound" if is_inbound else "Outbound"
    }
    direction = "Inbound" if is_inbound else "Outbound"
    content_hash = email_content_hash(from_email, to_email, subject, body, direction)
    if is_hash_indexed(content_hash, scam_email):
        log.info("Email content already archived, skipping...")
        return
    archive_name_json = f"{scam_email}.json"
    # Check if the email content is already archived to avoid duplicates.
    archive_path_json = os.path.join(MAIL_ARCHIVE_DIR, archive_name_json)
    if os.path.exists(archive_path_json):
        with open(archive_path_json, "r", encoding="utf8") as f:
            existing_content = f.read()
            if content_hash in existing_content:
                log.info("Email content already archived, skipping...")
                return


    with open(os.path.join(MAIL_ARCHIVE_DIR, archive_name_json), "a", encoding="utf8") as f:
        log.info(f"Storing email JSON file: {archive_name_json}")
        json.dump(archive_content_json, f)
        f.write("\n")
    
    archive_content_txt = \
        f"[{'scam' if is_inbound else 'bait'}_start]\n" \
        f'TYPE: {"scam" if is_inbound else "bait"}\n' \
        f'TIME: {int(time.time())}\n' \
        f'FROM: {scam_email if is_inbound else bait_email}\n' \
        f'TO: {bait_email if is_inbound else scam_email}\n' \
        f'SUBJECT: {subject}\n' \
        f'\n{body}\n' \
        f'DIRECTION: {"Inbound" if is_inbound else "Outbound"}\n' \
        f"[{'scam' if is_inbound else 'bait'}_end]\n" \
        f'------------------------------------------------\n\n'
        # f'\n# {"Inbound" if is_inbound else "Outbound"}\n'\
    archive_name_txt = f"{scam_email}.txt"
    with open(os.path.join(MAIL_ARCHIVE_DIR, archive_name_txt), "a", encoding="utf8") as f:
        log.info(f"Storing email text file: {archive_name_txt}")
        f.write(archive_content_txt)
    # history_filename_json = f"{scam_email}_history.json"
    # history_content = {
    #     "type": "scam" if is_inbound else "bait",
    #     "body": body
    # }
    # with open(os.path.join(MAIL_ARCHIVE_DIR, history_filename_json), "a", encoding="utf8") as f:
    #     log.info(f"Storing email JSON history file: {history_filename_json}")
    #     json.dump(history_content, f)
    #     f.write("\n")
    # history_filename_txt = f"{scam_email}_history.txt"
    # history_content_txt = f"[{'scam' if is_inbound else 'bait'}_start]\n{body}\n[{'scam' if is_inbound else 'bait'}_end]\n"
    # with open(os.path.join(MAIL_ARCHIVE_DIR, history_filename_txt), "a", encoding="utf8") as f:
    #     log.info(f"Storing email text history file: {history_filename_txt}")
    #     f.write(history_content_txt)