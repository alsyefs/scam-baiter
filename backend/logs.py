import logging
import os
from globals import (
    LOGGING_LEVEL, DB_PATH, DEBUGGING_LOGS_TABLE_NAME, INFO_LOGS_TABLE_NAME, 
    WARNING_LOGS_TABLE_NAME, ERROR_LOGS_TABLE_NAME, CRITICAL_LOGS_TABLE_NAME, 
    NOTSET_LOGS_TABLE_NAME, INFO_LOGS_TEXT_FILE_PATH, WARNING_LOGS_TEXT_FILE_PATH, 
    ERROR_LOGS_TEXT_FILE_PATH, CRITICAL_LOGS_TEXT_FILE_PATH, NOTSET_LOGS_TEXT_FILE_PATH, 
    DEBUGGING_LOGS_TEXT_FILE_PATH
)
from database.log_tables import LogsDatabaseManager

class LogManager:
    _logger = None

    @staticmethod
    def get_logger():
        if LogManager._logger is None:
            LogManager._setup_logger()
        return LogManager._logger

    @staticmethod
    def _setup_logger():
        LogManager._logger = logging.getLogger('custom_logger')
        LogManager._logger.setLevel(LOGGING_LEVEL)
        if not LogManager._logger.handlers:
            LogManager._logger.propagate = False
            log_format = '%(asctime)s %(levelname)s: %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'
            formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
            LogManager._setup_db_handlers(formatter)
            LogManager._setup_console_handler(formatter)
    @staticmethod
    def _setup_db_handlers(formatter):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        level_to_table_name = {
            logging.DEBUG: DEBUGGING_LOGS_TABLE_NAME,
            logging.INFO: INFO_LOGS_TABLE_NAME,
            logging.WARNING: WARNING_LOGS_TABLE_NAME,
            logging.ERROR: ERROR_LOGS_TABLE_NAME,
            logging.CRITICAL: CRITICAL_LOGS_TABLE_NAME,
            logging.NOTSET: NOTSET_LOGS_TABLE_NAME
        }
        handler = DBHandler(DB_PATH, level_to_table_name, base_path)
        handler.setFormatter(formatter)
        LogManager._logger.addHandler(handler)


    @staticmethod
    def _setup_file_handlers(formatter):
        txt_log_directory = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(txt_log_directory):
            os.makedirs(txt_log_directory)

        file_paths = [DEBUGGING_LOGS_TEXT_FILE_PATH, INFO_LOGS_TEXT_FILE_PATH, WARNING_LOGS_TEXT_FILE_PATH, 
                      ERROR_LOGS_TEXT_FILE_PATH, CRITICAL_LOGS_TEXT_FILE_PATH, NOTSET_LOGS_TEXT_FILE_PATH]

        for file_path in file_paths:
            file_handler = logging.FileHandler(os.path.join(txt_log_directory, file_path))
            file_handler.setFormatter(formatter)
            LogManager._logger.addHandler(file_handler)

    @staticmethod
    def _setup_console_handler(formatter):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        LogManager._logger.addHandler(console_handler)

class DBHandler(logging.Handler):
    def __init__(self, db_path, level_to_table_name, base_path):
        super().__init__()
        self.db_path = db_path
        self.level_to_table_name = level_to_table_name
        self.base_path = base_path
        self._is_handling_log = False

    def emit(self, record):
        if self._is_handling_log:
            return
        self._is_handling_log = True
        try:
            file_name = os.path.relpath(record.pathname, start=self.base_path)
            level = record.levelno
            table_name = self.level_to_table_name.get(level, NOTSET_LOGS_TABLE_NAME)
            message = record.getMessage()
            db_manager = LogsDatabaseManager(self.db_path, table_name)
            db_manager.insert_log(level, message, table_name, file_name)
        except Exception as e:
            # print(f"backend/logs.py: Error logging to database: {e}.\nfile_name: {file_name}, level: {level}, Message: {record.getMessage()}")
            print(f"backend/logs.py: Error logging to database: {e}.\nfile_name: {file_name}, level: {level}")
            pass
        finally:
            self._is_handling_log = False