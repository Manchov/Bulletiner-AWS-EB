-- schema_postgresql.sql

CREATE TABLE IF NOT EXISTS bulletin_batches (
    batch_id SERIAL PRIMARY KEY,
    page_id INTEGER NOT NULL UNIQUE,
    scraped BOOLEAN NOT NULL,
    scrapable BOOLEAN NOT NULL,
    date DATE,
    date_scraped TIMESTAMP,
    bulletin_count INTEGER
);

CREATE TABLE IF NOT EXISTS bulletins_raw (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    bulletin_number INTEGER NOT NULL,
    date DATE,
    description TEXT,
    processed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (batch_id) REFERENCES bulletin_batches (batch_id)
);

CREATE TABLE IF NOT EXISTS bulletins_processed (
    batch_id INTEGER NOT NULL,
    bulletin_number INTEGER NOT NULL,
    date DATE,
    description TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    category TEXT,
    PRIMARY KEY (batch_id, bulletin_number),
    FOREIGN KEY (batch_id) REFERENCES bulletin_batches (batch_id)
);
