from flask import Flask, jsonify, request
from ugc_service.extensions import db
from ugc_service.config import Config
from ugc_service.errors import UgcException, error_response
from ugc_service.schemas import validate_review_create_data
from ugc_service.services import create_review


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.errorhandler(UgcException)
    def handle_ugc_exception(error):
        return error_response(error)

    @app.post('/api/ugc/reviews/')
    def create_review_view():
        raw_data = validate_review_create_data(request.get_json(silent=True))
        review = create_review(raw_data)
        return jsonify(review.to_dict()), 201

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