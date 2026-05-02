from django.shortcuts import get_object_or_404
from apps.shop.models import Product, Cart, CartItem


def add_product_to_cart(user, product_id, quantity):
    """
    Добавляет товар в корзину пользователя:
    - находит товар
    - получает или создает корзину
    - добавляет товар в корзину или увеличивает количество.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()