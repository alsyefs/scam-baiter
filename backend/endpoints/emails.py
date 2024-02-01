from functools import wraps
from backend import emailing_service
from flask import Blueprint, Response, render_template, request, redirect, url_for, session, flash, jsonify
from backend.database.models import db_models, User, Role
from database.emails_table import EmailsDatabaseManager
from logs import LogManager
log = LogManager.get_logger()
import traceback

emails_bp = Blueprint('emails', __name__)
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

@emails_bp.route('/emails')
@requires_roles('admin', 'super admin')
def index():
    user_roles = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_roles = [role.name for role in user.roles]
    return render_template('emails.html', user_roles=user_roles)

@emails_bp.route("/email_inbox", methods=["GET", "POST"])
def scam_inbox():
    if request.method == "POST":
        try:
            emailing_service.on_receive(request.form)
        except Exception as e:
            log.error("An error occurred: %s", str(e))
            log.error("", traceback.format_exc())
    return "ok"

@emails_bp.route('/create_emails_table')
@requires_roles('admin', 'super admin')
def create_emails_table():
    EmailsDatabaseManager.create_table()
    return jsonify({'message': 'Emails table created successfully'})

@emails_bp.route('/drop_emails_table')
@requires_roles('admin', 'super admin')
def drop_emails_table():
    EmailsDatabaseManager.drop_table()
    return jsonify({'message': 'Emails table dropped successfully'})

@emails_bp.route('/insert_email', methods=['POST'])
@requires_roles('admin', 'super admin')
def insert_email():
    data = request.json
    EmailsDatabaseManager.insert_email(**data)
    return jsonify({'message': 'Email inserted successfully'})

@emails_bp.route('/get_emails')
@requires_roles('admin', 'super admin')
def get_emails():
    emails = EmailsDatabaseManager.get_emails()
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/get_email/<int:email_id>')
@requires_roles('admin', 'super admin')
def get_email(email_id):
    email = EmailsDatabaseManager.get_email_by_id(email_id)
    return jsonify(dict(email)) if email else 'Email not found', 404

@emails_bp.route('/get_email_by_email_address/<string:email_address>')
@requires_roles('admin', 'super admin')
def get_email_by_email_address(email_address):
    emails = EmailsDatabaseManager.get_email_by_email_address(email_address)
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/get_email_by_subject/<string:subject>')
@requires_roles('admin', 'super admin')
def get_email_by_subject(subject):
    emails = EmailsDatabaseManager.get_email_by_subject(subject)
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/get_email_by_body/<string:body>')
@requires_roles('admin', 'super admin')
def get_email_by_body(body):
    emails = EmailsDatabaseManager.get_email_by_body(body)
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/get_all_emails')
@requires_roles('admin', 'super admin')
def get_all_emails():
    emails = EmailsDatabaseManager.get_emails()
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/get_inbound_emails')
@requires_roles('admin', 'super admin')
def get_inbound_emails():
    emails = EmailsDatabaseManager.get_inbound_emails()
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/get_outbound_emails')
@requires_roles('admin', 'super admin')
def get_outbound_emails():
    emails = EmailsDatabaseManager.get_outbound_emails()
    return jsonify([dict(email) for email in emails])
@emails_bp.route('/get_scammer_emails')
@requires_roles('admin', 'super admin')
def get_scammer_emails():
    emails = EmailsDatabaseManager.get_scammer_emails()
    return jsonify([dict(email) for email in emails])
@emails_bp.route('/get_archived_emails')
@requires_roles('admin', 'super admin')
def get_archived_emails():
    emails = EmailsDatabaseManager.get_archived_emails()
    return jsonify([dict(email) for email in emails])
@emails_bp.route('/get_handled_emails')
@requires_roles('admin', 'super admin')
def get_handled_emails():
    emails = EmailsDatabaseManager.get_handled_emails()
    return jsonify([dict(email) for email in emails])
@emails_bp.route('/get_queued_emails')
@requires_roles('admin', 'super admin')
def get_queued_emails():
    emails = EmailsDatabaseManager.get_queued_emails()
    return jsonify([dict(email) for email in emails])

@emails_bp.route('/send_email', methods=['POST'])
@requires_roles('admin', 'super admin')
def send_email():
    username = request.json['username']
    address = request.json['address']
    target = request.json['target']
    subject = request.json['subject']
    text = request.json['text']
    emailing_service.send_email(username, address, target, subject, text)
    return jsonify({'message': 'Email sent successfully'})