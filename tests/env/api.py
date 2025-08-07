from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data
data = [
    {'id': 262, 
    'owner': 'admin', 
    'source': 'The beam has reached a new destination.\n\n\n\nThe log creation has been triggered by the pv: SL-APP-MCS:BOM-CPU:BeamDestCode,             with value: 3.0\n\n [Context] \n\n\n\n The destination is (second autolog): \n\n- LBT.BB\n\n Log created automatically by the application AutOlog', 
    'description': 'The beam has reached a new destination.\nThe log creation has been triggered by the pv: SL-APP-MCS:BOM-CPU:BeamDestCode,             with value: 3.0\n[Context]\nThe destination is (second autolog):\n- LBT.BB\nLog created automatically by the application AutOlog', 
    'title': 'Destination Reached', 
    'level': 'info', 
    'state': 'Active', 
    'createdDate': 1749654340486, 
    'modifyDate': None, 
    'events': None, 
    'logbooks': [{'name': 'tests', 'owner': None, 'state': 'Active'}], 
    'tags': [], 
    'properties': [], 
    'attachments': []}

]

# Route to get all items
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(data)

# Route to get a single item by ID
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in data if item["id"] == item_id), None)
    if item:
        return jsonify(item)
    else:
        return jsonify({"error": "Item not found"}), 404

# Route to create a new item
@app.route('/items', methods=['POST'])
def create_item():
    new_item = request.json
    new_item["id"] = len(data) + 1
    data.append(new_item)
    return jsonify(new_item), 201

# Route to update an existing item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in data if item["id"] == item_id), None)
    if item:
        item.update(request.json)
        return jsonify(item)
    else:
        return jsonify({"error": "Item not found"}), 404

# Route to delete an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global data
    data = [item for item in data if item["id"] != item_id]
    return jsonify({"result": True})

if __name__ == '__main__':
    app.run(debug=True)