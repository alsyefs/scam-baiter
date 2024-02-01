import re
from .models import db_models, Role, UserRoles
from logs import LogManager
log = LogManager.get_logger()
class RolesDatabaseManager:
    @staticmethod
    def create_table():
        db_models.create_all()
    @staticmethod
    def drop_table():
        db_models.drop_all()
    @staticmethod
    def create_role(name):
        new_role = Role(name=name)
        db_models.session.add(new_role)
        db_models.session.commit()
        return new_role

    @staticmethod
    def assign_role_to_user(user, role):
        user_role = UserRoles(user_id=user.id, role_id=role.id)
        db_models.session.add(user_role)
        db_models.session.commit()

    @staticmethod
    def get_role_by_id(role_id):
        return Role.query.get(role_id)

    @staticmethod
    def get_all_roles():
        return Role.query.all()

    @staticmethod
    def delete_role(role_id):
        role = Role.query.get(role_id)
        if role:
            db_models.session.delete(role)
            db_models.session.commit()
    @staticmethod
    def update_role(role_id, name):
        role = Role.query.get(role_id)
        if role:
            role.name = name
            db_models.session.commit()
            log.info(f"Updated role {role.name}")
            return role
        else:
            return None
    @staticmethod
    def get_role_by_name(name):
        return Role.query.filter_by(name=name).first()
    
    @staticmethod
    def update_user_role(user, new_role):
        user.roles.clear()
        user.roles.append(new_role)
        db_models.session.commit()