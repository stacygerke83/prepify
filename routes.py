# prepify/routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DataError
from .models import PantryItem
from . import db

pantry_bp = Blueprint('pantry', __name__)

# ---- Helpers ----

def _normalize_str(value, default=''):
    """Ensure we always store strings; convert numbers to str, trim whitespace."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        value = str(value)
    return str(value).strip()

def _serialize_item(item: PantryItem):
    return {
        'id': item.id,
        'name': item.name,
        'quantity': item.quantity,
        'category': item.category,
    }

# ---- Routes ----

@pantry_bp.route('/pantry', methods=['GET'])
def get_items():
    items = PantryItem.query.order_by(PantryItem.id.asc()).all()
    return jsonify([_serialize_item(i) for i in items]), 200


@pantry_bp.route('/pantry', methods=['POST'])
def add_item():
    if not request.is_json:
        return jsonify({'error': 'Request must be application/json'}), 415

    data = request.get_json()
    name = _normalize_str(data.get('name', '')).strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400

    quantity = _normalize_str(data.get('quantity', ''))
    category = _normalize_str(data.get('category', ''))

    item = PantryItem(name=name, quantity=quantity, category=category)

    try:
        db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Item added', 'item': _serialize_item(item)}), 201

    except (IntegrityError, DataError) as ie:
        db.session.rollback()
        return jsonify({'error': 'Invalid data or constraint violation', 'details': str(ie)}), 400
    except SQLAlchemyError as se:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(se)}), 500


@pantry_bp.route('/pantry/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = PantryItem.query.get_or_404(item_id)

    if not request.is_json:
        return jsonify({'error': 'Request must be application/json'}), 415

    data = request.get_json()

    # Update name if provided and non-empty
    if 'name' in data:
        new_name = _normalize_str(data.get('name', '')).strip()
        if not new_name:
            return jsonify({'error': 'name cannot be empty'}), 400
        item.name = new_name

    # Update quantity if provided
    if 'quantity' in data:
        item.quantity = _normalize_str(data.get('quantity', item.quantity))

    # Update category if provided
    if 'category' in data:
        item.category = _normalize_str(data.get('category', item.category))

    try:
        db.session.commit()
        return jsonify({'message': 'Item updated', 'item': _serialize_item(item)}), 200

    except (IntegrityError, DataError) as ie:
        db.session.rollback()
        return jsonify({'error': 'Invalid data or constraint violation', 'details': str(ie)}), 400
    except SQLAlchemyError as se:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(se)}), 500


@pantry_bp.route('/pantry/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = PantryItem.query.get_or_404(item_id)

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted', 'id': item_id}), 200

    except IntegrityError as ie:
        db.session.rollback()
        # Most common cause: another table references pantry_items.id
        return jsonify({
            'error': 'Cannot delete item due to related records (FK constraint)',
            'details': str(ie)
        }), 409

    except SQLAlchemyError as se:
        db.session.rollback()
        return jsonify({
            'error': 'Database error while deleting item',
            'details': str(se)
        }), 500
