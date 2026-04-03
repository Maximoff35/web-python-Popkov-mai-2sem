from rest_framework import serializers
from .models import Product

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
    quantity = serializers.IntegerField(default=1)