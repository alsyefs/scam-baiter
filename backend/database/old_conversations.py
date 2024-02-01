import csv
import sqlite3
from globals import (
    DB_PATH, OLD_COVERSATIONS_CSV
)
from logs import LogManager
log = LogManager.get_logger()

class OldConversationsDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(OldConversationsDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS old_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    inbound_time TEXT NOT NULL,
                    inbound_message TEXT NOT NULL,
                    outbound_time TEXT NOT NULL,
                    outbound_message TEXT NOT NULL
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
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS old_conversations")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def insert_data_from_csv():
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            with open(OLD_COVERSATIONS_CSV, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute('''
                        INSERT INTO old_conversations (file_name, strategy, inbound_time, inbound_message, outbound_time, outbound_message)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (row['file_name'], row['strategy'], row['inbound_time'], row['inbound'], row['outbound_time'], row['outbound']))

            conn.commit()
        except Exception as e:
            log.error(f"Error inserting data from CSV: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def select_all():
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM old_conversations")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            log.error(f"Error selecting all: {e}")
            raise
        finally:
            conn.close()
    @staticmethod
    def get_number_of_rows():
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM old_conversations")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            log.error(f"Error getting number of rows: {e}")
            raise
        finally:
            conn.close()