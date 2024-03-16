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
        conn = None
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
            if conn:
                conn.close()
    @staticmethod
    def drop_table():
        conn = None
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS old_conversations")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def insert_data_from_csv():
        conn = None
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
            if conn:
                conn.close()

    @staticmethod
    def select_all():
        conn = None
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
            if conn:
                conn.close()

    @staticmethod
    def select_all_pages(page=1, per_page=100):
        conn = None
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            cursor.execute("SELECT * FROM old_conversations ORDER BY id LIMIT ? OFFSET ?", (per_page, offset))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            log.error(f"Error selecting page: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_number_of_rows():
        conn = None
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
            if conn:
                conn.close()
    
    @staticmethod
    def get_conversation_count():
        conn = None
        try:
            conn = OldConversationsDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM old_conversations"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            log.error(f"Error counting old_conversations: {e}")
            raise
        finally:
            if conn:
                conn.close()