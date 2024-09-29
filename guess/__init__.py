from flask import Flask, jsonify, request, current_app
from flask_cors import CORS
from  repository import dynamodb, hash, sqlite
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import os
import pathlib


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_prefixed_env()
    
    CORS(app) 
    
    app.config.update(config or {})

    FlaskInstrumentor().instrument_app(app)
     
    if app.config.get('TESTING'):
        app.db = hash.HashRepository()
    else:
        match app.config.get('DB_TYPE', 'dynamodb'):
            case 'sqlite':
                path="{}/db/database.db".format(pathlib.Path(__file__).parent.parent.absolute())
                app.db = sqlite.SQLiteRepository(app.config.get( 'DB_PATH',path ))
            case 'dynamodb':
                app.db = dynamodb.DynamoDBRepository('GameTable')

    from .game_routes import game_bp  # Assuming your blueprint is named `game_bp`
    app.register_blueprint(game_bp)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    return app