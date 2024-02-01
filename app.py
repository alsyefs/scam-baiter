import sys
from flask import Flask, jsonify, request, render_template, session
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from backend import emailing_service
from logs import LogManager
log = LogManager.get_logger()
from globals import (
    EMAILS_DIRECTORY, DB_PATH, LOGGING_LEVEL, CRAWLER_PROG_DIR,
    INFO_LOGS_TABLE_NAME, WARNING_LOGS_TABLE_NAME, ERROR_LOGS_TABLE_NAME,
    CRITICAL_LOGS_TABLE_NAME, NOTSET_LOGS_TABLE_NAME,
    ERROR_LOGS_TEXT_FILE_PATH, CRITICAL_LOGS_TEXT_FILE_PATH,
    NOTSET_LOGS_TEXT_FILE_PATH, FLASK_SECRET_KEY,
    DEFAULT_SUPER_ADMIN_USERNAME, DEFAULT_SUPER_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME, DEFAULT_USER_USERNAME, DEFAULT_USER_PASSWORD,
    DEFAULT_ADMIN_PASSWORD, CRON_JOB_PATH, MAILGUN_DOMAIN_NAME
)
from werkzeug.security import generate_password_hash
import shutil
import subprocess
from database import logs_db_manager, emails_db_manager, calls_db_manager, sms_db_manager, gpt_db_manager, settings_db_manager
from backend.database.models import db_models
from backend.database.users_table import UsersDatabaseManager
from backend.database.roles_table import RolesDatabaseManager
from backend.database.old_conversations import OldConversationsDatabaseManager
from backend.database.settings_table import SettingsDatabaseManager
from backend.endpoints.users import users_bp
from backend.endpoints.roles import roles_bp
from backend.endpoints.settings import settings_bp
from backend.endpoints.gpt import gpt_bp
from backend.endpoints.emails import emails_bp
from backend.endpoints.twilio import twilio_bp
from backend.endpoints.logs import logs_bp
from backend.endpoints.old_conversations import old_conversations_bp
from backend.cron_scheduler import run_scheduler

