from flask import Flask

application = Flask(__name__)


@application.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    application.run()
