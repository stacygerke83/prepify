from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Temporary in-memory pantry list
pantry = []

@app.route('/')
def home():
    return "Prepify API is running!", 200

# GET /pantry
@app.route('/pantry', methods=['GET'])
def get_pantry():
    return jsonify(pantry), 200

# POST /pantry
@app.route('/pantry', methods=['POST'])
def add_item():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    quantity = data.get('quantity')

    if not name:
        return jsonify({"error": "name is required"}), 400

    pantry.append({"name": name, "quantity": quantity})
    return jsonify({"name": name, "quantity": quantity}), 201

# PUT /pantry/<int:item_id>
@app.route('/pantry/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if item_id < 0 or item_id >= len(pantry):
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get('name')
    quantity = data.get('quantity')

    if not name:
        return jsonify({"error": "name is required"}), 400

    pantry[item_id] = {"name": name, "quantity": quantity}
    return jsonify(pantry[item_id]), 200

# DELETE /pantry/<int:item_id>
@app.route('/pantry/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if item_id < 0 or item_id >= len(pantry):
        return jsonify({"error": "Item not found"}), 404

    pantry.pop(item_id)
    return Response(status=204)

if __name__ == '__main__':
    app.run(debug=True)
