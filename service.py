from database import service_db

from datetime import datetime

def get_bulletins(search_string=None, start_date=None, end_date=None):

    bulletins_list = []
    search_string_lower = search_string.lower() if search_string else None

    for bulletin in bulletins:
        bulletin_date_str = bulletin['date']

        # Check if the date is None or null
        if bulletin_date_str is None:
            continue  # Skip records with no date

        # Convert the date string from 'YYYY-MM-DD' to a datetime object
        try:
            bulletin_date = datetime.strptime(bulletin_date_str, '%Y-%m-%d')
        except ValueError:
            continue  # Skip records with invalid date format

        # Perform date filtering in Python
        if start_date and end_date:
            if not (start_date <= bulletin_date <= end_date):
                continue

        # Perform case-insensitive filtering in Python for the search string
        if search_string_lower and search_string_lower not in bulletin['description'].lower():
            continue

        bulletins_list.append(bulletin)

    return bulletins_list


def load_full_bulletins_from_db():
    query = "SELECT date, description, location, latitude, longitude, category FROM bulletins"
    bulletins = service_db.get_database(query)

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


bulletins = load_full_bulletins_from_db()