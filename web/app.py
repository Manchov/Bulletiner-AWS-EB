import os
from flask import Flask, render_template, jsonify
from database import service_db
# from web import create_app
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

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


# db = SQLAlchemy()
# app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object('config.Config')
#
#     db.init_app(app)
#
#     with app.app_context():
#         from . import routes, models
#         db.create_all()
#
#     return app

app = create_app()
#
# def get_bulletins():
#     bulletins = service_db.get_database("SELECT date, description, location, latitude, longitude FROM bulletins")
#
#     # Convert the result to a list of dictionaries
#     bulletins_list = []
#     for row in bulletins:
#         bulletins_list.append({
#             'date': row[0],
#             'description': row[1],
#             'location': row[2],
#             'latitude': row[3],
#             'longitude': row[4]
#         })
#
#     return bulletins_list

#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/api/bulletins')
# def api_bulletins():
#     bulletins = get_bulletins()
#     return jsonify(bulletins)


if __name__ == '__main__':
    app.run(debug=True)
