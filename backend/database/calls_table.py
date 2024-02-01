import sqlite3
from datetime import datetime
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

class CallsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(CallsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_call TEXT NOT NULL,
                    to_call TEXT NOT NULL,
                    call_sid TEXT NOT NULL,
                    call_length TEXT NOT NULL,
                    call_recording_url TEXT NULL,
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
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS calls")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def insert_call(from_call, to_call, call_sid, call_length, call_recording_url, is_inbound, is_outbound, is_scammer=0):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        sql_query = '''
            INSERT INTO calls (from_call, to_call, call_sid, call_length, call_recording_url, is_inbound, is_outbound, date, time, is_scammer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_tuple = (from_call, to_call, call_sid, call_length, call_recording_url, is_inbound, is_outbound, formatted_date, formatted_time, is_scammer)
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error inserting call: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_calls():
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls")
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting calls: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_call_by_id(call_id):
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE id=?", (call_id,))
            call = cursor.fetchone()
            return call
        except Exception as e:
            log.error(f"Error getting call: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_call_by_call_sid(call_sid):
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE call_sid=?", (call_sid,))
            call = cursor.fetchone()
            return call
        except Exception as e:
            log.error(f"Error getting call: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_call_by_phone_number(phone_number):
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE from_call LIKE '%' || ? || '%' OR to_call LIKE '%' || ? || '%'", (phone_number, phone_number))
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting call: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_calls_by_date(date):
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM call WHERE date=?", (date,))
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting calls: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_calls_by_time(time):
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE time=?", (time,))
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting calls: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_received_calls():
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE is_inbound=1")
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting sent calls: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_sent_calls():
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE is_outbound=1")
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting sent calls: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_calls_by_is_scammer(is_scammer):
        try:
            conn = CallsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calls WHERE is_scammer=?", (is_scammer,))
            calls = cursor.fetchall()
            return calls
        except Exception as e:
            log.error(f"Error getting calls: {e}")
            raise
        finally:
            conn.close()