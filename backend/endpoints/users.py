import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database.models import db_models, User, Role
from logs import LogManager
log = LogManager.get_logger()
import traceback
from functools import wraps
from datetime import datetime

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

@users_bp.route('/users')
@requires_roles('admin', 'super admin')
def users():
    try:
        user_roles = []
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                user_roles = [role.name for role in user.roles]
        all_users = User.query.all()
        all_roles = Role.query.all()
        users_with_roles = []
        for user in all_users:
            roles = [role.name for role in user.roles]
            if 'admin' in user_roles and 'super admin' in roles:
                continue
            created = user.created.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            updated = user.updated.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            user_data = {
                'username': user.username,
                'id': user.id,
                'roles': roles,
                'created': created,
                'updated': updated
            }
            users_with_roles.append(user_data)
        return render_template('users.html', users=users_with_roles, all_roles=all_roles, user_roles=user_roles)
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return "An error occurred"

@users_bp.route("/signin", methods=["GET", "POST"])
def signin():
    try:
        if request.method == "POST":
            username = request.form.get('username').lower()
            password = request.form.get('password')
            user_exists = User.query.filter_by(username=username).first()
            if user_exists:
                if check_password_hash(user_exists.password_hash, password):
                    log.info(f"Successful login for '{username}'")
                    session['username'] = username
                    return redirect(url_for('index'))
                else:
                    log.info(f"Incorrect password for '{username}'")
            else:
                log.info(f"Sign in attempt for username: '{username}'. This user does not exist.")
            flash('Incorrect username or password', 'error')
            return render_template("signin.html")
        if 'username' in session:
            return redirect(url_for('index'))
        return render_template("signin.html")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        flash('An error occurred during sign in', 'error')
        return render_template("signin.html")


@users_bp.route("/signup", methods=["GET", "POST"])
def signup():
    try:
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            if not re.match(r"[^@]+@bristol\.ac\.uk$", username):
                pass
            if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?/~`'-=|\\])[A-Za-z\d!@#$%^&*()_+{}\[\]:;<>,.?/~`'-=|\\]{8,}$", password):
                return "Username must be an email ending with @bristol.ac.uk"
            if password != confirm_password:
                    return "Passwords do not match"
            if password == confirm_password:
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password_hash=hashed_password)
                username_exists = User.query.filter_by(username=username).first()
                if username_exists:
                    flash('Username already exists. Please choose a different username.', 'error')
                    return redirect(url_for('users.signup'))
                db_models.session.add(new_user)
                db_models.session.flush()
                guest_role = Role.query.filter_by(name='guest').first()
                if guest_role:
                    new_user.roles.append(guest_role)
                db_models.session.commit()
                log.info(f"Created user '{username}' with role 'guest'.")
                session['username'] = username
                return redirect(url_for('index'))
        return render_template("signup.html")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("", traceback.format_exc())
        return render_template("signup.html")

@users_bp.route('/check_username_exists')
@requires_roles('admin', 'super admin')
def check_username_exists():
    username = request.args.get('username').lower()
    username_exists = User.query.filter_by(username=username).first()
    return jsonify({'exists': bool(username_exists)})

@users_bp.route("/logout")
def logout():
    log.info(f"User '{session['username']}' logged out.")
    session.pop('username', None)
    return redirect(url_for('index'))

@users_bp.route('/update_role', methods=['POST'])
@requires_roles('admin', 'super admin')
def update_role():
    try:
        user_id = request.form.get('update_role')
        role_id = request.form.get(f'role_{user_id}')
        user = User.query.get(user_id)
        role = Role.query.get(role_id)
        if user and role:
            user.roles = [role]
            user.updated = datetime.utcnow()
            db_models.session.commit()
            flash('Role updated successfully!', 'success')
        else:
            flash('User or role not found.', 'danger')
        return redirect(url_for('users.users'))
    except Exception as e:
        db_models.session.rollback()
        flash('An error occurred while updating the role.', 'danger')
        log.error(f"Error updating role: {e}")
        return redirect(url_for('users.users'))

@users_bp.route('/roles')
@requires_roles('admin', 'super_admin')
def list_roles():
    try:
        all_roles = Role.query.all()
        return render_template('roles_list.html', roles=all_roles)
    except Exception as e:
        log.error("An error occurred when listing roles: %s", str(e))
        log.error("", traceback.format_exc())
        flash('An error occurred while fetching roles', 'error')
        return redirect(url_for('index'))
    
@users_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    try:
        user_roles = []
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                user_roles = [role.name for role in user.roles]
        if request.method == 'GET':
            return render_template('change_password.html', user_roles=user_roles)
        else:
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('index'), user_roles=user_roles)

            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('users.change_password'), user_roles=user_roles)
            user.password_hash = generate_password_hash(new_password)
            user.updated = datetime.utcnow()
            db_models.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('users.users'), user_roles=user_roles)

    except Exception as e:
        log.error("An error occurred when changing password: %s", str(e))
        log.error("", traceback.format_exc())
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('users.change_password'))


@users_bp.route('/clear_password', methods=['POST'])
@requires_roles('admin', 'super admin')
def clear_password():
    try:
        user_id = request.form.get('user_id')
        new_password = '123'
        user = User.query.get(user_id)
        if user:
            user.password_hash = generate_password_hash(new_password)
            user.updated = datetime.utcnow()
            db_models.session.commit()
            flash('Password updated successfully!', 'success')
        else:
            flash('User not found.', 'danger')
        return redirect(url_for('users.users'))
    except Exception as e:
        log.error("An error occurred when changing password: %s", str(e))
        log.error("", traceback.format_exc())