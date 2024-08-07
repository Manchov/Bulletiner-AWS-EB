from flask import render_template, jsonify
# from models import Bulletin
# from app import app

from flask import current_app as app

from web import service


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/bulletins')
def api_bulletins():
    # bulletins = Bulletin.query.all()
    bulletins = service.get_bulletins()
    # return jsonify([bulletin.to_dict() for bulletin in bulletins])
    return jsonify(bulletins)
