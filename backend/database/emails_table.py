import sqlite3
from datetime import datetime, timedelta
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

ROWS_PER_PAGE = 100
PAGE_START = 1

class EmailsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(EmailsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_email TEXT NOT NULL,
                    to_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    is_inbound INTEGER NOT NULL,
                    is_outbound INTEGER NOT NULL,
                    is_archived INTEGER NOT NULL,
                    is_handled INTEGER NOT NULL,
                    is_queued INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    is_scammer INTEGER NOT NULL,
                    replied_from TEXT NOT NULL
                )
            ''')
            conn.commit()
        except Exception as e:
            log.error(f"Error creating table: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def drop_table():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS email")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def insert_email(from_email, to_email, subject, body, is_inbound, is_outbound, is_archived=0, is_handled=0, is_queued=0, is_scammer=0, replied_from=''):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        if EmailsDatabaseManager.is_scammer_by_two_emails(from_email, to_email) or is_outbound==1:
            is_scammer=1
        sql_query = '''
            INSERT INTO email (from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, date, time, is_scammer, replied_from)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_tuple = (from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, formatted_date, formatted_time, is_scammer, replied_from)
        if EmailsDatabaseManager.email_exists(from_email,to_email,subject,body):
            log.info(f"(database) Email already exists.")
            return
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
            log.info(f"(database) inserted email from ({from_email}) to ({to_email}).")
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error inserting email: {e}. Failed Query: {sql_query}. Data: {data_tuple}.")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_count():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM email"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            log.error(f"Error counting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_by_id(email_id):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE id=? order by id desc", (email_id,))
            email = cursor.fetchone()
            return email
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_by_email_address(email_address):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE from_email LIKE '%' || ? || '%' OR to_email LIKE '%' || ? || '%' order by id desc", (email_address, email_address))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_by_subject(subject):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE subject LIKE '%' || ? || '%' order by id desc", (subject,))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_by_body(body):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE body LIKE '%' || ? || '%' order by id desc", (body,))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_emails_by_date(date):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE date=? order by id desc", (date,))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_emails_by_time(time):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE time=? order by id desc", (time,))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_inbound_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_inbound=1 and to_email not like 'CRAWLER' order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_inbound_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email WHERE is_inbound=1 and to_email not like 'CRAWLER' ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_outbound_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_outbound=1 order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting sent emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_outbound_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email WHERE is_outbound=1 ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_archived_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_archived=1 order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_archived_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email WHERE is_archived=1 ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_handled_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_handled=1 order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_handled_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email WHERE is_handled=1 ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_queued_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_queued=1 order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_queued_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email WHERE is_queued=1 ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_scammer_emails():
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_scammer=1 order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_scammer_emails_pages(page=PAGE_START, per_page=100):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM email WHERE is_scammer=1 ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting emails: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_by_replied_from(replied_from):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE replied_from=? order by id desc", (replied_from,))
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_email_id_by_email_address_and_subject_and_body(from_email, to_email, subject, body):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM email WHERE from_email=? AND to_email=? AND subject=? AND body=? ORDER BY id DESC", (from_email, to_email, subject, body))
            row = cursor.fetchone()
            if row is not None:
                email_id = row[0]
                return email_id
            return None
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def email_exists(from_email, to_email, subject, body):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""SELECT date, time FROM email WHERE from_email=? AND to_email=? AND subject=? AND body=? ORDER BY id DESC LIMIT 1""", (from_email, to_email, subject, body))
            email = cursor.fetchone()
            if email is not None:
                email_date, email_time = email
                email_timestamp = datetime.strptime(f"{email_date} {email_time}", "%Y-%m-%d %H:%M:%S.%f")
                current_timestamp = datetime.now()
                if (current_timestamp - email_timestamp) > timedelta(minutes=2):  # Check if the email is newer than 1 minute
                    return False  # If the email is older than 2 minute, it's considered not a duplicate
                return True  # If within the last minute, it's a duplicate
            return False  # If no email was found, it's not a duplicate
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_last_email_by_email_address(from_email):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT body FROM email WHERE from_email=? order by id desc", (from_email,))
            email = cursor.fetchone()
            log.info(f"Last email: {email}")
            return email
        except Exception as e:
            log.error(f"Error getting last email: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_email_by_id(email_id, from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, date, time, is_scammer, replied_from):
        sql_query = '''
            UPDATE email
            SET from_email=?, to_email=?, subject=?, body=?, is_inbound=?, is_outbound=?, is_archived=?, is_handled=?, is_queued=?, date=?, time=?, is_scammer=?, replied_from=?
            WHERE id=?
        '''
        data_tuple = (from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, date, time, is_scammer, replied_from, email_id)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def set_email_archived_by_email_id(email_id):
        sql_query = '''UPDATE email SET is_archived=1 WHERE id=?'''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def remove_email_queued_flag_by_email_id(email_id):
        sql_query = '''UPDATE email SET is_queued=0 WHERE id=?'''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def set_email_handled_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_handled=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def set_email_queued_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_queued=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def set_email_scammer_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_scammer=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def set_email_inbound_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_inbound=1 AND is_outbound=0
            WHERE id=?
        '''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def set_email_outbound_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_inbound=0 AND is_outbound=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"Error updating email: {e}. Failed Query: {sql_query}. Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def is_scammer_inbound_or_outbound_by_email_address(email_address):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE from_email=? OR to_email=? order by id desc", (email_address, email_address))
            emails = cursor.fetchall()
            for email in emails:
                if email['is_scammer'] == 1:
                    return True
            return False
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def is_scammer_by_two_emails(email_address1, email_address2):
        conn = None
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM email 
            WHERE 
            ((from_email=? AND to_email=?) OR (from_email=? AND to_email=?))
            OR 
            ((from_email=? AND to_email='CRAWLER') OR (from_email='CRAWLER' AND to_email=?))
            OR
            ((from_email=? AND to_email='CRAWLER') OR (from_email='CRAWLER' AND to_email=?))
            ORDER BY id DESC
            """, (email_address1, email_address2, email_address2, email_address1, email_address1, email_address1, email_address2, email_address2))
            emails = cursor.fetchall()
            for email in emails:
                if email['is_scammer'] == 1:
                    log.info(f"Scammer email found in: ({email_address1}) or ({email_address2})")
                    return True
            log.info(f"Scammer email ({email_address1}) or ({email_address2}) not found.")
            return False
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            if conn:
                conn.close()
