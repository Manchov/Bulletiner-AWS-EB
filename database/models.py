# database/models.py

from database import db

class BulletinBatch(db.Model):
    __tablename__ = 'bulletin_batches'

    batch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.Integer, nullable=False, unique=True)
    scraped = db.Column(db.Boolean, nullable=False)
    scrapable = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.Date)
    date_scraped = db.Column(db.TIMESTAMP)
    bulletin_count = db.Column(db.Integer)

    # Relationships
    bulletins_raw = db.relationship('BulletinRaw', backref='batch', lazy=True)
    bulletins_processed = db.relationship('BulletinProcessed', backref='batch', lazy=True)

class BulletinRaw(db.Model):
    __tablename__ = 'bulletins_raw'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('bulletin_batches.batch_id'), nullable=False)
    bulletin_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    processed = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('batch_id', 'bulletin_number', name='uq_bulletin_raw'),
    )

class BulletinProcessed(db.Model):
    __tablename__ = 'bulletins_processed'

    batch_id = db.Column(db.Integer, db.ForeignKey('bulletin_batches.batch_id'), nullable=False)
    bulletin_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    location = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    category = db.Column(db.String)

    __table_args__ = (
        db.PrimaryKeyConstraint('batch_id', 'bulletin_number'),
    )
