# database/models.py

from database import db

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Text, TIMESTAMP, Float,
    ForeignKeyConstraint, PrimaryKeyConstraint, ForeignKey, DateTime, Time
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BulletinBatch(db.Model):
    __tablename__ = 'bulletin_batches'

    batch_id = Column(Integer, primary_key=True)
    scraped = Column(Boolean, nullable=False)
    scrapable = Column(Boolean, nullable=False)
    date = Column(Date)
    date_scraped = Column(TIMESTAMP)
    bulletin_count = Column(Integer)   # Number of raw bulletins for this batch, if you choose to store it
    note = Column(Text)


class BulletinRaw(db.Model):
    __tablename__ = 'bulletins_raw'

    # Composite PK referencing BulletinBatch
    batch_id = Column(Integer, ForeignKey('bulletin_batches.batch_id'), primary_key=True)
    bulletin_number = Column(Integer, primary_key=True)

    date = Column(Date)
    description = Column(Text)
    processed = Column(Boolean, default=False)

    # Relationship back to BulletinBatch
    batch = relationship("BulletinBatch", backref="raw_bulletins")



class BulletinProcessed(db.Model):
    """
    Represents the AI-processed (classified, geocoded, etc.) version of a raw bulletin.
    References (batch_id, bulletin_number) from bulletins_raw.
    """
    __tablename__ = 'bulletins_processed'

    batch_id = Column(Integer, primary_key=True)
    bulletin_number = Column(Integer, primary_key=True)

    # We'll define a ForeignKeyConstraint for the composite
    __table_args__ = (
        ForeignKeyConstraint(
            ['batch_id', 'bulletin_number'],
            ['bulletins_raw.batch_id', 'bulletins_raw.bulletin_number']
        ),
        PrimaryKeyConstraint('batch_id', 'bulletin_number'),
    )

    # Basic fields
    date = Column(Date)               # Possibly refined or same as raw
    description = Column(Text)        # Possibly cleaned/shortened
    category = Column(String)
    sub_category = Column(String)

    # Where it was reported (e.g., Police station location)
    location_report = Column(String)  # e.g., "Downtown Police Precinct"
    lat_report = Column(Float)
    lon_report = Column(Float)

    # Where the incident actually happened
    location_event = Column(String)  # textual description, e.g., "Main St near Post Office"
    lat_event = Column(Float)
    lon_event = Column(Float)



    # Time fields
    event_time = Column(DateTime)            # When the event happened, if AI determines date+time
    # or if you only want time-of-day, do: event_time = Column(Time)

    # AI classification info
    processed_timestamp = Column(DateTime)   # When classification was done
    processor_version = Column(String)       # e.g., "v2.1.0"
    notes = Column(Text)                     # Additional unstructured data/remarks

    # Relationship back to the raw bulletin
    raw_bulletin = relationship(
        "BulletinRaw",
        backref="processed_bulletin",
        uselist=False  # assuming 1-to-1
    )
