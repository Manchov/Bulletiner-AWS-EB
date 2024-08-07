from database import service_db


def get_bulletins():
    bulletins = service_db.get_database("SELECT date, description, location, latitude, longitude, category FROM bulletins")

    # Convert the result to a list of dictionaries
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
