from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db_models = SQLAlchemy()
now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d")
formatted_time = now.strftime("%H:%M:%S.%f")[:-3]
class User(db_models.Model):
    id = db_models.Column(db_models.Integer, primary_key=True)
    username = db_models.Column(db_models.String(100), unique=True, nullable=False)
    password_hash = db_models.Column(db_models.String(128))
    created = db_models.Column(db_models.DateTime, default=datetime.utcnow)
    updated = db_models.Column(db_models.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = db_models.relationship('Role', secondary='user_roles', backref=db_models.backref('users', lazy=True))


class Role(db_models.Model):
    id = db_models.Column(db_models.Integer, primary_key=True)
    name = db_models.Column(db_models.String(50), unique=True)

class UserRoles(db_models.Model):
    __tablename__ = 'user_roles'
    user_id = db_models.Column(db_models.Integer, db_models.ForeignKey('user.id'), primary_key=True)
    role_id = db_models.Column(db_models.Integer, db_models.ForeignKey('role.id'), primary_key=True)

class CallConversations(db_models.Model):
    id = db_models.Column(db_models.Integer, primary_key=True)
    from_number = db_models.Column(db_models.String(255))
    to_number = db_models.Column(db_models.String(255))
    datetime = db_models.Column(db_models.DateTime, default=datetime.utcnow)
    caller_text = db_models.Column(db_models.Text)
    system_text = db_models.Column(db_models.Text)
    call_sid = db_models.Column(db_models.String(255))
    call_status = db_models.Column(db_models.String(255))
    call_duration = db_models.Column(db_models.String(255))
    recording_url = db_models.Column(db_models.String(255))
