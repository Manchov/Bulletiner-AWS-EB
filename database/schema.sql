CREATE TABLE IF NOT EXISTS bulletins_scraped
(
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id          INTEGER NOT NULL,
    scraped          BOOLEAN NOT NULL,
    scrapable        BOOLEAN NOT NULL,
    date             TEXT,
    date_scraped     TEXT,
    number_bulletins INTEGER
);

CREATE TABLE IF NOT EXISTS bulletins_raw
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     INTEGER NOT NULL,
    post_number INTEGER NOT NULL,
    date        TEXT,
    description TEXT,
    processed   BOOLEAN,
    FOREIGN KEY (post_id) REFERENCES bulletins_scraped (post_id)
);

CREATE TABLE IF NOT EXISTS bulletins
(
    post_id     INTEGER NOT NULL,
    post_number INTEGER NOT NULL,
    date        TEXT,
    description TEXT,
    location    TEXT,
    latitude    REAL,
    longitude   REAL,
    category    TEXT,
    PRIMARY KEY (post_id, post_number),
    FOREIGN KEY (post_id) REFERENCES bulletins_scraped (post_id)
);
