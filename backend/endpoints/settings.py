from flask import Blueprint, Response, render_template, request, redirect, url_for, session, flash, jsonify
import json
from backend.database.models import db_models, User, Role
from logs import LogManager
log = LogManager.get_logger()
import traceback
from functools import wraps
from datetime import datetime
import openai
import re
from database.settings_table import SettingsDatabaseManager
from cron_scheduler import run_scheduler


settings_bp = Blueprint('settings', __name__)
users_bp = Blueprint('users', __name__)
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

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()
    
@settings_bp.route('/settings')
@requires_roles('super admin', 'admin')
def index():
    user_roles = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_roles = [role.name for role in user.roles]
    return render_template('settings.html', user_roles=user_roles)

@settings_bp.route('/get_settings')
@requires_roles('super admin', 'admin')
def get_settings():
    try:
        settings = SettingsDatabaseManager.get_settings()
        return jsonify([dict(setting) for setting in settings])
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
@settings_bp.route('/update_cron_state', methods=['POST'])
@requires_roles('super admin', 'admin')
def update_cron_state():
    try:
        data = request.get_json()
        cron_state = data['cron_state']
        SettingsDatabaseManager.update_cron_state(cron_state)
        run_scheduler()
        return jsonify({'message': 'cron state updated successfully'})
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
@settings_bp.route('/get_cron_state')
@requires_roles('super admin', 'admin')
def get_cron_state():
    try:
        cron_state_rows = SettingsDatabaseManager.get_cron_state()
        if cron_state_rows:
            cron_state = cron_state_rows[0][0]
            return jsonify({'cron_state': cron_state})
        else:
            return jsonify({'cron_state': 'unknown'})
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching cron state'})