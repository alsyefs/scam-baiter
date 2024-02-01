import sqlite3
from datetime import datetime
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

class SettingsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(SettingsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        try:
            conn = SettingsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cron_state VARCHAR(50) DEFAULT 'stopped' NOT NULL,
                    settings_update_datetime DATETIME NOT NULL
                )
            ''')
            # cron_state: 'running', 'stopped', 'run_once'
            conn.commit()
        except Exception as e:
            log.error(f"Error creating table: {e}")
            raise
        finally:
            conn.close()
        SettingsDatabaseManager.insert_if_table_is_empty()
    @staticmethod
    def insert_if_table_is_empty():
        try:
            conn = SettingsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM settings''')
            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute('''INSERT INTO settings (cron_state, settings_update_datetime) VALUES (?, ?)''', ('stopped', datetime.now()))
                conn.commit()
                # log.info(f"Inserted default settings")
                print(f"Inserted default settings")
        except Exception as e:
            log.error(f"Error inserting default settings: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def drop_table():
        try:
            conn = SettingsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS settings")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_settings():
        try:
            conn = SettingsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM settings''')
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            log.error(f"Error getting settings: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_cron_state():
        try:
            conn = SettingsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT cron_state FROM settings''')
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            log.error(f"Error getting cron_state: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def update_cron_state(cron_state):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%Y-%m-%d")
            formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
            update_datetime = formatted_date + " " + formatted_time
            conn = SettingsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''UPDATE settings SET cron_state = ?, settings_update_datetime = ?''', (cron_state, update_datetime))
            conn.commit()
            # cron_state: 'running', 'stopped', 'run_once'
            log.info(f"Updated cron_state to {cron_state}")
        except Exception as e:
            log.error(f"Error updating cron_state: {e}")
            raise
        finally:
            conn.close()