app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(gpt_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(emails_bp)
app.register_blueprint(twilio_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(old_conversations_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
db_models.init_app(app)

app.logger.setLevel(LOGGING_LEVEL)
app.logger.propagate = True

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        log.error(f"An error occurred while deleting file '{file_path}': {e}")
        pass
def clear_log_tables():
    logs_db_manager.drop_table(INFO_LOGS_TABLE_NAME)
    logs_db_manager.drop_table(WARNING_LOGS_TABLE_NAME)
    logs_db_manager.drop_table(ERROR_LOGS_TABLE_NAME)
    logs_db_manager.drop_table(CRITICAL_LOGS_TABLE_NAME)
    logs_db_manager.drop_table(NOTSET_LOGS_TABLE_NAME)
    logs_db_manager.create_table(INFO_LOGS_TABLE_NAME)
    logs_db_manager.create_table(WARNING_LOGS_TABLE_NAME)
    logs_db_manager.create_table(ERROR_LOGS_TABLE_NAME)
    logs_db_manager.create_table(CRITICAL_LOGS_TABLE_NAME)
    logs_db_manager.create_table(NOTSET_LOGS_TABLE_NAME)
    print("dropped and created all logs tables")
def clear_everything():
    try:
        clear_log_tables()
        emails_db_manager.drop_table()
        emails_db_manager.create_table()
        gpt_db_manager.drop_table()
        gpt_db_manager.create_table()
        calls_db_manager.drop_table()
        calls_db_manager.create_table()
        sms_db_manager.drop_table()
        sms_db_manager.create_table()
        settings_db_manager.drop_table()
        settings_db_manager.create_table()
        with app.app_context():
            db_models.drop_all()
            db_models.create_all()
        if os.path.exists(EMAILS_DIRECTORY):
            shutil.rmtree(EMAILS_DIRECTORY)
        if os.path.exists(CRAWLER_PROG_DIR):
            shutil.rmtree(CRAWLER_PROG_DIR)
    except Exception as e:
        log.error(f"An error occurred while clearing everything: {e}")
    finally:
        print("Clearing everything completed.")
def initialize_default_roles():
    roles = ['super admin', 'admin', 'user', 'guest']
    for role_name in roles:
        existing_role = RolesDatabaseManager.get_role_by_name(role_name)
        if not existing_role:
            RolesDatabaseManager.create_role(role_name)
def initialize_default_users():
    existing_super_admin = UsersDatabaseManager.get_user_by_username(DEFAULT_SUPER_ADMIN_USERNAME)
    existing_admin = UsersDatabaseManager.get_user_by_username(DEFAULT_ADMIN_USERNAME)
    existing_user = UsersDatabaseManager.get_user_by_username(DEFAULT_USER_USERNAME)
    if not existing_super_admin:
        super_admin_user = UsersDatabaseManager.create_user(DEFAULT_SUPER_ADMIN_USERNAME, DEFAULT_SUPER_ADMIN_PASSWORD)
        super_admin_role = RolesDatabaseManager.get_role_by_name('super admin')
        if super_admin_role:
            RolesDatabaseManager.assign_role_to_user(super_admin_user, super_admin_role)
    if not existing_admin:
        admin_user = UsersDatabaseManager.create_user(DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD)
        admin_role = RolesDatabaseManager.get_role_by_name('admin')
        if admin_role:
            RolesDatabaseManager.assign_role_to_user(admin_user, admin_role)
    if not existing_user:
        user_user = UsersDatabaseManager.create_user(DEFAULT_USER_USERNAME, DEFAULT_USER_PASSWORD)
        user_role = RolesDatabaseManager.get_role_by_name('user')
        if user_role:
            RolesDatabaseManager.assign_role_to_user(user_user, user_role)
def fill_old_conversations():
    try:
        if OldConversationsDatabaseManager.get_number_of_rows() >= 1244:
            print("old_conversations table already filled.")
            return
        OldConversationsDatabaseManager.drop_table()
        OldConversationsDatabaseManager.create_table()
        OldConversationsDatabaseManager.insert_data_from_csv()
        log.info("old_conversations table filled.")
    except Exception as e:
        log.error(f"An error occurred while filling OldConversationsDatabaseManager: {e}")
@app.route('/')
def index():
    user_roles = []
    try:
        if 'username' in session:
            user = UsersDatabaseManager.get_user_by_username(session['username'])
            if user:
                user_roles = [role.name for role in user.roles]
        return render_template('index.html', user_roles=user_roles)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        log.error(error_message)
        log.error("", traceback.format_exc())
        return error_message
@app.route("/favicon.ico")
def favicon():
    return ""
@app.route("/about")
def about():
    try:
        user_roles = []
        if 'username' in session:
            user = UsersDatabaseManager.get_user_by_username(session['username'])
            if user:
                user_roles = [role.name for role in user.roles]
        return render_template('about.html', user_roles=user_roles)
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
@app.route("/get_support_email")
def get_support_email():
    try:
        return jsonify({'support_email': f"support@{MAILGUN_DOMAIN_NAME}"})
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
@app.route("/get_domain")
def get_domain():
    try:
        return jsonify({'domain': f"{MAILGUN_DOMAIN_NAME}"})
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
def initialize_app():
    with app.app_context():
        db_models.create_all()
        initialize_default_roles()
        initialize_default_users()
        settings_db_manager.create_table()
        emails_db_manager.create_table()
        gpt_db_manager.create_table()
        calls_db_manager.create_table()
        sms_db_manager.create_table()
        fill_old_conversations()
@app.after_request
def apply_caching(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

if __name__ == "__main__":
    # clear_log_tables() # run this to clear all logs tables
    # clear_everything() # run this to clear everything
    # Initialize scheduler:
    run_scheduler() # run this to start the scheduler in the background
    initialize_app()
    app.run(host="0.0.0.0", port=10234, debug=True)
