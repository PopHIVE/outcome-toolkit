from flask import Flask
import os
from dataclasses import asdict
from app.ext.cache import cache
from app.ext.middleware import add_middleware
from app.ext.exceptions.handlers import add_error_handlers
from app.configs.settings import CacheSettings, FlaskConfig


def create_app() -> Flask:
    """
    Factory to generate a Flask App with registered routes.

    Returns
    -------
    Flask:
        Configured Flask App

    """
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=FlaskConfig.SECRET_KEY,
        # SESSION_COOKIE_SECURE=True, # Uncomment once HTTPS is setup??
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    cache.init_app(app, config=asdict(CacheSettings()))

    with app.app_context():
        # Initialize DB (currently don't do anything)
        # from backend.db.database import init_db
        # init_db()

        # Register Routes
        from app.routes.api.v1_refactor.geometries_routes import bp as geometries_bp
        from app.routes.api.v1_refactor.properties_routes import bp as properties_bp
        from app.routes.api.v1_refactor.misc import bp as misc_bp
        from app.routes.docs import bp as docs_bp

        # API Endpoints V1
        app.register_blueprint(geometries_bp, url_prefix='/api')
        app.register_blueprint(properties_bp, url_prefix='/api')
        app.register_blueprint(misc_bp, url_prefix='/api')

        # V2 Register Routes
        from app.routes.api.v2.details_routes import bp as details_bp
        from app.routes.api.v2.bin_routes import bp as bins_bp
        from app.routes.api.v2.geometries_routes import bp as latest_geometries_bp
        from app.routes.api.v2.overview_routes import bp as overview_bp
        from app.routes.api.v2.trendline_routes import bp as trendlines_bp
        from app.routes.api.v2.demographic_routes import bp as demographics_bp
        from app.routes.api.v2.project_routes import bp as project_bp
        from app.routes.api.v2.protected_project_routes import bp as protected_project_bp
        from app.routes.api.v2.protected_user_routes import bp as protected_user_bp
        from app.routes.api.v2.release_notes_routes import bp as release_notes_bp
        from app.routes.api.v2.email_routes import bp as email_bp
        from app.routes.api.v2.target_routes import bp as target_bp


        # API Endpoints V2
        app.register_blueprint(details_bp, url_prefix='/api/v2')
        app.register_blueprint(bins_bp, url_prefix='/api/v2')
        app.register_blueprint(latest_geometries_bp, url_prefix='/api/v2')
        app.register_blueprint(overview_bp, url_prefix='/api/v2')
        app.register_blueprint(trendlines_bp, url_prefix='/api/v2')
        app.register_blueprint(demographics_bp, url_prefix='/api/v2')
        app.register_blueprint(project_bp, url_prefix='/api/v2')
        app.register_blueprint(protected_project_bp, url_prefix='/protected/api/v2')
        app.register_blueprint(protected_user_bp, url_prefix='/protected/api/v2')
        app.register_blueprint(release_notes_bp, url_prefix='/api/v2')
        app.register_blueprint(email_bp, url_prefix='/api/v2')
        app.register_blueprint(target_bp, url_prefix='/api/v2')

        # Docs Endpoints
        if (os.getenv('SWAGGER_DOCS') == "yes"):
            app.register_blueprint(docs_bp, url_prefix='/api/docs')
        

        # Add Middleware
        add_middleware(app)
        add_error_handlers(app)

        # Add Health Check
        @app.route('/api/health-check')
        def flask_health_check():
            return 'success'

    return app
