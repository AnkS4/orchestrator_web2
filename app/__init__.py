from flask import Flask, render_template, request
from flask_restful import Api
from app.config import Config
from app.resources.endpoints import register_resources
import os
import logging


def create_app():
    # Specify static folder path explicitly
    app = Flask(
        __name__,
        static_folder='../static',  # Point to static folder at root level
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)

    # Disable werkzeug and other Flask loggers
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    # Create custom logger for application only
    app_logger = logging.getLogger('edc_app')
    app_logger.setLevel(logging.DEBUG)

    # Create file handler for application logs
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))

    app_logger.addHandler(file_handler)
    app_logger.propagate = False  # Prevent propagation to root logger

    # Store logger in app config for access in endpoints
    app.config['APP_LOGGER'] = app_logger

    # ADD THE CACHE CONTROL HEADERS HERE
    @app.after_request
    def add_cache_headers(response):
        # Only apply to API endpoints
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Initialize API
    api = Api(app)
    register_resources(api)

    # Homepage route
    @app.route('/')
    def homepage():
        return render_template('index.html')

    return app
