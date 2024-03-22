from typing import Optional
from globals import SCAMMERS_EMAILS_FILE_PATH
from database.scammers_table import ScammersDatabaseManager
import json
import os
import names
from collections import namedtuple
from logs import LogManager
log = LogManager.get_logger()

StoredInfo = namedtuple("StoredInfo", ["addr", "to", "strategy", "username", "summary_context"])

if not os.path.exists(os.path.dirname(SCAMMERS_EMAILS_FILE_PATH)):
    os.makedirs(os.path.dirname(SCAMMERS_EMAILS_FILE_PATH))

if not os.path.exists(SCAMMERS_EMAILS_FILE_PATH):
    with open(SCAMMERS_EMAILS_FILE_PATH, "w", encoding="utf8") as f:
        json.dump({}, f)

def addr_exists(addr) -> bool:
    try:
        with open(SCAMMERS_EMAILS_FILE_PATH, "r", encoding="utf8") as f:
            d = json.load(f)
        if addr in d:
            return True
        return False
    except Exception as e:
        log.error(f"Error in addr_exists while checking if address exists: {e}")
        return False


def scam_exists(addr) -> bool:
    try:
        with open(SCAMMERS_EMAILS_FILE_PATH, "r", encoding="utf8") as f:
            d = json.load(f)
        for bait in d:
            if d[bait]["to"] == addr:
                return True
        return False
    except Exception as e:
        log.error(f"Error in scam_exists while checking if scam exists: {e}")
        return False


def store_addr(addr, scam_email, strategy):
    try:
        with open(SCAMMERS_EMAILS_FILE_PATH, "r", encoding="utf8") as f:
            d = json.load(f)
        d[addr] = {
            "to": scam_email,
            "strategy": strategy,
            "username": names.get_first_name(),
            "summary_context": ""
        }
        with open(SCAMMERS_EMAILS_FILE_PATH, "w", encoding="utf8") as f:
            json.dump(d, f, indent=4)
        log.info(f"Stored address {addr} for {scam_email} with {strategy}.")
        store_scammer_database(scammer_email_address=scam_email, scammer_email_summary_context="", baiter_email_address=addr, baiter_username=d[addr]["username"], baiter_email_strategy=d[addr]["strategy"])
    except Exception as e:
        log.error(f"Error in store_addr: {e}")

def update_addr(addr, scam_email, strategy, username, summary_context):
    try:
        with open(SCAMMERS_EMAILS_FILE_PATH, "r", encoding="utf8") as f:
            d = json.load(f)
        d[addr] = {
            "to": scam_email,
            "strategy": strategy,
            "username": username,
            "summary_context": summary_context
        }
        with open(SCAMMERS_EMAILS_FILE_PATH, "w", encoding="utf8") as f:
            json.dump(d, f, indent=4)
        log.info(f"Updated address {addr} for {scam_email} with {strategy}.")
        update_scammer_database(scammer_email_address=scam_email, scammer_email_summary_context=summary_context, baiter_email_address=addr, baiter_username=username, baiter_email_strategy=strategy)
    except Exception as e:
        log.error(f"Error in update_addr: {e}")

def get_stored_info(addr, scam_email) -> Optional[StoredInfo]:
    try:
        with open(SCAMMERS_EMAILS_FILE_PATH, "r", encoding="utf8") as f:
            d = json.load(f)
        obj = None
        if addr not in d:
            for bait in d:
                if d[bait]["to"] == scam_email:
                    obj = d[bait]
                    addr = bait
                    break
        else:
            obj = d[addr]
        if obj is None:
            return None
        return StoredInfo(addr, obj["to"], obj["strategy"], obj["username"], obj["summary_context"])
    except Exception as e:
        log.error(f"Error in get_stored_info: {e}")
        return None

def store_scammer_database(scammer_email_address, scammer_email_summary_context, baiter_email_address, baiter_username, baiter_email_strategy):
    try:
        ScammersDatabaseManager.insert_scammer(scammer_email_address=scammer_email_address, scammer_email_summary_context=scammer_email_summary_context, baiter_email_address=baiter_email_address, baiter_username=baiter_username, baiter_email_strategy=baiter_email_strategy)
    except Exception as e:
        log.error(f"(database) Error while inserting scammer: {e}")

def update_scammer_database(scammer_email_address, scammer_email_summary_context, baiter_email_address, baiter_username, baiter_email_strategy):
    try:
        ScammersDatabaseManager.update_scammer_summary_context(scammer_email_address=scammer_email_address, scammer_email_summary_context=scammer_email_summary_context, baiter_email_address=baiter_email_address, baiter_username=baiter_username, baiter_email_strategy=baiter_email_strategy)
    except Exception as e:
        log.error(f"(database) Error while updating scammer summary context: {e}")