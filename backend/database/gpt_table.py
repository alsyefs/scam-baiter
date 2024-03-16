import sqlite3
from datetime import datetime
from globals import (
    DB_PATH
)
from logs import LogManager
log = LogManager.get_logger()

class GPTDatabaseManager:
    db_path = DB_PATH
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(GPTDatabaseManager.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def create_table():
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gpt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT,
                    generated_text TEXT,
                    instructions TEXT,
                    model VARCHAR(50),
                    temperature FLOAT,
                    max_length INTEGER,
                    stop_sequences TEXT,
                    top_p FLOAT,
                    frequency_penalty FLOAT,
                    presence_penalty FLOAT,
                    submission_datetime DATETIME,
                    username VARCHAR(100)
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
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS gpt")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def insert_gpt(prompt, generated_text, instructions, model, temperature, max_length, stop_sequences, top_p, frequency_penalty, presence_penalty, username):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
        sql_query = '''
            INSERT INTO gpt (prompt, generated_text, instructions, model, temperature, max_length, stop_sequences, top_p, frequency_penalty, presence_penalty, submission_datetime, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_tuple = (prompt, generated_text, instructions, model, temperature, max_length, stop_sequences, top_p, frequency_penalty, presence_penalty, formatted_date + " " + formatted_time, username)
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query, data_tuple)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Error inserting gpt: {e}")
            log.error(f"Failed Query: {sql_query}")
            log.error(f"Data: {data_tuple}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts():
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt order by id desc")
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpts: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpt_by_id(id):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt WHERE id=? order by id desc", (id,))
            gpt = cursor.fetchone()
            return gpt
        except Exception as e:
            log.error(f"Error getting gpt by id: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts_by_username(username):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt WHERE username=? order by id desc", (username,))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpts by username: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts_by_date(date):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt WHERE datetime LIKE ? order by id desc", (date + "%",))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpts by date: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts_by_date_and_username(date, username):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt WHERE datetime LIKE ? AND username=? order by id desc", (date + "%", username))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpts by date and username: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts_by_model(model):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt WHERE model=? order by id desc", (model,))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpts by model: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts_by_model_and_username(model, username):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gpt WHERE model=? AND username=? order by id desc", (model, username))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpts by model and username: {e}")
            raise
        finally:
            if conn:
                conn.close()
########################################################################################
    @staticmethod
    def get_gpts_pages(page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpt_count():
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM gpt"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            log.error(f"Error counting gpt interactions: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpt_by_id_pages(id, page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt WHERE id=? ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (id, per_page, offset))
            gpt = cursor.fetchone()
            return gpt
        except Exception as e:
            log.error(f"Error getting gpt interaction by id: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_gpts_by_username_pages(username, page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt WHERE username=? ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (username, per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by username: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_gpts_by_date_pages(date, page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt WHERE datetime LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (date + "%", per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by date: {e}")
            raise
        finally:
            if conn:
                conn.close()
        
    @staticmethod
    def get_gpts_by_date_and_username_pages(date, username, page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt WHERE datetime LIKE ? AND username=? ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (date + "%", username, per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by date and username: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_gpts_by_model_pages(model, page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt WHERE model=? ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (model, per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by model: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_gpts_by_model_and_username_pages(model, username, page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            query = "SELECT * FROM gpt WHERE model=? AND username=? ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (model, username, per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by model and username: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_gpts_by_system_pages(page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            # Adjusted query to include 'system', null, and empty string as system entries
            query = """
            SELECT * FROM gpt 
            WHERE COALESCE(username, '') = '' OR username = 'system'
            ORDER BY id DESC 
            LIMIT ? OFFSET ?
            """
            cursor.execute(query, (per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by system: {e}")
            raise
        finally:
            if conn:
                conn.close()
    @staticmethod
    def get_gpts_by_users_pages(page=1, per_page=100):
        conn = None
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            # Adjusted query to exclude 'system', null, and empty strings, considering them as system entries
            query = """
            SELECT * FROM gpt 
            WHERE COALESCE(username, '') NOT IN ('', 'system')
            ORDER BY id DESC 
            LIMIT ? OFFSET ?
            """
            cursor.execute(query, (per_page, offset))
            gpts = cursor.fetchall()
            return gpts
        except Exception as e:
            log.error(f"Error getting gpt interactions by users: {e}")
            raise
        finally:
            if conn:
                conn.close()