from flask import Blueprint, request, render_template, session, redirect, url_for, flash, Response
from functools import wraps
from logs import LogManager
log = LogManager.get_logger()
import traceback
from backend.database.models import User
from backend.database import logs_db_manager as logs
from globals import (
    DEBUGGING_LOGS_TABLE_NAME, INFO_LOGS_TABLE_NAME, WARNING_LOGS_TABLE_NAME, 
    ERROR_LOGS_TABLE_NAME, CRITICAL_LOGS_TABLE_NAME, NOTSET_LOGS_TABLE_NAME
)
import json
from backend.database.log_tables import LogsDatabaseManager


logs_bp = Blueprint('logs', __name__)
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('You need to be signed in to view this page.', 'error')
                return redirect(url_for('users.signin'))
            current_user = User.query.filter_by(username=session['username']).first()
            if current_user:
                user_roles = [role.name for role in current_user.roles]
                if any(role in roles for role in user_roles):
                    return f(*args, **kwargs)
            flash('You do not have the required permissions to view this page.', 'error')
            return redirect(url_for('index'))
        return decorated_function
    return wrapper

@logs_bp.route('/logs')
@requires_roles('admin', 'super admin')
def index():
    user_roles = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_roles = [role.name for role in user.roles]
    return render_template('logs.html', user_roles=user_roles)

@logs_bp.route("/get_logs", methods=['GET'])
@requires_roles('admin', 'super admin')
def get_logs():
    try:
        log_level = request.args.get('logLevel', None)
        if log_level:
            table_mapping = {
                'DEBUG': DEBUGGING_LOGS_TABLE_NAME,
                'INFO': INFO_LOGS_TABLE_NAME,
                'WARNING': WARNING_LOGS_TABLE_NAME,
                'ERROR': ERROR_LOGS_TABLE_NAME,
                'CRITICAL': CRITICAL_LOGS_TABLE_NAME,
                'NOTSET': NOTSET_LOGS_TABLE_NAME
            }
            table_name = table_mapping.get(log_level)
            if table_name:
                logs_list = LogsDatabaseManager.select_logs_by_level(log_level, table_name)
                logs_json = [{'id': log[0], 'level': log[1], 'message': log[2], 'date': log[3], 'time': log[4], 'file_name': log[5]} for log in logs_list]
                return Response(json.dumps(logs_json), mimetype='application/json')
            else:
                return Response("Invalid log level provided.", mimetype='application/json')
        else:
            return Response("No log level provided.", mimetype='application/json')
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return Response("An error occurred: %s" % str(e), mimetype='application/json')