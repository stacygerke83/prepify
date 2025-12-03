from flask import Blueprint, request, jsonify
from .models import PantryItem
from . import db

pantry_bp = Blueprint('pantry', __name__)

@pantry_bp.route('/pantry', methods=['GET'])
def get_items():
    items = PantryItem.query.all()
    return jsonify([{'id': i.id, 'name': i.name, 'quantity': i.quantity} for i in items])

@pantry_bp.route('/pantry', methods=['POST'])
def add_item():
    data = request.get_json(force=True)
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400
    item = PantryItem(name=name, quantity=data.get('quantity', ''))
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Item added'}), 201

@pantry_bp.route('/pantry/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = PantryItem.query.get_or_404(item_id)
    data = request.get_json(force=True)
    item.name = data.get('name', item.name)
    item.quantity = data.get('quantity', item.quantity)
    db.session.commit()
    return jsonify({'message': 'Item updated'})

@pantry_bp.route('/pantry/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = PantryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})
