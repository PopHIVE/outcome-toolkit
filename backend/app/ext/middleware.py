import time
import uuid
from flask import g, Flask, request, Response
from app.db.database import db_session
from app.utilities.loggerfactory import LoggerFactory


logger = LoggerFactory.getLogger(__name__, log_level='DEBUG')


def add_middleware(app: Flask) -> None:
    """
    Adds middleware to a flask App.

    Parameters
    ----------
    backend (Flask):
        Flask backend to add Middleware to.

    """

    @app.before_request
    def before_request():
        """This function executes before the routed function executes."""

        g.start = time.time()
        g.request_id = f"{str(uuid.uuid4())[:8]} ({request.headers.get('X-Request-Id', '')})"
        logger.info(f'Received Request for Resource ({request.path}) ... <{g.request_id}>')

    @app.after_request
    def after_request(response: Response) -> Response:
        """This function executes after every request."""

        # Custom
        response.headers['X-Execution-Time'] = time.time() - g.start
        response.headers['X-Backend-Request-Id'] = g.request_id

        # Security
        # response.headers["X-Frame-Options"] = "SAMEORIGIN"
        # response.headers['X-Content-Type-Options'] = 'nosniff'
        # response.headers['Content-Security-Policy'] = "default-src 'self'"
        # response.headers['X-XSS-Protection'] = '1; mode=block'

        logger.info(f"Completed Request {response.headers['X-Execution-Time']} <{g.request_id}>")

        return response

    # Safely stop DB Session when App is stopped
    @app.teardown_appcontext
    def shutdown_session(exception: Exception = None) -> None:
        db_session.remove()
