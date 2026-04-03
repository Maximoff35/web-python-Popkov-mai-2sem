from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    """
    Категория товаров.
    Используется для группировки продуктов.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Товар в магазине.
    Содержит основную информацию о продукте:
    название, цену, остаток (шт), принадлежность к категории.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    """
    Корзина пользователя.
    Временное хранилище товаров перед оформлением заказа.
    Один пользователь может иметь одну активную корзину.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'

class CartItem(models.Model):
    """
    Позиция в корзине.
    Связывает корзину и товар.
    Хранит количество товара.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product'),
        ]

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'


class Order(models.Model):
    """
    Заказ пользователя.
    Создается после оформления корзины.
    Хранит статус выполнения.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default='new', max_length=20)

    def __str__(self):
        return f'Заказ #{self.id} пользователя {self.user.username}'

class OrderItem(models.Model):
    """
    Позиция в заказе.
    Хранит товар, его количество и цену на момент покупки.
    Цена фиксируется для отсутствия зависимости от будущих изменений.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product'),
        ]

    def __str__(self):
        return f'{self.product.name} x {self.quantity} в заказе #{self.order.id}'