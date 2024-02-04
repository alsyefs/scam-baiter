import os
import json
from shutil import copy2
from globals import (
    BASE_DIR, MAIL_SAVE_DIR, MAIL_ARCHIVE_DIR, UNIQUE_EMAIL_QUEUED,
    UNIQUE_EMAIL_QUEUED_DUPLICATE, EMAIL_ARCHIVED_CLEANED_DIR,
    EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR
)

def check_duplicate_queued_emails():
    email_set = set()
    email_dup_set = set()
    email_count = 0
    for filename in os.listdir(MAIL_SAVE_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(BASE_DIR, "emails", "queued", filename)
            with open(file_path, "r", encoding="utf8") as f:
                email = json.load(f)
                email_count += 1
                print(f"Processing email {email_count} / {len(os.listdir(MAIL_SAVE_DIR))}")
                if email["from"] in email_set:
                    email_dup_set.add(email["from"])
                else:
                    email_set.add(email["from"])
    print(f"Total number of emails to process: {email_count}")
    print(f"Number of duplicates: {len(email_dup_set)}")
    print(f"Number of unique emails: {len(email_set)}")
    total_emails_queued_to_store = len(email_set)
    email_queued_counter = 0
    with open(UNIQUE_EMAIL_QUEUED, "w", encoding="utf8") as f:
        for email in email_set:
            email_queued_counter += 1
            print(f"Storing unique queued email {email_queued_counter} / {total_emails_queued_to_store}")
            f.write(email + "\n")
    total_emails_queued_to_store_duplicate = len(email_dup_set)
    email_queued_counter_duplicate = 0
    with open(UNIQUE_EMAIL_QUEUED_DUPLICATE, "w", encoding="utf8") as f:
        for email in email_dup_set:
            email_queued_counter_duplicate += 1
            print(f"Storing duplicate queued email {email_queued_counter_duplicate} / {total_emails_queued_to_store_duplicate}")
            f.write(email + "\n")
    print("Done checking duplicate emails. Stored unique and duplicate emails in emails_queued.txt and emails_queued_duplicate.txt respectively.")

def clean_and_sort_conversations(source_directory, output_directory, conversations_directory):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(conversations_directory, exist_ok=True)
    conversation_counts = {}
    total_files_to_process = sum(1 for filename in os.listdir(source_directory) if filename.endswith(".json") and not filename.endswith("_history.json"))
    total_files_to_process_counter = 0
    for filename in os.listdir(source_directory):
        if filename.endswith(".json") and not filename.endswith("_history.json"):
            total_files_to_process_counter += 1
            print(f"Processing file {total_files_to_process_counter} / {total_files_to_process}")
            file_path = os.path.join(source_directory, filename)
            conversations = []
            unique_emails = set()
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        email = json.loads(line)
                        if email["to"].lower() != "crawler":
                            serialized_email = json.dumps({key: email[key] for key in ["from", "to", "subject", "body", "direction"]}, sort_keys=True)
                            if serialized_email not in unique_emails:
                                unique_emails.add(serialized_email)
                                conversations.append(email)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {filename}: {e}")
            if conversations:
                cleaned_file_path = os.path.join(output_directory, filename)
                with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
                    json.dump(conversations, cleaned_file, ensure_ascii=False, indent=4)
                conversation_counts[filename] = len(conversations)
    print("Report:")
    if conversation_counts:
        max_conv_file = max(conversation_counts.items(), key=lambda x: x[1])
        print(f"File with the maximum number of conversations: ({max_conv_file[0]}) with ({max_conv_file[1]}) conversation/s.")
        files_with_more_than_one_conversation = 0
        for filename, count in conversation_counts.items():
            if count > 1:
                files_with_more_than_one_conversation += 1
                source_path = os.path.join(output_directory, filename)
                destination_path = os.path.join(conversations_directory, filename)
                copy2(source_path, destination_path)
        print(f"Total number of files with more than one conversations: {files_with_more_than_one_conversation}")
    else:
        print("No files with valid conversations were found.")

if __name__ == "__main__":
    print(f"Running...")
    print(f"Checking duplicate emails in {MAIL_SAVE_DIR}...")
    check_duplicate_queued_emails()
    print(f"Completed checking duplicate emails. Stored unique and duplicate emails in emails_queued.txt and emails_queued_duplicate.txt respectively.")
    print(f"Cleaning and sorting conversations in {MAIL_ARCHIVE_DIR}...")
    clean_and_sort_conversations(MAIL_ARCHIVE_DIR, EMAIL_ARCHIVED_CLEANED_DIR, EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR)
    print(f"Completed cleaning and sorting conversations in {MAIL_ARCHIVE_DIR}.")
    print(f"Done.")
