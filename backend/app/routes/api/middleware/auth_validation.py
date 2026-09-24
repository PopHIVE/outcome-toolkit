import json
from flask import Flask, request, jsonify
from functools import wraps
from sqlalchemy.orm import Session
from app.models.responses import ErrorResponse


def authenticate(allowed_roles=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.db.database import db_session
            from db.datasets.common_imports import User
            
            roles_list = allowed_roles if allowed_roles is not None else []
            
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
            
            if roles_list:
                if not isinstance(roles_list, list):
                    roles_list = [roles_list]
                
                if logged_in_user.role not in roles_list:
                    error_response = ErrorResponse(error="Insufficient permissions")
                    return error_response.to_response(status_code=403)
                            
            # Pass the user to the route
            request.logged_in_user = logged_in_user
            return f(*args, **kwargs)
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