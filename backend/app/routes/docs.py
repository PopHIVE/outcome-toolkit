import os
from app.configs.settings import Directories
from flask import Blueprint, render_template, send_from_directory

# Blueprint Example for Scalability
bp = Blueprint('docs', __name__)


@bp.route('/specs', methods=['GET'])
def get_spec():
    """Get Open API Specs yml."""

    swagger_directory = os.path.join(Directories.DOCS_DIRECTORY, 'swagger')
    return send_from_directory(os.path.realpath(swagger_directory), 'specs.yml')


@bp.route('/swagger', methods=['GET'])
def swagger_ui():
    """Get Swagger UI View."""

    return render_template('swagger_ui.html')
