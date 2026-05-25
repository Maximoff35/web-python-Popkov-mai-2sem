from flask import Flask, jsonify, request
from flask_cors import CORS
from ugc_service.extensions import db
from ugc_service.config import Config
from ugc_service.errors import UgcException, error_response
from ugc_service.schemas import (
    validate_review_create_data,
    validate_product_id_query,
    validate_review_status_data,
)
from ugc_service.services import create_review, get_reviews, update_review_status, get_user_from_django_token


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)
    CORS(app)

    db.init_app(app)

    @app.errorhandler(UgcException)
    def handle_ugc_exception(error):
        return error_response(error)

    @app.post('/api/ugc/reviews/')
    def create_review_view():
        raw_data = validate_review_create_data(request.get_json(silent=True))
        user = get_user_from_django_token(request.headers.get('Authorization'))
        review = create_review(raw_data, user=user)
        return jsonify(review.to_dict()), 201

    @app.get('/api/ugc/reviews/')
    def list_reviews_view():
        product_id = validate_product_id_query(request.args.get('product_id'))
        reviews = get_reviews(product_id=product_id)
        return jsonify({
            'count': len(reviews),
            'results': [review.to_dict() for review in reviews],
        })

    @app.patch('/api/ugc/reviews/<int:review_id>/status/')
    def update_review_status_view(review_id):
        data = validate_review_status_data(request.get_json(silent=True))
        review = update_review_status(
            review_id=review_id,
            status=data['status'],
        )
        return jsonify(review.to_dict())

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