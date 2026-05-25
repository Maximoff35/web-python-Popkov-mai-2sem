import requests
from typing import List
from ugc_service.config import Config
from ugc_service.errors import DjangoServiceUnavailable, ProductNotFound, ReviewNotFound
from ugc_service.models import Review
from ugc_service.extensions import db


def check_product_exists(product_id: int) -> None:
    """
    Проверяет существование товара в Django API.
    """
    url = f'{Config.DJANGO_SHOP_API_URL}/products/{product_id}/'

    try:
        response = requests.get(url, timeout=3)
    except requests.RequestException:
        raise DjangoServiceUnavailable()

    if response.status_code == 404:
        raise ProductNotFound(details={'product_id': product_id})

    if response.status_code != 200:
        raise DjangoServiceUnavailable(details={'status_code': response.status_code})

def create_review(data: dict, user: dict) -> Review:
    """
    Проверяет существование товара и создает отзыв от имени авторизованного пользователя.
    """
    check_product_exists(data['product_id'])

    review = Review(
        product_id=data['product_id'],
        user_name=user['username'],
        text=data['text'],
        rating=data['rating'],
    )
    db.session.add(review)
    db.session.commit()
    return review

def get_reviews(product_id: int | None = None, only_active: bool = True) -> List[Review]:
    """
    Возвращает список отзывов.
    Поддерживает фильтрацию по товару и по статусу active.
    """
    query = Review.query
    if product_id is not None:
        query = query.filter_by(product_id=product_id)
    if only_active:
        query = query.filter_by(status=Review.STATUS_ACTIVE)
    return query.order_by(Review.created_at.desc()).all()

def update_review_status(review_id: int, status: str) -> Review:
    """
    Изменяет статус отзыва.
    """
    review = db.session.get(Review, review_id)
    if review is None:
        raise ReviewNotFound(details={'review_id': review_id})
    review.status = status
    db.session.commit()
    return review

def get_user_from_django_token(auth_header: str | None) -> dict:
    """
    Проверяет JWT пользователя через Django auth API.
    """
    if not auth_header:
        raise DjangoServiceUnavailable(
            message='Authorization header is required.',
            details={'authorization': 'Missing Authorization header.'},
        )
    try:
        response = requests.get(
            Config.DJANGO_AUTH_ME_URL,
            headers={'Authorization': auth_header},
            timeout=3,
        )
    except requests.RequestException:
        raise DjangoServiceUnavailable()
    if response.status_code == 401:
        raise DjangoServiceUnavailable(
            message='Invalid or expired user token.',
            details={'authorization': 'Invalid token.'},
        )
    if response.status_code != 200:
        raise DjangoServiceUnavailable(details={'status_code': response.status_code})
    return response.json()