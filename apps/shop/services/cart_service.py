from apps.shop.models import Product, Cart, CartItem
from apps.shop.domain.exceptions import ProductNotFound, InvalidQuantity


def add_product_to_cart(user, product_id, quantity):
    """
    Добавляет товар в корзину пользователя:
    - находит товар
    - получает или создает корзину
    - добавляет товар в корзину или увеличивает количество.
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        raise ProductNotFound(details={'product_id': product_id})
    if quantity <= 0:
        raise InvalidQuantity()
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    return cart_item


def update_cart_item_quantity(user, cart_item_id, quantity):
    """
    Изменяет количество товара в корзине пользователя.
    """
    if quantity <= 0:
        raise InvalidQuantity()
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, cart__user=user)
    except CartItem.DoesNotExist:
        raise ProductNotFound(details={'cart_item_id': cart_item_id})
    cart_item.quantity = quantity
    cart_item.save()
    return cart_item


def delete_cart_item(user, cart_item_id):
    """
    Удаляет товар из корзины пользователя.
    """
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, cart__user=user)
    except CartItem.DoesNotExist:
        raise ProductNotFound(details={'cart_item_id': cart_item_id})
    cart_item.delete()