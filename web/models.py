# from web import db
# import app
#
#
# class Bulletin(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(10))
#     description = db.Column(db.Text)
#     location = db.Column(db.String(100))
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)
#
#     def to_dict(self):
#         return {
#             'date': self.date,
#             'description': self.description,
#             'location': self.location,
#             'latitude': self.latitude,
#             'longitude': self.longitude,
#         }
