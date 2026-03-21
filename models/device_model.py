from connection import db

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    average_watts = db.Column(db.Integer, nullable=False)
    standby_watts = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories_elettrodomestico.id"), nullable=False)