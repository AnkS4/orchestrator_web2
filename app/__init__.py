from flask import Flask, render_template
from flask_restful import Api
from app.config import Config
from app.resources.endpoints import register_resources
import os
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)

    # Setup logging
    logging.basicConfig(
        filename=app.config['LOG_FILE'],
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

    # Initialize API
    api = Api(app)
    register_resources(api)

    # Homepage route
    @app.route('/')
    def homepage():
        return render_template('index.html')

    return app
