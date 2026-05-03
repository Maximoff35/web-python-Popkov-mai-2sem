from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from ugc_service.config import Config


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.get('/api/ugc/health/')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'ugc'})

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)