import sqlite3


def setup_database():
    conn = sqlite3.connect('../database/bulletins.db')
    cursor = conn.cursor()

    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
