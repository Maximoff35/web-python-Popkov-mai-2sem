from django.db import transaction
from apps.shop.models import Cart, Order, OrderItem
from apps.shop.domain.exceptions import EmptyCart, NotEnoughStock


def create_order_from_cart(user):
    """
    Создает заказ из корзины пользователя:
    - получает или создает корзину
    - проверяет, что она не пустая
    - проверяет остатки товаров
    - создает заказ
    - переносит товары из корзины в заказ
    - уменьшает остатки товаров
    - чистит корзину.
    """

    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        raise EmptyCart()

    for item in cart_items:
        product = item.product
        if product.stock < item.quantity:
            raise NotEnoughStock(
                details={
                    'product_id': product.id,
                    'product_name': product.name,
                    'available': product.stock,
                    'requested': item.quantity,
                }
            )
    with transaction.atomic():
        order = Order.objects.create(user=user)

        for item in cart_items:
            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            product.stock -= item.quantity
            product.save()

        cart_items.delete()

    return order