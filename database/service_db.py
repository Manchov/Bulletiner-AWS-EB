import sqlite3


# def connect_database():
#     return sqlite3.connect('bulletins.db')

def get_database(query):
    # Connect to the SQLite database
    conn = sqlite3.connect('database/bulletins.db')
    cursor = conn.cursor()

    # Query the bulletins table
    cursor.execute(query)  # "SELECT date, description, location, latitude, longitude FROM bulletins"
    data = cursor.fetchall()

    conn.close()
    return data


def log_bulletin_db(data):
    # Connect to the SQLite database
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO bulletins_scraped (id,post_id,scraped,scrapable,date,date_scraped) VALUES (?,?,?,?,? ?)",
        (data['id'], data['post_id'], data['date'], data['scraped'], data['scrapable'], data['date'],
         data['date_scraped']))

    return "."


def insert_into_db(events, train=False):
    # Connect to the SQLite database
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()

    # Insert each event into the bulletins table
    if not train:
        for event in events:
            cursor.execute("INSERT INTO bulletins_raw (post_id, date, description) VALUES (?,?, ?)",
                           (event['post_id'], event['date'], event['description']))
    elif train:
        for event in events:
            cursor.execute(
                "INSERT INTO bulletins (post_id, date, description, location, latitude,longitude) VALUES (?,?, ?,?,?,?)",
                (event['post_id'], event['date'], event['description'], event['location'], event['latitude'],
                 event['longitude']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def log_into_db(post_id, scraped, scrapable, date, date_scraped, number_bulletins):
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO bulletins_scraped (post_id,scraped,scrapable,date,date_scraped,number_bulletins) VALUES (?,?,?,?,?,?)",
        (post_id, scraped, scrapable, date, date_scraped, number_bulletins))

    conn.commit()
    conn.close()


def save_raw(data):
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()

    for dat in data:
        cursor.execute(
            "INSERT INTO bulletins_raw (post_id,post_number, date, description, processed) VALUES (?,?,?,?,?)",
            (dat['post_id'], dat['post_number'], dat['date'], dat['description'], False))

    conn.commit()
    conn.close()


def get_scraped_ids():
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()
    cursor.execute("SELECT post_id FROM bulletins_scraped ORDER BY post_id")
    data = cursor.fetchall()

    conn.close()
    return data


import sqlite3


# Function to fetch unprocessed bulletins from bulletins_raw
def fetch_unprocessed_bulletins():
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, post_id, post_number, date, description FROM bulletins_raw WHERE processed = 0")
    bulletins = cursor.fetchall()
    conn.close()
    return bulletins


# Function to update the processed status of a bulletin in bulletins_raw
def update_bulletin_processed_status(bulletin_id):
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE bulletins_raw SET processed = 1 WHERE id = ?", (bulletin_id,))
    conn.commit()
    conn.close()


# Function to insert classified bulletins into the bulletins table
def insert_classified_bulletin(post_id, post_number, date, description, latitude, longitude, location, category):
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bulletins (post_id, post_number, date, description,latitude,longitude, location, category) VALUES (?, ?, ?, ?,?,?, ?, ?)",
        (post_id, post_number, date, description, latitude, longitude, location, category)
    )
    conn.commit()
    conn.close()
