from flask import Flask, jsonify, request

app = Flask(__name__)

# Temporary in-memory storage for pantry items
pantry = []

# GET /pantry - Fetch all items
@app.route('/pantry', methods=['GET'])
def get_pantry():
    return jsonify(pantry), 200

# POST /pantry - Add item
@app.route('/pantry', methods=['POST'])
def add_item():
    data = request.get_json()
    pantry.append(data)
    return jsonify(data), 201

# PUT /pantry/<int:item_id> - Edit item
@app.route('/pantry/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if item_id < 0 or item_id >= len(pantry):
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json()
    pantry[item_id] = data
    return jsonify(data), 200

# DELETE /pantry/<int:item_id> - Remove item
@app.route('/pantry/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if item_id < 0 or item_id >= len(pantry):
        return jsonify({"error": "Item not found"}), 404
    pantry.pop(item_id)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
