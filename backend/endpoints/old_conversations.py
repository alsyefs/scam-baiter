from flask import Blueprint, request, render_template, session, redirect, url_for, flash, Response
from functools import wraps
from logs import LogManager
log = LogManager.get_logger()
import traceback
from backend.database.models import User
from backend.database import old_conversations_db_manager as old_conversations
import json
from backend.database.old_conversations import OldConversationsDatabaseManager


old_conversations_bp = Blueprint('old_conversations', __name__)
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

@old_conversations_bp.route('/old_conversations')
@requires_roles('admin', 'super admin', 'user')
def index():
    user_roles = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_roles = [role.name for role in user.roles]
    return render_template('old_conversations.html', user_roles=user_roles)
    

@old_conversations_bp.route("/select_all", methods=['GET'])
@requires_roles('admin', 'super admin', 'user')
def select_all():
    try:
        list = OldConversationsDatabaseManager.select_all()
        json_list = [{'id': item[0], 'file_name': item[1], 'strategy': item[2], 'inbound_time': item[3], 'inbound_message': item[4], 'outbound_time': item[5], 'outbound_message': item[6]} for item in list]
        return Response(json.dumps(json_list), mimetype='application/json')
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return Response("An error occurred: %s" % str(e), mimetype='application/json')