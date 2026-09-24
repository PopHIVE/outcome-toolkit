from flask import Blueprint
from markdown import markdown
from app.ext.cache import cache
from app.models.responses import HTMLResponse
import os.path

bp = Blueprint('release_notes', '__name__')

@bp.route('/data-release-notes', methods=['GET'])
@cache.cached()
def get_data_release_notes():
    with open(os.path.join(os.path.dirname(__file__), "../../../../docs/DATA-RELEASE-NOTES.md"), 'r', encoding='utf-8') as input_file:
        text = input_file.read()
        html = markdown(text)
        html_response = HTMLResponse()
        html_response.html_text = html
        return html_response.to_response()

