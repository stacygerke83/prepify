from flask import Blueprint, request, jsonify
from services.pantry_service import (
    list_items, create_item, update_item, delete_item
)

bp = Blueprint('pantry', __name__, url_prefix='/pantry')

@bp.get('/')
def get_items():
    return jsonify(list_items()), 200

@bp.post('/')
def post_item():
    data = request.get_json(force=True)
    item, error = create_item(data)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(item), 201

@bp.put('/<int:item_id>')
def put_item(item_id):
    data = request.get_json(force=True)
    item, error = update_item(item_id, data)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(item), 200

@bp.delete('/<int:item_id>')
def del_item(item_id):
    ok, error = delete_item(item_id)
    if not ok:
        return jsonify({'error': error}), 404
