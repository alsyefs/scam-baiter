import json
import os
from collections import namedtuple, defaultdict
from globals import MODEL_HISTORY_PATH
from .replier import Replier, TemplateReplier, ChatReplier1, ChatReplier2
from logs import LogManager
log = LogManager.get_logger()

replier_list = [ChatReplier1(), ChatReplier2()]
ReplyResult = namedtuple("ReplyResult", ["name", "text"])

if not os.path.exists(os.path.dirname(MODEL_HISTORY_PATH)):
    os.makedirs(os.path.dirname(MODEL_HISTORY_PATH))

if not os.path.exists(MODEL_HISTORY_PATH):
    d = {}
    for r in replier_list:
        d[r.name] = 0
    with open(MODEL_HISTORY_PATH, "w", encoding="utf8") as f:
        json.dump(d, f)


def get_replier_by_name(name):
    for r in replier_list:
        if r.name == name:
            return r
    return None

def get_replier_randomly() -> Replier:
    try:
        if os.path.exists(MODEL_HISTORY_PATH) and os.path.getsize(MODEL_HISTORY_PATH) > 0:
            with open(MODEL_HISTORY_PATH, "r", encoding="utf8") as f:
                j = json.load(f)
        else:
            j = {}
            log.info("MODEL_HISTORY_PATH is empty or does not exist. Initializing an empty dictionary.")
    except json.JSONDecodeError as e:
        log.error(f"JSON parsing error in file {MODEL_HISTORY_PATH}: {e}")
        j = {}
    except Exception as e:
        log.error(f"Unexpected error reading file {MODEL_HISTORY_PATH}: {e}")
        j = {}
    count_dict = defaultdict(int, j)
    res = min(count_dict, key=count_dict.get)
    count_dict[res] += 1
    with open(MODEL_HISTORY_PATH, "w", encoding="utf8") as f:
        json.dump(count_dict, f)
    return get_replier_by_name(res)


def get_reply_random(mail_body) -> ReplyResult:
    r = get_replier_randomly()
    text = r.get_reply(mail_body)
    res = ReplyResult(r.name, text)
    return res