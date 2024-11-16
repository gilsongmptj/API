from flask import Flask, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import os
from itsdangerous import URLSafeTimedSerializer
from cachelib.simple import SimpleCache
import functools

# Ideally, store SECRET_KEY in a secure environment variable
SECRET_KEY = 'sgs18ssd38g'
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Create cache instance
cache = SimpleCache()
app = Flask(__name__)

def generate_token(data, expiration=300):
    token = serializer.dumps(data)
    cache.set(token, data, timeout=expiration)
    return token

def validate_token(token):
    data = cache.get(token)
    if data is not None:
        return data
    return None  

def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'error': 'token is missing'}), 401
        data = validate_token(token)
        if not data:
            return jsonify({'error': 'token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/token', methods=['POST'])
def token():
    data = request.json
    token = generate_token(data)
    return jsonify({'token': token}), 200

@app.route('/upload', methods=['POST'])
@token_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400

    f = request.files['file']

    if f.filename == '':
        return jsonify({'error': 'no file selected'}), 400

    if f.filename.endswith(".csv"):
        try:
            filename = secure_filename(f.filename)
            f.save(filename)
            df = pd.read_csv(filename)
            json_filename = filename.replace(".csv", ".json")
            df.to_json(json_filename, orient='records')
            return jsonify(df.head().to_dict(orient='records')), 202
        except Exception as e:  
            return jsonify({'error': f'File operation failed: {str(e)}'}), 500

    else:
        return jsonify({'error': 'file is not CSV'}), 400

if __name__ == '__main__':
    app.run(debug=True)