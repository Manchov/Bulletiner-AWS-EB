import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    TESTING = False
    # DATABASE_URI = 'sqlite:///bulletins.db'


class TestConfig(Config):
    TESTING = True
    # DATABASE_URI = 'sqlite:///database/bulletins.db'  # Use an in-memory database for testing


print("config opened and is empty, init for future uses")
