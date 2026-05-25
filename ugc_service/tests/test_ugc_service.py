import pytest
from ugc_service.app import create_app
from ugc_service.extensions import db
from ugc_service.models import Review
from ugc_service.errors import ProductNotFound, DjangoServiceUnavailable


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_product_exists(monkeypatch):
    def fake_check_product_exists(product_id: int):
        return None
    monkeypatch.setattr(
        'ugc_service.services.check_product_exists',
        fake_check_product_exists
    )

@pytest.fixture
def mock_product_not_found(monkeypatch):
    def fake_check_product_exists(product_id: int):
        raise ProductNotFound(details={'product_id': product_id})

    monkeypatch.setattr(
        'ugc_service.services.check_product_exists',
        fake_check_product_exists
    )

@pytest.fixture
def mock_django_unavailable(monkeypatch):
    def fake_check_product_exists(product_id: int):
        raise DjangoServiceUnavailable()

    monkeypatch.setattr(
        'ugc_service.services.check_product_exists',
        fake_check_product_exists
    )

@pytest.fixture
def mock_user_from_django_token(monkeypatch):
    def fake_get_user_from_django_token(auth_header: str | None):
        return {
            'id': 1,
            'username': 'maxim',
            'email': 'max@test.ru',
        }
    monkeypatch.setattr(
        'ugc_service.app.get_user_from_django_token',
        fake_get_user_from_django_token,
    )

def test_create_review_success(client, mock_product_exists, mock_user_from_django_token):
    response = client.post('/api/ugc/reviews/', json={
        'product_id': 1,
        'text': 'Хороший продукт бла бла бла.',
        'rating': 5,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['product_id'] == 1
    assert data['user_name'] == 'maxim'
    assert data['rating'] == 5
    assert data['text'] == 'Хороший продукт бла бла бла.'
    assert data['status'] == Review.STATUS_PENDING

def test_create_review_not_json(client):
    response = client.post('/api/ugc/reviews/', data='not json', content_type='text/plain')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert 'body' in data['details']

def test_create_review_product_not_found(client, mock_product_not_found, mock_user_from_django_token):
    response = client.post('/api/ugc/reviews/', json={
        'product_id': 999,
        'text': 'Хороший продукт бла бла бла.',
        'rating': 5,
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['error_code'] == 'PRODUCT_NOT_FOUND'

def test_create_review_invalid_rating(client):
    response = client.post('/api/ugc/reviews/', json={
        'product_id': 1,
        'user_name': 'maxim',
        'text': 'Хороший продукт бла бла бла.',
        'rating': 10,
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert 'rating' in data['details']

def test_create_review_empty_text(client):
    response = client.post('/api/ugc/reviews/', json={
        'product_id': 1,
        'user_name': 'maxim',
        'text': '',
        'rating': 5,
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert 'text' in data['details']

def test_create_review_django_unavailable(client, mock_django_unavailable):
    response = client.post('/api/ugc/reviews/', json={
        'product_id': 1,
        'user_name': 'maxim',
        'text': 'Хороший продукт бла бла бла.',
        'rating': 5,
    })
    assert response.status_code == 503
    data = response.get_json()
    assert data['error_code'] == 'DJANGO_SERVICE_UNAVAILABLE'

def test_list_reviews_returns_only_active(client, app):
    with app.app_context():
        active_review = Review(
            product_id=1,
            user_name='maxim',
            text='с активным статусом',
            rating=5,
            status=Review.STATUS_ACTIVE,
        )
        pending_review = Review(
            product_id=1,
            user_name='maxim',
            text='с пендинговым статусом',
            rating=5,
            status=Review.STATUS_PENDING,
        )
        db.session.add(active_review)
        db.session.add(pending_review)
        db.session.commit()
    response = client.get('/api/ugc/reviews/?product_id=1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['results'][0]['text'] == 'с активным статусом'
    assert data['results'][0]['status'] == Review.STATUS_ACTIVE

def test_list_rewiews_invalid_product_id(client):
    response = client.get('/api/ugc/reviews/?product_id=abc')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert 'product_id' in data['details']

def test_list_reviews_neg_product_id(client):
    response = client.get('/api/ugc/reviews/?product_id=-5')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert 'product_id' in data['details']

def test_update_review_status(client, app):
    with app.app_context():
        review = Review(
            product_id=1,
            user_name='maxim',
            text='с пендинговым статусом',
            rating=5,
            status=Review.STATUS_PENDING,
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id
    response = client.patch(f'/api/ugc/reviews/{review_id}/status/', json={
        'status': Review.STATUS_ACTIVE,
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == review_id
    assert data['status'] == Review.STATUS_ACTIVE

def test_update_review_invalid_status(client, app):
    with app.app_context():
        review = Review(
            product_id=1,
            user_name='maxim',
            text='с пендинговым статусом',
            rating=5,
            status=Review.STATUS_PENDING,
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id
    response = client.patch(f'/api/ugc/reviews/{review_id}/status/', json={
        'status': 'invalidniy',
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert 'status' in data['details']

def test_update_review_status_not_found(client):
    response = client.patch('/api/ugc/reviews/500/status/', json={
        'status': Review.STATUS_ACTIVE,
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['error_code'] == 'REVIEW_NOT_FOUND'