import json
from app.models.responses import ErrorResponse
from flask import request, jsonify
from functools import wraps
from sqlalchemy.orm import Session
from app.models.common import UserRole

def authorize_project_access(
    allowed_roles=[UserRole.SYSTEM_ADMIN, UserRole.PROGRAM_ADMIN], 
    must_be_on_project=False,
    required_project_roles=None
):
    """ Middleware to verify if the user can access the project """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.db.database import db_session
            from db.datasets.users.users_tables import User
            from db.datasets.associations.association_tables import UserProjectAssociation
            from db.datasets.projects.project_tables import Project

            # FIXME: Remove the strip_leading_comma function when ellen updates on her end
            temp_prp_email = request.headers.get("prp-email")
            if not temp_prp_email:
                error_response = ErrorResponse(error="User is not logged in")
                return error_response.to_response(status_code=401)   
            
            prp_email = strip_leading_comma(temp_prp_email)
            
            session: Session = db_session()
            logged_in_user = session.query(User).filter_by(email=prp_email).first()

            if not logged_in_user:
                error_response = ErrorResponse(error="Invalid user")
                return error_response.to_response(status_code=403)
            
            project_id = request.json.get("project_id")
            if not project_id:
                error_response = ErrorResponse(error="project_id field is required")
                return error_response.to_response(status_code=400)

            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                error_response = ErrorResponse(error="Project not found")
                return error_response.to_response(status_code=422)

            # Admin access 
            has_admin_role = logged_in_user.role in allowed_roles

            # Check if user is part of the project
            user_on_project = session.query(UserProjectAssociation).filter_by(
                user_id=logged_in_user.id, project_id=project.id
            ).first()
            
            if (has_admin_role and not must_be_on_project) or user_on_project:
                if user_on_project and required_project_roles and user_on_project.role not in required_project_roles:
                    error_response = ErrorResponse(error="Insufficient project-level permissions")
                    return error_response.to_response(status_code=403)
                                
                return f(*args, **kwargs)
            
            error_response = ErrorResponse(error="Unauthorized to access this project")
            return error_response.to_response(status_code=403)
        
        return decorated_function
    return wrapper

# FIXME: Delete function after ellen makes updates
def strip_leading_comma(s):
    """
    Removes the leading comma from a string if it exists.

    Args:
        s (str): The input string.

    Returns:
        str: The string without the leading comma.
    """
    if s.startswith(','):
        return s[1:]
    return s