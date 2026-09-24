import os
from app.configs.settings import Directories
from db.datasets.common_imports import User, UserProjectAssociation, Area, ProjectAreaAssociation, ProjectMeasurement
from app.db.database import (
    db_session,
    registered_tables,
)
from app.db.datasets.projects.project_loaders import load_projects
from app.db.datasets.users.user_loaders import load_users
from app.db.datasets.associations.association_loaders import load_project_areas, load_user_projects

def setup_test_projects() -> None:
    records = []
    
    records.extend(load_projects(os.path.join(Directories.STATIC_DIRECTORY, 'project_testing', 'projects_testing.csv')))
    records.extend(load_users(os.path.join(Directories.STATIC_DIRECTORY, 'project_testing','users_testing.csv')))
    records.extend(load_project_areas(os.path.join(Directories.STATIC_DIRECTORY, 'project_testing','project_area_association_testing.csv')))
    records.extend(load_user_projects(os.path.join(Directories.STATIC_DIRECTORY, 'project_testing','user_project_association_testing.csv')))

    for record in records:
        # TODO: This is inefficient and can be optimized but is written this way to avoid race condition.
        db_session.merge(record)
        db_session.commit()

if __name__ == '__main__':
    setup_test_projects()