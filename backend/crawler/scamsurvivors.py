import json
import os
import time
import requests
from bs4 import BeautifulSoup
from requests import session
from langdetect import detect, LangDetectException
from collections import namedtuple
import re
from globals import MAIL_QUEUED_DIR, CRAWLER_PROG_DIR, MAX_PAGE_SS
from logs import LogManager
log = LogManager.get_logger()
from database.emails_table import EmailsDatabaseManager

URL = "https://www.scamsurvivors.com/forum/viewforum.php?f=6"
BASE_URL = "https://www.scamsurvivors.com/forum/"
EMAIL_RE = re.compile(r"^\w+?@\w+?\.\w+$")
s = session()
TopicInfo = namedtuple("TopicInfo", ["scam_addr", "url"])
if not os.path.exists(MAIL_QUEUED_DIR):
    log.info(f"Creating directory {MAIL_QUEUED_DIR}")
    os.makedirs(MAIL_QUEUED_DIR)
if not os.path.exists(CRAWLER_PROG_DIR):
    log.info(f"Creating directory {CRAWLER_PROG_DIR}")
    os.makedirs(CRAWLER_PROG_DIR)
PROG_FILE = CRAWLER_PROG_DIR + "/ss.his"
def fetch():
    last_url = None
    if os.path.exists(PROG_FILE):
        with open(PROG_FILE, "r", encoding="utf8") as f:
            prog = json.load(f)
            last_url = prog["last_url"]
    prog_saved = False
    res = s.get(URL)
    if not res.ok:
        log.error(f"Cannot fetch the homepage for scamsurvivors")
        return
    soup = BeautifulSoup(res.text, "lxml")
    try:
        total_page = int(soup.select_one("div.pagination > a:nth-child(2) > strong:nth-child(2)").text)
    except ValueError:
        total_page = 1
    total_page = min(MAX_PAGE_SS, total_page)
    page_count = 1
    topic_list = []
    time.sleep(1)
    while page_count <= total_page:
        log.info(f"Fetching page {page_count} / {total_page} in scamsurvivors")
        res = s.get(URL + f"&start={25 * (page_count - 1)}")
        if not res.ok:
            log.error(f"Cannot fetch page {page_count} / {total_page} in scamsurvivors")
            break
        soup = BeautifulSoup(res.text, "lxml")
        for topic in soup.select("div.forumbg:not(.announcement) ul.topiclist.topics > li:not(.sticky) dt"):
            topic_title = topic.find("a", class_="topictitle")
            if topic_title is None:
                continue
            scam_addr = str(topic_title.text.strip())
            if not re.match(EMAIL_RE, scam_addr):
                continue
            url = str(topic_title["href"]).replace("./", BASE_URL, 1).strip() + "&sd=d"
            if url == last_url:
                page_count = total_page + 1
                break
            topic_list.append(TopicInfo(scam_addr, url))
            if not prog_saved:
                prog_saved = True
                prog = {"last_url": url, "time": time.time()}
                with open(PROG_FILE, "w", encoding="utf8") as f:
                    json.dump(prog, f)
        page_count += 1
    if len(topic_list) > 0:
        log.info(f"Found {len(topic_list)} scam letters in scamsurvivors")
    current_email_count = 0
    for topic_info in topic_list:
        current_email_count += 1
        log.info(f"Extracting email from {topic_info.scam_addr} ({current_email_count}/{len(topic_list)})")
        res = requests.get(topic_info.url)
        if not res.ok:
            log.error(f"Cannot fetch {topic_info.url}, {res.status_code}")
            time.sleep(3 * 60)
            continue
        soup = BeautifulSoup(res.text, "lxml")
        d = soup.select_one("div.post.bg2 > div > div.postbody > div.content > blockquote > div")
        if d is None:
            log.error(f"Cannot extract the body for {topic_info.url}")
            continue
        content = d.get_text("\n")
        try:
            if detect(content) != 'en':
                continue
        except LangDetectException:
            continue
        title = content.split("\n", maxsplit=1)[0][:30]
        from_email = topic_info.scam_addr.lower()
        to_email = "CRAWLER"
        info = {"title": title, "content": content, "url": topic_info.url, "from": from_email}
        file_name = topic_info.url.rsplit("/", 1)[1].split("&")[1].replace("t=", "ss_")
        output_path = f"{MAIL_QUEUED_DIR}/{file_name}.json"
        with open(output_path, "w", encoding="utf8") as f:
            json.dump(info, f, indent=4)
        store_email_database(from_email, to_email, title, content)
            
def store_email_database(from_email, to_email, subject, body):
    try:
        EmailsDatabaseManager.insert_email(
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body,
            is_inbound=1,
            is_outbound=0,
            is_archived=0,
            is_handled=0,
            is_queued=1,
            is_scammer=1,
            replied_from=''
        )
    except Exception as e:
        log.error(f"(database) Error while inserting crawled email: {e}")

if __name__ == '__main__':
    fetch()