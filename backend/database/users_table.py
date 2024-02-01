from .models import db_models, User, Role
from werkzeug.security import generate_password_hash, check_password_hash
from logs import LogManager
log = LogManager.get_logger()

class UsersDatabaseManager:
    @staticmethod
    def create_table():
        db_models.create_all()
    @staticmethod
    def drop_table():
        db_models.drop_all()
    @staticmethod
    def create_user(username, password):
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db_models.session.add(new_user)
        db_models.session.commit()
        return new_user
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            db_models.session.delete(user)
            db_models.session.commit()
            log.info(f"Deleted user {user.username}")
    @staticmethod
    def update_user(user_id, username, password):
        user = User.query.get(user_id)
        if user:
            user.username = username
            user.password_hash = generate_password_hash(password)
            db_models.session.commit()
            log.info(f"Updated user {user.username}")
            return user
        else:
            return None

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_username_and_password(username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        else:
            return None

    @staticmethod
    def get_user_by_id_and_password(user_id, password):
        user = User.query.get(user_id)
        if user and check_password_hash(user.password_hash, password):
            return user
        else:
            return None

    @staticmethod
    def get_user_by_id_and_username(user_id, username):
        user = User.query.get(user_id)
        if user and user.username == username:
            return user
        else:
            return None

    @staticmethod
    def get_user_by_id_and_username_and_password(user_id, username, password):
        user = User.query.get(user_id)
        if user and user.username == username and check_password_hash(user.password_hash, password):
            return user
        else:
            return None
        
    @staticmethod
    def assign_role_to_user(user_id, role_id):
        user = User.query.get(user_id)
        role = Role.query.get(role_id)
        if user and role:
            user.roles.append(role)
            db_models.session.commit()
            log.info(f"Assigned role '{role.name}' to user '{user.username}'")
        else:
            log.warning(f"User or role not found. User ID: {user_id}, Role ID: {role_id}")
    
    @staticmethod
    def change_password(user_id, new_password):
        user = User.query.get(user_id)
        if user:
            user.password_hash = generate_password_hash(new_password)
            db_models.session.commit()
            log.info(f"Changed password for user '{user.username}'")
        else:
            log.warning(f"User not found. User ID: {user_id}")