from flask import Blueprint
roles_bp = Blueprint('roles', __name__)
@roles_bp.route('/roles')
def roles():
    return "roles endpoint"
