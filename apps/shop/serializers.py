from rest_framework import serializers
from .models import Product, CartItem, Cart, OrderItem, Order


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    Используется для преобразования товара в JSON
    при получении списка и детальной информации о товаре.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'stock']

class AddToCartSerializer(serializers.Serializer):
    """
    Сериализатор для добавления товара в корзину.
    Принимает данные от клиента:
    - product_id: id товара
    - quantity: количество шт (1 по умолчанию)
    """
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CartItem.
    Используется для преобразования элемента корзины в JSON
    при GET-запросе корзины.
    """
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_name', 'price', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Cart.
    Используется для преобразования всей корзины в JSON
    при GET-запросе корзины.
    """
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели OrderItem.
    Используется для преобразования позиции заказа в JSON
    при GET-запросе данных о заказах.
    """
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Order.
    Используется для преобразования заказа в JSON
    при GET-запросе данных о заказах.
    """
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'items']