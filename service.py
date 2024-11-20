from datetime import datetime

from database import service_db
from database.models import BulletinProcessed

def get_bulletins(search_string=None, start_date=None, end_date=None):
    query = BulletinProcessed.query

    if start_date and end_date:
        query = query.filter(BulletinProcessed.date.between(start_date, end_date))

    if search_string:
        query = query.filter(BulletinProcessed.description.ilike(f'%{search_string}%'))

    bulletins = query.all()

    bulletins_list = []
    for bulletin in bulletins:
        bulletins_list.append({
            'date': bulletin.date.strftime('%Y-%m-%d') if bulletin.date else None,
            'description': bulletin.description,
            'location': bulletin.location,
            'latitude': bulletin.latitude,
            'longitude': bulletin.longitude,
            'category': bulletin.category
        })

    return bulletins_list

def load_full_bulletins_from_db():
    query = "SELECT date, description, location, latitude, longitude, category FROM bulletins"
    # bulletins = service_db.get_database(query)
    bulletins = query = BulletinProcessed.query

    bulletins_list = []
    for row in bulletins:
        bulletins_list.append({
            'date': row[0],
            'description': row[1],
            'location': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'category': row[5]
        })

    return bulletins_list


# bulletins = load_full_bulletins_from_db()
