from functools import wraps
from flask import request, jsonify
import hashlib

API_KEYS = {}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in API_KEYS:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
# v3
