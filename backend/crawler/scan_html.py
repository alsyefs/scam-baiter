import requests
from bs4 import BeautifulSoup
import re
# url = "http://example.com"
# url = "https://www.scamsurvivors.com/forum/viewforum.php?f=6"
url = "https://scammer.info/c/scams/5"

def find_emails_and_bodies(html):
    print("Parsing the HTML content...")
    soup = BeautifulSoup(html, 'html.parser')
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)
    print(f"Found {len(emails)} email(s).")

    email_bodies = {}
    for email in emails:
        try:
            # Find the text node containing the email and retrieve parent
            parent = soup.find(text=re.compile(re.escape(email))).parent
            # Retrieve surrounding text
            body = ' '.join(parent.find_parent().stripped_strings)
        except AttributeError:
            # If the parent or body can't be found, continue to the next email
            body = "No body text found."
            print("Could not find a body for an email.")

        email_bodies[email] = body

    return email_bodies

def fetch_and_scan_url(url):
    print(f"Fetching content from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Content fetched successfully. Scanning for emails...")
        html_content = response.text
        return find_emails_and_bodies(html_content)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

emails_and_bodies = fetch_and_scan_url(url)

if emails_and_bodies:
    for email, body in emails_and_bodies.items():
        print(f"Email: {email}\nBody: {body}\n")
else:
    print("No emails found or unable to fetch the URL.")
