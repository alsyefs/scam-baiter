import sqlite3
from datetime import datetime
import logging
from globals import (
    LOGGING_LEVEL, DEBUGGING_LOGS_TABLE_NAME, INFO_LOGS_TABLE_NAME, WARNING_LOGS_TABLE_NAME,
    ERROR_LOGS_TABLE_NAME, CRITICAL_LOGS_TABLE_NAME, NOTSET_LOGS_TABLE_NAME, DB_PATH
)
log = logging.getLogger('custom_logger.log_tables')
log.setLevel(LOGGING_LEVEL)
    
class LogsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(LogsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    allowed_tables = [DEBUGGING_LOGS_TABLE_NAME, INFO_LOGS_TABLE_NAME, WARNING_LOGS_TABLE_NAME, ERROR_LOGS_TABLE_NAME, CRITICAL_LOGS_TABLE_NAME, NOTSET_LOGS_TABLE_NAME]
    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.validate_table_name(table_name)
        self.create_table(table_name)
    def validate_table_name(self, table_name):
        if table_name not in self.allowed_tables:
            print(f"Invalid table name: {table_name}")
            log.error(f"Invalid table name: {table_name}")
            raise ValueError(f"Invalid table name: {table_name}")
    def drop_table(self, table_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
        except Exception as e:
            print(f"Error dropping {table_name} table: {e}")
            log.error(f"Error dropping {table_name} table: {e}")
        finally:
            conn.close()
    def create_table(self, table_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    level TEXT,
                    message TEXT,
                    date TEXT,
                    time TEXT,
                    file_name TEXT
                )
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error creating {table_name} table: {e}")
            log.error(f"Error creating {table_name} table: {e}")
        finally:
            conn.close()

    def insert_log(self, level, message, table_name, file_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        try:
            level_name = logging.getLevelName(level)  # Convert level number to level name
            if level_name not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NOTSET']:
                raise ValueError(f"Invalid log level: {level_name}")
            cursor.execute(f'''
                INSERT INTO {table_name} (level, message, date, time, file_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (level_name, message, formatted_date, formatted_time, file_name))
            conn.commit()
        except Exception as e:
            print(f"Error inserting log in {table_name} table: {e}")
            log.error(f"Error inserting log in {table_name} table: {e}")
        finally:
            conn.close()

    def delete_all_logs(self, table_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'DELETE FROM {table_name}')
            conn.commit()
        except Exception as e:
            print(f"Error deleting all logs in {table_name} table: {e}")
            log.error(f"Error deleting all logs in {table_name} table: {e}")
        finally:
            conn.close()

    def select_all_logs(self, table_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        logs = []
        try:
            cursor.execute(f"SELECT * FROM {table_name} order by date desc, time desc")
            logs = cursor.fetchall()
        except Exception as e:
            print(f"Error selecting all logs in {table_name} table: {e}")
            log.error(f"Error selecting all logs in {table_name} table: {e}")
        finally:
            conn.close()
        return logs
    @staticmethod
    def select_logs_by_level(level, table_name):
        # validate_table_name(table_name)
        conn = LogsDatabaseManager.get_db_connection()
        cursor = conn.cursor()
        logs = []
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE level = ? order by date desc, time desc", (level,))
            logs = cursor.fetchall()
        except Exception as e:
            log.error(f"Error selecting logs in {table_name} table: {e}")
        finally:
            conn.close()
        return logs
    
    def select_logs_by_message(self, message, table_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        logs = []
        try:
            cursor.execute("SELECT * FROM {table_name} WHERE message LIKE '%' || ? || '%' order by date desc, time desc", (message,))
            logs = cursor.fetchall()
        except Exception as e:
            print(f"Error selecting logs in {table_name} table: {e}")
            log.error(f"Error selecting logs in {table_name} table: {e}")
        finally:
            conn.close()
        return logs

    def select_log_by_id(self, log_id, table_name):
        self.validate_table_name(table_name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        log = []
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ? order by date desc, time desc", (log_id,))
            log = cursor.fetchone()
        except Exception as e:
            print(f"Error selecting log in {table_name} table: {e}")
            log.error(f"Error selecting log in {table_name} table: {e}")
        finally:
            conn.close()
        return log

    # delete all logs where their level is not related to that table:
    @staticmethod
    def delete_logs_by_level(level):
        if(level == 'DEBUG'):
            table_name = DEBUGGING_LOGS_TABLE_NAME
        elif(level == 'INFO'):
            table_name = INFO_LOGS_TABLE_NAME
        elif(level == 'WARNING'):
            table_name = WARNING_LOGS_TABLE_NAME
        elif(level == 'ERROR'):
            table_name = ERROR_LOGS_TABLE_NAME
        elif(level == 'CRITICAL'):
            table_name = CRITICAL_LOGS_TABLE_NAME
        elif(level == 'NOTSET'):
            table_name = NOTSET_LOGS_TABLE_NAME
        else:
            raise ValueError(f"Invalid log level: {level}")
        sql = f"DELETE FROM {table_name} WHERE level != ?"
        with sqlite3.connect(DB_PATH) as conn:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(sql, (level,))
            conn.commit()
            conn.close()
# # call delete_logs_by_level():
# LogsDatabaseManager.delete_logs_by_level('DEBUG')
# LogsDatabaseManager.delete_logs_by_level('INFO')
# LogsDatabaseManager.delete_logs_by_level('WARNING')
# LogsDatabaseManager.delete_logs_by_level('ERROR')
# LogsDatabaseManager.delete_logs_by_level('CRITICAL')
# LogsDatabaseManager.delete_logs_by_level('NOTSET')