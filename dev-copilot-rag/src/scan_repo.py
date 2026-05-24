import os
from typing import List, Dict

# Ignore directories commonly found in developer projects
IGNORE_DIRS = {
    'node_modules', '.git', '.github', 'venv', '.venv', '__pycache__', 
    '.gemini', 'dist', 'build', '.idea', '.vscode'
}

# Accepted extensions
ACCEPTED_EXTENSIONS = {'.py', '.js', '.ts', '.md', '.json', '.html', '.css'}

def scan_local_directory(dir_path: str) -> List[Dict[str, str]]:
    """
    Recursively scans the target directory and returns file contents with relative paths.
    """
    files_data = []
    
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        return get_mock_repository()
        
    for root, dirs, files in os.walk(dir_path):
        # In-place modify dirs to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ACCEPTED_EXTENSIONS:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    rel_path = os.path.relpath(full_path, dir_path).replace("\\", "/")
                    files_data.append({
                        "path": rel_path,
                        "content": content
                    })
                except Exception:
                    # Ignore unreadable files (binary or encoding issues)
                    pass
                    
    # If no files found, return mock repository
    if not files_data:
        return get_mock_repository()
        
    return files_data

def get_mock_repository() -> List[Dict[str, str]]:
    """Returns a mock repository file layout for offline/simulation runs."""
    return [
        {
            "path": "auth/service.py",
            "content": """import jwt
import datetime
from database.connection import get_db_session

def generate_auth_token(user_id, secret_key):
    \"\"\"
    Generates a secure JWT authentication token for a user.
    Expires in 2 hours.
    \"\"\"
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_session_token(token, secret_key):
    \"\"\"
    Decodes and verifies a JWT token. Returns user_id if valid, else raises ValueError.
    \"\"\"
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise ValueError("Auth token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid authentication token.")
"""
        },
        {
            "path": "database/connection.py",
            "content": """import sqlite3
import os

DB_FILE = os.getenv("DATABASE_FILE", "app.db")

def get_db_session():
    \"\"\"
    Establishes a connection to the SQL database.
    Yields a cursor connection, committing on exit.
    \"\"\"
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
"""
        },
        {
            "path": "api/routes.py",
            "content": """from flask import Flask, request, jsonify
from auth.service import generate_auth_token, verify_session_token

app = Flask(__name__)
SECRET_KEY = "super-secret-dev-key"

@app.route("/login", methods=["POST"])
def login_route():
    \"\"\"
    Authentication Route. Requires user_id in JSON body.
    \"\"\"
    data = request.json
    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id parameter"}), 400
        
    token = generate_auth_token(data["user_id"], SECRET_KEY)
    return jsonify({"token": token, "status": "authenticated"})

@app.route("/secure-data", methods=["GET"])
def secure_data_route():
    \"\"\"
    Protected API Endpoint. Requires Bearer Token in authorization header.
    \"\"\"
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or malformed Authorization header"}), 401
        
    token = auth_header.split(" ")[1]
    try:
        user_id = verify_session_token(token, SECRET_KEY)
        return jsonify({"message": f"Welcome User {user_id}", "restricted_data": [102, 104, 201]})
    except ValueError as e:
        return jsonify({"error": str(e)}), 403
"""
        },
        {
            "path": "README.md",
            "content": "# Dev Core API Service\n\nThis codebase handles user session management, authentication token processing (using PyJWT), and SQLite database connection wrappers."
        }
    ]
