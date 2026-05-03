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