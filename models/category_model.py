from connection import db

class Category(db.Model):
    __tablename__ = "categories_elettrodomestico"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    devices = db.relationship("Device", backref="category", lazy=True)