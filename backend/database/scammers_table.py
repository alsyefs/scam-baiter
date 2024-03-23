import sqlite3
from datetime import datetime, timedelta
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

ROWS_PER_PAGE = 100
PAGE_START = 1

class ScammersDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(ScammersDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scammers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scammer_email_address TEXT NULL,
                    scammer_email_summary_context TEXT NULL,
                    baiter_email_address TEXT NULL,
                    baiter_username TEXT NULL,
                    baiter_email_strategy TEXT NULL,
                    phone_number TEXT NULL,
                    whatsapp_number TEXT NULL,
                    telegram_username TEXT NULL,
                    datetime datetime DEFAULT CURRENT_TIMESTAMP
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
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS scammers")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def insert_scammer(scammer_email_address="", scammer_email_summary_context="", baiter_email_address="", baiter_username="", baiter_email_strategy="", phone_number="", whatsapp_number="", telegram_username=""):
        formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        sql_query = '''
            INSERT INTO scammers (scammer_email_address, scammer_email_summary_context, baiter_email_address, baiter_username, baiter_email_strategy, phone_number, whatsapp_number, telegram_username, datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_tuple = (scammer_email_address, scammer_email_summary_context, baiter_email_address, baiter_username, baiter_email_strategy, phone_number, whatsapp_number, telegram_username, formatted_datetime)
        if ScammersDatabaseManager.scammer_exists(scammer_email_address):  # I am not checking for baiter_email_address because a baiter can have multiple scammers and I assume uniquness is based on scammer_email_address
            log.info(f"(database) Scammer already exists: {scammer_email_address}")
            return
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
            log.info(f"(database) Scammer inserted: {scammer_email_address}")
        except Exception as e:
            log.error(f"Error inserting scammer: {e}. Failed query: {sql_query}. Data tuple: {data_tuple}.")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_scammer_summary_context(scammer_email_address="", scammer_email_summary_context="", baiter_email_address="", baiter_username="", baiter_email_strategy=""):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE scammers SET scammer_email_summary_context = ?
                WHERE scammer_email_address = ? AND baiter_email_address = ? AND baiter_username = ? AND baiter_email_strategy = ?
            ''', (scammer_email_summary_context, scammer_email_address, baiter_email_address, baiter_username, baiter_email_strategy))
            conn.commit()
            log.info(f"(database) Scammer updated for: ({scammer_email_address}) with new summary context: ({scammer_email_summary_context}).")
        except Exception as e:
            log.error(f"Error updating scammer: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def scammer_exists(scammer_email_address=""):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM scammers WHERE scammer_email_address = ?""", (scammer_email_address,))
            scammer = cursor.fetchall()
            if scammer is not None:
                return False  # If the scammer was found, it's a duplicate
            return True  # If no scammer was found, it's not a duplicate
        except Exception as e:
            log.error(f"Error getting scammer: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_scammer_by_id(scammer_id):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scammers WHERE id = ?
            ''', (scammer_id,))
            return cursor.fetchone()
        except Exception as e:
            log.error(f"Error getting scammer by ID: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_scammer_info_by_scammer_email(scammer_email_address):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scammers WHERE scammer_email_address = ?
            ''', (scammer_email_address,))
            return cursor.fetchone()
        except Exception as e:
            log.error(f"Error getting scammer by email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_scammer_info_by_baiter_email(baiter_email_address):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scammers WHERE baiter_email_address = ?
            ''', (baiter_email_address,))
            return cursor.fetchone()
        except Exception as e:
            log.error(f"Error getting scammer by email: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_scammer_email_summary_context_by_scammer_email_address(scammer_email_address):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT scammer_email_summary_context FROM scammers WHERE scammer_email_address = ?
            ''', (scammer_email_address,))
            return cursor.fetchone()
        except Exception as e:
            log.error(f"Error getting scammer email summary context: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_scammers():
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scammers
            ''')
            return cursor.fetchall()
        except Exception as e:
            log.error(f"Error getting all scammers: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_scammers_paginated(page=PAGE_START):
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scammers LIMIT ? OFFSET ?
            ''', (ROWS_PER_PAGE, (page - 1) * ROWS_PER_PAGE))
            return cursor.fetchall()
        except Exception as e:
            log.error(f"Error getting all scammers paginated: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_scammer_count():
        conn = None
        try:
            conn = ScammersDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM scammers
            ''')
            return cursor.fetchone()[0]
        except Exception as e:
            log.error(f"Error getting scammer count: {e}")
            raise
        finally:
            if conn:
                conn.close()