import os
import json
from shutil import copy2
from datetime import datetime
from tqdm import tqdm
from globals import (
    BASE_DIR, MAIL_SAVE_DIR, MAIL_ARCHIVE_DIR, UNIQUE_EMAIL_QUEUED,
    UNIQUE_EMAIL_QUEUED_DUPLICATE, EMAIL_ARCHIVED_CLEANED_DIR,
    EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR, ADDR_SOL_PATH,
    EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_TOP_10
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

def get_sol_from_addr_sol_path(addr_sol_path, email_to, email_from):
    with open(addr_sol_path, 'r') as f:
        addr_sol_data = json.load(f)
    for key, value in addr_sol_data.items():
        if key.lower() == email_to.lower() or key.lower() == email_from.lower():
            if value.get('sol') == 'Chat1':
                return 'gpt-4'
            return 'gpt-3.5-turbo'
    return None


def clean_and_sort_conversations(source_directory, output_directory, conversations_directory, conversations_directory_top_10):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(conversations_directory, exist_ok=True)
    os.makedirs(conversations_directory_top_10, exist_ok=True)
    conversation_counts = {}
    total_files_to_process = sum(1 for filename in os.listdir(source_directory) if filename.endswith(".json") and not filename.endswith("_history.json"))
    with tqdm(total=total_files_to_process) as progress_bar:
        for filename in os.listdir(source_directory):
            if filename.endswith(".json") and not filename.endswith("_history.json"):
                progress_bar.update(1)
                file_path = os.path.join(source_directory, filename)
                conversations = []
                unique_emails = set()
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        try:
                            email = json.loads(line)
                            email['time'] = datetime.fromtimestamp(email['time']).strftime('%Y-%m-%d %H:%M:%S')
                            sol_name = get_sol_from_addr_sol_path(ADDR_SOL_PATH, email["to"], email["from"])
                            email["startegy"] = sol_name
                            if not sol_name:
                                email["startegy"] = 'None'
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
    if conversation_counts:
        files_with_more_than_one_conversation = 0
        total_conversations = 0
        for filename, count in conversation_counts.items():
            if count > 2:
                files_with_more_than_one_conversation += 1
                total_conversations += count
                source_path = os.path.join(output_directory, filename)
                destination_path = os.path.join(conversations_directory, filename)
                copy2(source_path, destination_path)
        top_10_max_conv_files = sorted(conversation_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"Top 10 files with the maximum number of conversations: ")
        for filename, count in top_10_max_conv_files:
            print(f"({filename}) with ({count}) conversation/s.")
            source_path = os.path.join(output_directory, filename)
            destination_path = os.path.join(conversations_directory_top_10, filename)
            copy2(source_path, destination_path)
        print(f"*** Number of files with more than one conversation: ({files_with_more_than_one_conversation}).")
        print(f"*** Total number of conversations in all files with more than one conversation: ({total_conversations}).")
    else:
        print("No files with valid conversations were found.")

if __name__ == "__main__":
    print(f"Running...")
    # print(f"Checking duplicate emails in ({os.path.relpath(MAIL_SAVE_DIR, BASE_DIR)})...")
    # check_duplicate_queued_emails()
    # print(f"Completed checking duplicate emails. Stored unique and duplicate emails in emails_queued.txt and emails_queued_duplicate.txt respectively.")
    print(f"Reading files in ({os.path.relpath(MAIL_ARCHIVE_DIR, BASE_DIR)}) for cleaning and sorting conversations...")
    clean_and_sort_conversations(MAIL_ARCHIVE_DIR, EMAIL_ARCHIVED_CLEANED_DIR, EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR, EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_TOP_10)
    print(f"1. Copied the files from ({os.path.relpath(MAIL_ARCHIVE_DIR, BASE_DIR)}), cleaned them, sorted them, added startegy, then made another copy to ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_DIR, BASE_DIR)}) without affecting the original files.")
    print(f"2. Created a copy of conversations with more than one conversation in ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR, BASE_DIR)}).")
    print(f"3. Created a copy of top 10 conversations with the maximum number of conversations in ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_TOP_10, BASE_DIR)}).")
    print(f"Done.")
