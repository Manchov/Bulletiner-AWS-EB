from flask import render_template, jsonify, request
from flask import current_app as app
from datetime import datetime

from service import get_bulletins


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/bulletins')
def api_bulletins():
    search_string = request.args.get('search', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    bulletins = get_bulletins(search_string, start_date, end_date)

    return jsonify(bulletins)
