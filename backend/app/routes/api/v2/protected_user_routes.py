import json
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from app.routes.api.middleware.auth_validation import authenticate 
from app.db.database import db_session  
from app.models.common import UserRole
from db.datasets.common_imports import User

bp = Blueprint('protected_user', __name__)


def format_user_projects(projects):
    """Format projects data for response"""
    projects_data = []
    for project in projects:
        projects_data.append({
            "id": project.id,
            "project_name": project.project_name,
            "performance_period_from": project.performance_period_from,
            "performance_period_to": project.performance_period_to,
            "outcome": project.outcome.value,
            "performer_type": project.performer_type.value 
        })
    return projects_data

def get_user_response(user):
    """Create a standardized user response"""
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization": user.organization,
        "role": user.role.value,
        "projects": format_user_projects(user.projects)
    }

@bp.route('/user', methods=['GET'])
@authenticate()
def get_current_user():
    try:
        prp_email = request.headers.get("prp-email")
        session: Session = db_session()
        db_user = session.query(User).filter_by(email=prp_email).first()

        if not db_user:
            return jsonify({"error": "User not found"}), 403

        return jsonify(get_user_response(db_user)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# debug endpoint to see F5 headers
@bp.route('/user/headers', methods=['GET'])
# @authenticate(allowed_roles=[UserRole.SYSTEM_ADMIN])
def get_user_headers():
    try:
        # prp_email = request.headers.get("prp-email")
        # session: Session = db_session()
        # db_user = session.query(User).filter_by(email=prp_email).first()

        # if not db_user:
        #     return jsonify({"error": "User not found"}), 403

        return jsonify(json.dumps(dict(request.headers))), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/user/<user_email>', methods=['GET'])
@authenticate(allowed_roles=[UserRole.SYSTEM_ADMIN])
def get_user(user_email):
    try:
        session: Session = db_session()
        db_user = session.query(User).filter_by(email=user_email).first()

        if not db_user:
            return jsonify({"error": "User not found"}), 403

        return jsonify(get_user_response(db_user)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@bp.route('/user/logout', methods=['POST'])
@authenticate()
def logout():
    try:
        return jsonify({"message": "User has been logged out"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500