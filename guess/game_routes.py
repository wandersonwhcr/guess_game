from flask import Blueprint, jsonify, request, current_app
import hashlib
import random
import string

game_bp = Blueprint('game_bp', __name__)

def generate_salt(length=4):
    """Generate a random alphanumeric salt."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hash_password(password, salt):
    """Hash a password with the given salt."""
    hasher = hashlib.sha256()
    hasher.update(f"{salt}{password}".encode('utf-8'))
    return hasher.hexdigest()

@game_bp.route('/create', methods=['POST'])
def create_game():
    password = request.json['password']
    salt = generate_salt()
    hashed_password = hash_password(password, salt)
    game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    data = {'password': f"{hashed_password}:{salt}", 'attempts': []}
    current_app.db.store(game_id, data)
    return jsonify({'game_id': game_id})

@game_bp.route('/guess/<game_id>', methods=['POST'])
def guess(game_id):
    try:
        data = current_app.db.retrieve(game_id)
        myguess = request.json['guess']
        hashed_password, salt = data['password'].split(':')
        hashed_guess = hash_password(myguess, salt)
        if hashed_guess == hashed_password:
            result = "Correct"
        else:
            result = "Incorrect"
        return jsonify({'result': result})
    except KeyError:
        current_app.logger.error(f"Game {game_id} not found")
        return jsonify({'error': 'Game not found'}), 404
