from flask import Flask, jsonify
from ugc_service.extensions import db
from ugc_service.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from ugc_service.models import Review
        db.create_all()

    @app.get('/api/ugc/health/')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'ugc'})

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)