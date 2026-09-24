from app.models.responses import (
    ProjectBaseRequest, 
)
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from app.routes.api.middleware.auth_validation import authenticate
from app.routes.api.middleware.project_validation import authorize_project_access
from app.db.database import db_session
from app.models.common import UserRole

# Import tables directly to avoid circular imports
from db.datasets.projects.project_tables import Project

bp = Blueprint('project', __name__)

def format_project_users(users):
    """Format users data for response"""
    users_data = []
    for user in users:
        users_data.append({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "organization": user.organization,
            "role": user.role.value
        })
    return users_data

def format_project_areas(areas):
    """Format areas data for response"""
    areas_data = []
    for area in areas:
        areas_data.append({
            "mid": area.mid,
            "type": area.type
        })
    return areas_data

def format_mid_metrics(mid_metrics):
    """Format mid metrics for response"""
    metrics_data = []
    for metric in mid_metrics:
        metrics_data.append({
            "mid": metric.area_mid,
            "metric": metric.metric_value
        })
    return metrics_data

def format_project_measurements(measurements):
    """Format project measurements data for response with metrics"""
    measurements_data = []
    for measurement in measurements:
        measurements_data.append({
            "period": measurement.period.value,
            "date_of_payout": measurement.date_of_payout,
            "actual_payout": measurement.actual_payout,
            "project_metric": measurement.project_metric,
            "national_metric": measurement.national_metric,
            "mid_metrics": format_mid_metrics(measurement.mid_metrics)
        })
    return measurements_data

def get_project_response(project):
    """Create a standardized project response"""
    return {
        "id": project.id,
        "project_name": project.project_name,
        "performance_period_from": project.performance_period_from,
        "performance_period_to": project.performance_period_to,
        "outcome": project.outcome.value,
        "performer_type": project.performer_type.value,
        "users": format_project_users(project.users),
        "areas": format_project_areas(project.areas),
        "project_measurements": format_project_measurements(project.project_measurements)
    }
 
@bp.route('/project', methods=['POST'])
# @authorize_project_access()
def get_project():
    try:
        session: Session = db_session()

        data = ProjectBaseRequest(**request.json)
        project_id = data.project_id
        
        # Get project by ID
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({"error": f'Project {project_id} not found'}), 422
        
        response_data = get_project_response(project)
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/projects/all', methods=['GET'])
# @authenticate(allowed_roles=[UserRole.SYSTEM_ADMIN, UserRole.PROGRAM_ADMIN])
def get_all_projects():
    try:
        session: Session = db_session()
        
        # Get all projects (you may want to add filtering/pagination)
        projects = session.query(Project).all()
        
        # Convert each project to response format
        response_data = []
        for project in projects:
            project_data = get_project_response(project)
            response_data.append(project_data)
        
        return jsonify({
            "projects": response_data,
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
