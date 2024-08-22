import os
from flask import Flask,session


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # db.init_app(app)

    with app.app_context():
        # Import parts of our application
        # from . import routes  # This should ensure routes are registered
        import routes

        # Print registered routes for debugging
        print(app.url_map)

        # Create database tables for our data models
        # db.create_all()


    return app


basedir = os.path.abspath(os.path.dirname(__file__))

application = create_app()
app = application

app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True)
