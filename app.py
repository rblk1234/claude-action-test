import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = load_users()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({'error': 'Missing fields'}), 400
    user = {'name': name, 'email': email}
    save_user(user)
    return jsonify(user), 201

def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

def save_user(user):
    users = load_users()
    users.append(user)
    with open('users.json', 'w') as f:
        json.dump(users, f)

if __name__ == '__main__':
    app.run(debug=True)
