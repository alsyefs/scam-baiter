import requests
from globals import (
    MAILGUN_API_KEY, MAILGUN_API_BASE_URL, MAILGUN_DOMAIN_NAME,
    EMAIL_TEMPLATE, MAILGUN_TARGET_EMAIL_TEST
)
from database.emails_table import EmailsDatabaseManager
from logs import LogManager
log = LogManager.get_logger()

def send_email(username, address, target, subject, text):
    target = MAILGUN_TARGET_EMAIL_TEST  # Email for testing to be removed in production.
    with open(EMAIL_TEMPLATE, "r") as f:
        template = f.read()
    try:
        res = requests.post(
            f"{MAILGUN_API_BASE_URL}/{MAILGUN_DOMAIN_NAME}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={"from": f"{username} <{address}>",
                "to": target,
                "subject": str(subject),
                "html": template.replace("{{{content}}}", text).replace("\n", "<br>")})
        if not ("Queued." in res.text):
            log.error(f"Failed to send email from email: {address}, to email: {target} , {res.text}")
            return False
        log.info(f"Email sent successfully from email: {address}, to email: {target}")
    except Exception as e:
        log.error(f"Error while sending email: {e}")
        return False
    try:
        EmailsDatabaseManager.insert_email(
            from_email=address,
            to_email=target,
            subject=str(subject),
            body=text,
            is_inbound=0,
            is_outbound=1,
            is_archived=0,
            is_handled=0,
            is_queued=0,
            is_scammer=0,
            replied_from=''
        )
    except Exception as e:
        log.error(f"Error while inserting email into database: {e}")
    return True
