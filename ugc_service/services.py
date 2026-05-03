import requests
from ugc_service.config import Config
from ugc_service.errors import DjangoServiceUnavailable, ProductNotFound
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

def create_review(data: dict) -> Review:
    """
    Проверяет существование товара и создает отзыв.
    """
    check_product_exists(data['product_id'])

    review = Review(
        product_id=data['product_id'],
        user_name=data['user_name'],
        text=data['text'],
        rating=data['rating'],
    )
    db.session.add(review)
    db.session.commit()
    return review