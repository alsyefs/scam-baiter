import sqlite3
from datetime import datetime
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

class SmsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(SmsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_sms TEXT NOT NULL,
                    to_sms TEXT NOT NULL,
                    sms_sid TEXT NULL,
                    sms_text TEXT NOT NULL,
                    sms_recording_url TEXT NULL,
                    is_inbound INTEGER NOT NULL,
                    is_outbound INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    is_scammer INTEGER NOT NULL
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
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS sms")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def insert_sms(from_sms, to_sms, sms_sid, sms_text, sms_recording_url, is_inbound, is_outbound, is_scammer=0):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        sql_query = '''
            INSERT INTO sms (from_sms, to_sms, sms_sid, sms_text, sms_recording_url, is_inbound, is_outbound, date, time, is_scammer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_tuple = (from_sms, to_sms, sms_sid, sms_text, sms_recording_url, is_inbound, is_outbound, formatted_date, formatted_time, is_scammer)
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error inserting Sms: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms():
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms")
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms_by_id(sms_id):
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE id=?", (sms_id,))
            sms = cursor.fetchone()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms_by_sms_sid(sms_sid):
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE sms_sid=?", (sms_sid,))
            sms = cursor.fetchone()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms_by_phone_number(phone_number):
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE from_sms LIKE '%' || ? || '%' OR to_sms LIKE '%' || ? || '%'", (phone_number, phone_number))
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms_by_date(date):
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE date=?", (date,))
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms_by_time(time):
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE time=?", (time,))
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_received_sms():
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE is_inbound=1")
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sent sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sent_sms():
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE is_outbound=1")
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sent sms: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sms_by_is_scammer(is_scammer):
        try:
            conn = SmsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sms WHERE is_scammer=?", (is_scammer,))
            sms = cursor.fetchall()
            return sms
        except Exception as e:
            log.error(f"Error getting sms: {e}")
            raise
        finally:
            conn.close()