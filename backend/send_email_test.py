import requests
from globals import MAILGUN_API_KEY, MAILGUN_API_BASE_URL, MAILGUN_DOMAIN_NAME
def send_email(username, address, target, subject, text):
    print(f"Trying to send an email from {address} to {target}")
    with open("emailing_service/template.html", "r") as f:
        template = f.read()
    res = requests.post(
        f"{MAILGUN_API_BASE_URL}/{MAILGUN_DOMAIN_NAME}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"{username} <{address}>",
              "to": target,
              "subject": str(subject),
              "html": template.replace("{{{content}}}", text).replace("\n", "<br>")})
    if not ("Queued." in res.text):
        print(f"Failed to send, {res.text}")
        return False
    print(f"Email sent successfully from email: {address}, to email: {target}")
    return True
if __name__ == "__main__":
    email_from_username = "Name"
    email_from_address = f"name@{MAILGUN_DOMAIN_NAME}"
    email_to_address = "to_test@domain.com"
    email_subject = "Test Subject"
    email_body_text = "This is a test email."
    send_email(email_from_username, email_from_address, email_to_address, email_subject, email_body_text)