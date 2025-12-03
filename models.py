from . import db

class PantryItem(db.Model):
    __tablename__ = 'pantry_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    quantity = db.Column(db.String(50))
    category = db.Column(db.String(50))
