import sqlite3
from datetime import datetime
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

class EmailsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(EmailsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
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
            conn.close()
    @staticmethod
    def drop_table():
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS email")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def insert_email(from_email, to_email, subject, body, is_inbound, is_outbound, is_archived=0, is_handled=0, is_queued=0, is_scammer=0, replied_from=''):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        sql_query = '''
            INSERT INTO email (from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, date, time, is_scammer, replied_from)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_tuple = (from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, formatted_date, formatted_time, is_scammer, replied_from)
        try:
            email_id = EmailsDatabaseManager.get_email_id_by_email_address_and_subject_and_body(from_email, to_email, subject, body)
            if email_id is not None:
                EmailsDatabaseManager.update_email_by_id(email_id, from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, formatted_date, formatted_time, is_scammer, replied_from)
                return
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error inserting email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_emails():
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
            conn.close()
    @staticmethod
    def get_email_by_id(email_id):
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
            conn.close()
    @staticmethod
    def get_email_by_email_address(email_address):
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
            conn.close()
    @staticmethod
    def get_email_by_subject(subject):
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
            conn.close()
    @staticmethod
    def get_email_by_body(body):
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
            conn.close()
    @staticmethod
    def get_emails_by_date(date):
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
            conn.close()
    @staticmethod
    def get_emails_by_time(time):
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
            conn.close()
    @staticmethod
    def get_inbound_emails():
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE is_inbound=1 order by id desc")
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_outbound_emails():
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
            conn.close()
    @staticmethod
    def get_archived_emails():
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
            conn.close()
    @staticmethod
    def get_handled_emails():
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
            conn.close()
    @staticmethod
    def get_queued_emails():
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
            conn.close()
    @staticmethod
    def get_scammer_emails():
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
            conn.close()
    @staticmethod
    def get_email_by_replied_from(replied_from):
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
            conn.close()
    @staticmethod
    def get_email_id_by_email_address_and_subject_and_body(from_email, to_email, subject, body):
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
            conn.close()
    @staticmethod
    def update_email_by_id(email_id, from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, date, time, is_scammer, replied_from):
        sql_query = '''
            UPDATE email
            SET from_email=?, to_email=?, subject=?, body=?, is_inbound=?, is_outbound=?, is_archived=?, is_handled=?, is_queued=?, date=?, time=?, is_scammer=?, replied_from=?
            WHERE id=?
        '''
        data_tuple = (from_email, to_email, subject, body, is_inbound, is_outbound, is_archived, is_handled, is_queued, date, time, is_scammer, replied_from, email_id)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def set_email_archived_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_archived=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def set_email_handled_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_handled=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def set_email_queued_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_queued=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def set_email_scammer_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_scammer=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def set_email_inbound_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_inbound=1 AND is_outbound=0
            WHERE id=?
        '''
        data_tuple = (email_id,)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def set_email_outbound_by_email_id(email_id):
        sql_query = '''
            UPDATE email
            SET is_inbound=0 AND is_outbound=1
            WHERE id=?
        '''
        data_tuple = (email_id,)
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error updating email: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def is_scammer_inbound_or_outbound_by_email_address(email_address):
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
            conn.close()
    @staticmethod
    def is_scammer_by_two_emails(email_address1, email_address2):
        try:
            conn = EmailsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email WHERE (from_email=? AND to_email=?) OR (from_email=? AND to_email=?) order by id desc", (email_address1, email_address2, email_address2, email_address1))
            emails = cursor.fetchall()
            for email in emails:
                if email['is_scammer'] == 1:
                    return True
            return False
        except Exception as e:
            log.error(f"Error getting email: {e}")
            raise
        finally:
            conn.close()