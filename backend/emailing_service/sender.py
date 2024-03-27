import requests
from globals import (
    MAILGUN_API_KEY, MAILGUN_API_BASE_URL, MAILGUN_DOMAIN_NAME,
    EMAIL_TEMPLATE, TARGET_EMAIL_TEST, SENDGRID_API_KEY, SENDGRID_DOMAIN_NAME
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from database.emails_table import EmailsDatabaseManager
from logs import LogManager
log = LogManager.get_logger()

# def send_email(username, address, target, subject, text):  # SendGrid API
#     # target = TARGET_EMAIL_TEST  # Email for testing to be removed in production.
#     with open(EMAIL_TEMPLATE, "r") as f:
#         template = f.read()
#     message = Mail(
#         from_email=f"{username} <{address}>",
#         to_emails=target,
#         subject=str(subject),
#         html_content=template.replace("{{{content}}}", text).replace("\n", "<br>"))
#     try:
#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)
#         if response.status_code != 202:
#             log.error(f"(SendGrid) Failed to send email from email: {address}, to email: {target} , {response.body}")
#             return False
#         log.info(f"(SendGrid) Email sent successfully from email: {address}, to email: {target}")
#     except Exception as e:
#         log.error(f"(SendGrid) Failed to send email from email: {address}, to email: {target} , {e.message}")
#         return False
#     store_sent_email_database(address, target, str(subject), text)
#     return True


def send_email(username, address, target, subject, text):  # Mailgun API
    # target = TARGET_EMAIL_TEST  # Email for testing to be removed in production.
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
            log.error(f"(Mailgun) Failed to send email from email: {address}, to email: {target} , {res.text}")
            return False
        log.info(f"(Mailgun) Email sent successfully from email: {address}, to email: {target}")
    except Exception as e:
        log.error(f"(Mailgun) Error while sending email: {e}")
        return False
    store_sent_email_database(address, target, str(subject), text)
    return True

def store_sent_email_database(email_from, email_to, email_subject, email_body):
    try:
        EmailsDatabaseManager.insert_email(
            from_email=email_from,
            to_email=email_to,
            subject=email_subject,
            body=email_body,
            is_inbound=0,
            is_outbound=1,
            is_archived=0,
            is_handled=1,
            is_queued=0,
            is_scammer=0,
            replied_from=''
        )
    except Exception as e:
        log.error(f"Error while inserting email into database: {e}")