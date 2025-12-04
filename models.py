# prepify/models.py
from . import db

class PantryItem(db.Model):
    __tablename__ = 'pantry_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    # Keeping quantity as String to avoid migration for now.
    # If you want numeric later, change to Integer + a migration.
    quantity = db.Column(db.String(50), nullable=True, default='')
    category = db.Column(db.String(50), nullable=True, default='')

    def __repr__(self) -> str:
        return f"<PantryItem id={self.id} name={self.name!r}>"
