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
            conn.close()
    @staticmethod
    def drop_table():
        try:
            conn = GPTDatabaseManager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS gpt")
            conn.commit()
        except Exception as e:
            log.error(f"Error dropping table: {e}")
            raise
        finally:
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
            conn.close()
    @staticmethod
    def get_gpts():
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
            conn.close()
    @staticmethod
    def get_gpt_by_id(id):
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
            conn.close()
    @staticmethod
    def get_gpts_by_username(username):
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
            conn.close()
    @staticmethod
    def get_gpts_by_date(date):
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
            conn.close()
    @staticmethod
    def get_gpts_by_date_and_username(date, username):
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
            conn.close()
    @staticmethod
    def get_gpts_by_model(model):
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
            conn.close()
    @staticmethod
    def get_gpts_by_model_and_username(model, username):
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
            conn.close()