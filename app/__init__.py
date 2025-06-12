from flask import Flask, render_template, request, redirect, url_for, session
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from app.config import Config
from app.resources.endpoints import register_resources
from logging.handlers import RotatingFileHandler
import os
import logging
import secrets


def create_app():
    app = Flask(
        __name__,
        static_folder='../static',
        static_url_path='/static'
    )

    # Secure configuration
    app.config.from_object(Config)
    app.config.update(
        SECRET_KEY=secrets.token_hex(32),
        WTF_CSRF_SECRET_KEY=secrets.token_hex(32),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        WTF_CSRF_TIME_LIMIT=None
    )

    # Create required directories
    for folder in [app.config['UPLOAD_FOLDER'], app.config['RESULT_FOLDER'], app.config['LOG_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Logging configuration
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app_logger = logging.getLogger('edc_app')
    app_logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))

    app_logger.addHandler(file_handler)
    app_logger.propagate = False
    app.config['APP_LOGGER'] = app_logger

    # Cache control headers
    @app.after_request
    def add_cache_headers(response):
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Initialize security headers and CSRF protection
    Talisman(app, content_security_policy=None)
    csrf = CSRFProtect(app)

    # Initialize API
    api = Api(app)
    register_resources(api)

    # Login form using Flask-WTF
    from flask_wtf import FlaskForm
    from wtforms import StringField, PasswordField, SubmitField
    from wtforms.validators import DataRequired

    class LoginForm(FlaskForm):
        username = StringField('Usuario', validators=[DataRequired()])
        password = PasswordField('Contraseña', validators=[DataRequired()])
        submit = SubmitField('Entrar')

    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            if form.username.data == 'demo' and form.password.data == 'UPCXelsDEMO':
                session['logged_in'] = True
                return redirect(url_for('homepage'))
            else:
                form.username.errors.append('Usuario o contraseña incorrectos.')
        return render_template('login.html', form=form)

    @app.route('/')
    def homepage():
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return render_template('index.html')

    return app
