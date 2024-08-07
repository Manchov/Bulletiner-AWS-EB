from flask import Flask


def create_app():
    app = Flask(__name__)
    # app.config.from_object('config.Config')

    # db.init_app(app)

    # with app.app_context():
    #     # Import parts of our application
    #     # from . import routes  # This should ensure routes are registered
    #     # import routes
    #
    #     # Print registered routes for debugging
    #     # print(app.url_map)
    #
    #     # Create database tables for our data models
    #     # db.create_all()

    return app


application = create_app()

app = application


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
