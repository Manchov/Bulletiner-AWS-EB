import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # print(f"config loaded : {os.environ.get('DATABASE_URL')} :: {os.environ}")
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    TESTING = True

try:
    from config_local import Config as LocalConfig
    Config = LocalConfig
except ImportError:
    pass
