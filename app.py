import os
from flask import Flask, session
from config import Config

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        # Import parts of our application
        # This should ensure routes are registered
        import routes

        # Print registered routes for debugging
        print(app.url_map)

    return app


basedir = os.path.abspath(os.path.dirname(__file__))

# EB [must] search for "application" variable in app.py therefore app = application
application = create_app(Config)
app = application

# Future use for sessions
app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=False)
