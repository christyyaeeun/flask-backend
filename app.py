from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://aquamarine-capybara-eac2c1.netlify.app/"}})
# Serve the React build files from the 'client' directory
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')

def serve_react(path):
    if path != "" and os.path.exists(f"client/{path}"):
        return send_from_directory('client', path)
    else:
        return send_from_directory('client', 'index.html')
CORS(app)

GUEST_LIST_FILE = 'data/guestList.json'

def load_guest_list():
    with open(GUEST_LIST_FILE, 'r') as file:
        return json.load(file)

def update_guest_list(guests):
    with open(GUEST_LIST_FILE, 'w') as file:
        json.dump(guests, file, indent=2)

@app.route('/api/guestList', methods=['GET'])
def get_guest_list():
    try:
        guests = load_guest_list()
        return jsonify(guests)
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/updateGuest', methods=['POST'])
def update_guest():
    try:
        new_data = request.json
        guests = load_guest_list()

        for guest in guests:
            if guest['firstName'] == new_data['firstName'] and guest['lastName'] == new_data['lastName']:
                if new_data.get('role') and new_data['role'] == 'admin':
                    guest.update(new_data)
                    update_guest_list(guests)
                    return jsonify({'message': 'Guest updated successfully'})
                else:
                    return jsonify({'error': 'Insufficient permissions'})

        return jsonify({'error': 'Guest not found'})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/addGuest', methods=['POST'])
def add_guest():
    try:
        new_guest = request.json
        if new_guest.get('role') and new_guest['role'] == 'admin':
            guests = load_guest_list()
            guests.append(new_guest)
            update_guest_list(guests)
            return jsonify({'message': 'Guest added successfully'})
        else:
            return jsonify({'error': 'Insufficient permissions'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)