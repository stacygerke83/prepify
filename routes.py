from flask import Blueprint, request, jsonify
from .models import PantryItem
from . import db

pantry_bp = Blueprint('pantry', __name__)

@pantry_bp.route('/pantry', methods=['GET'])
def get_items():
    items = PantryItem.query.order_by(PantryItem.name).all()
    return jsonify([{
        'id': i.id,
        'name': i.name,
        'quantity': i.quantity,
        'category': i.category
    } for i in items])

@pantry_bp.route('/pantry', methods=['POST'])
def add_item():
    data = request.get_json(force=True)
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    existing = PantryItem.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'item already exists'}), 409
    item = PantryItem(
        name=name,
        quantity=data.get('quantity', ''),
        category=data.get('category', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Item added', 'id': item.id}), 201

@pantry_bp.route('/pantry/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = PantryItem.query.get_or_404(item_id)
    data = request.get_json(force=True)
    if 'name' in data:
        item.name = data['name']
    if 'quantity' in data:
        item.quantity = data['quantity']
    if 'category' in data:
        item.category = data['category']
    db.session.commit()
    return jsonify({'message': 'Item updated'})

@pantry_bp.route('/pantry/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = PantryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})
