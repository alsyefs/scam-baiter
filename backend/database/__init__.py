from .settings_table import SettingsDatabaseManager
from .emails_table import EmailsDatabaseManager
from .gpt_table import GPTDatabaseManager
from .calls_table import CallsDatabaseManager
from .sms_table import SmsDatabaseManager
from .log_tables import LogsDatabaseManager
from .users_table import UsersDatabaseManager
from .roles_table import RolesDatabaseManager
from .old_conversations import OldConversationsDatabaseManager
from globals import DB_PATH, INFO_LOGS_TABLE_NAME

settings_db_manager = SettingsDatabaseManager()
emails_db_manager = EmailsDatabaseManager()
gpt_db_manager = GPTDatabaseManager()
calls_db_manager = CallsDatabaseManager()
sms_db_manager = SmsDatabaseManager()
logs_db_manager = LogsDatabaseManager(DB_PATH, INFO_LOGS_TABLE_NAME)
users_db_manager = UsersDatabaseManager()
roles_db_manager = RolesDatabaseManager()
old_conversations_db_manager = OldConversationsDatabaseManager()