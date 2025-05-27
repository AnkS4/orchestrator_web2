import os

class Config:
    SECRET_KEY = 'dev-secret-key'
    UPLOAD_FOLDER = 'data/uploads'
    RESULT_FOLDER = 'data/results'
    LOG_FOLDER = 'data/logs'
    LOG_FILE = 'data/logs/log.txt'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
