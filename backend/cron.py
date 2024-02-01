import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = TensorFlow all messages are logged (default behavior)
                                          # 1 = TensorFlow INFO messages are not printed
                                          # 2 = TensorFlow INFO and WARNING messages are not printed
                                          # 3 = TensorFlow INFO, WARNING, and ERROR messages are not printed
import shutil
import sys
import traceback
import atexit
import signal
from globals import MAIL_SAVE_DIR, MAIL_HANDLED_DIR, MAX_TOKENS, GPT_MODEL, MAX_EMAILS_TO_HANDLE, EMAILS_DIRECTORY
import tiktoken
import emailing_service
import responder
import solution_manager
from archiver import archive
import crawler
from logs import LogManager
log = LogManager.get_logger()
from database.emails_table import EmailsDatabaseManager


mymodel = GPT_MODEL
def main(crawl=True):
    log.info(f"Starting cron job with crawling {'enabled' if crawl else 'disabled'}")
    if crawl:
        crawler.fetch_all()
        log.info("Crawling done")
    email_filenames = os.listdir(MAIL_SAVE_DIR)
    count = 0
    log.info(f"Handling {len(email_filenames)} emails")
    for email_filename in email_filenames:
        if count < 5:
            try:
                log.info(f"Handling {email_filename}")
                email_path = os.path.join(MAIL_SAVE_DIR, email_filename)
                with open(email_path, "r", encoding="utf8") as f:
                    email_obj = json.load(f)
                text = email_obj["content"]
                encoding = tiktoken.encoding_for_model(mymodel)
                num_tokens = len(encoding.encode(text))
                log.info(f"Number of tokens: {num_tokens}")
                if num_tokens > MAX_TOKENS:
                    log.warning("This email is too long")
                    os.remove(email_path)
                    continue
                subject = str(email_obj["title"])
                if not subject.startswith("Re:"):
                    subject = "Re: " + subject
                scam_email = email_obj["from"]
                if "bait_email" not in email_obj:
                    if solution_manager.scam_exists(scam_email):
                        log.info("This crawled email has been replied, ignoring")
                        os.remove(email_path)
                        continue
                        # pass
                    archive(True, scam_email, "CRAWLER", email_obj["title"], text)
                    log.info("This email is just crawled, using random replier")
                    replier = responder.get_replier_randomly()
                    bait_email = solution_manager.gen_new_addr(scam_email, replier.name)
                    stored_info = solution_manager.get_stored_info(bait_email, scam_email)
                else:
                    bait_email = email_obj["bait_email"]
                    stored_info = solution_manager.get_stored_info(bait_email, scam_email)
                    if stored_info is None:
                        log.warning(f"Cannot find replier for {bait_email}")
                        os.remove(email_path)
                        continue
                    log.info(f"Found selected replier {stored_info.sol}")
                    replier = responder.get_replier_by_name(stored_info.sol)
                    if replier is None:
                        log.warning("Replier Sol_name not found")
                        os.remove(email_path)
                        continue
                try:
                    res_text = replier.get_reply(text)
                except Exception as e:
                    log.error("GENERATING ERROR")
                    log.error("", e)
                    log.error("", traceback.format_exc())
                    log.error("Due to CUDA Error, stopping whole sequence")
                    return
                res_text += f"\n\nBest wishes,\n{stored_info.username}" # Adding a signature
                send_result = emailing_service.send_email(stored_info.username, stored_info.addr, scam_email, subject, res_text)
                if send_result:
                    log.info(f"Successfully sent response to {scam_email}")
                    count += 1
                    if not os.path.exists(MAIL_HANDLED_DIR): # Move from queued to handled dir
                        os.makedirs(MAIL_HANDLED_DIR)
                    shutil.move(email_path, os.path.join(MAIL_HANDLED_DIR, email_filename))
                    try:
                        email_id = EmailsDatabaseManager.get_email_id_by_email_address_and_subject_and_body(stored_info.addr, scam_email, subject, res_text)
                        if email_id is not None:
                            EmailsDatabaseManager.set_email_handled_by_email_id(email_id)
                            EmailsDatabaseManager.set_email_outbound_by_email_id(email_id)
                            if EmailsDatabaseManager.is_scammer_by_two_emails(stored_info.addr, scam_email):
                                EmailsDatabaseManager.set_email_scammer_by_email_id(email_id)
                        else:
                            is_scammer = 0
                            if EmailsDatabaseManager.is_scammer_by_two_emails(stored_info.addr, scam_email) or bait_email == 'CRAWLER':
                                is_scammer = 1
                            EmailsDatabaseManager.insert_email(
                                from_email=stored_info.addr,
                                to_email=scam_email,
                                subject=subject,
                                body=res_text,
                                is_inbound=0,
                                is_outbound=1,
                                is_archived=0,
                                is_handled=1,
                                is_queued=0,
                                is_scammer=is_scammer,
                                replied_from=''
                            )
                    except Exception as e:
                        log.error(f"Error while inserting email into database: {e}")
                    archive(False, scam_email, bait_email, subject, res_text)
            except Exception as e:
                log.error("", e)
                log.error("", traceback.format_exc())
        else:
            break

def create_lock_file():
    try:
        with open("./lock", "w") as f:
            f.write("Running")
    except Exception as e:
        log.error(f"Error creating lock file: {e}")
def delete_lock_file():
    lock_file_path = "./lock"
    if os.path.exists(lock_file_path):
        try:
            os.remove(lock_file_path)
        except Exception as e:
            log.error(f"Error deleting lock file: {e}")
        
cleanup_executed = False
def cleanup():
    global cleanup_executed
    if cleanup_executed:
        return
    """Cleanup function to delete the lock file, called when exiting."""
    try:
        delete_lock_file()
        log.info("Cleanup completed, lock file removed.")
        log.info("--------------------- End of cron job ---------------------\n\n")
        cleanup_executed = True
    except Exception as e:
        log.error(f"An error occurred during cleanup: {e}")
def handle_sigterm(*args):
    """Handle termination signal to ensure cleanup is performed."""
    try:
        cleanup()
        log.info("Graceful termination after SIGTERM.")
    except Exception as e:
        log.error(f"Exception during SIGTERM handling: {e}")
        sys.exit(1)
    else:
        sys.exit(0)

def prepare_main(crawl=True):
    log.info("--------------------- Start of cron job ---------------------")
    signal.signal(signal.SIGTERM, handle_sigterm)
    atexit.register(cleanup)
    if os.path.exists("./lock"):
        log.info("Lock file detected, cron job is currently running.")
        return
    create_lock_file()
    arg_crawl = not ("--no-crawl" in sys.argv)
    try:
        main(crawl=arg_crawl)
        pass
    except KeyboardInterrupt:
        log.info("Script interrupted by user. Initiating cleanup...")
        cleanup()
    except Exception as e:
        log.error("An error occurred in the main execution", exc_info=True)
        log.error(f"Error in main execution: {e}")
        traceback.print_exc()
    finally:
        if 'cleanup' not in locals():
            cleanup()
if __name__ == '__main__':
    prepare_main(crawl=("--no-crawl" not in sys.argv))