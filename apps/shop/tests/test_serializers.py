import pytest
from django.contrib.auth.models import User
from apps.shop.models import Category, Product, Cart, CartItem, Order, OrderItem
from apps.shop.serializers import (
    ProductSerializer,
    AddToCartSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
)

@pytest.mark.django_db
def test_product_serializer_returns_correct_data():
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    serializer = ProductSerializer(product)
    assert serializer.data == {
        'id': product.id,
        'name': 'iPhone 16',
        'slug': 'iPhone-16',
        'price': '100000.00',
        'stock': 5,
    }

def test_add_to_cart_serializer_valid_data():
    data = {'product_id': 1, 'quantity': 3}
    serializer = AddToCartSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == data

def test_add_to_cart_serializer_quantity_default_is_1():
    data = {'product_id': 1}
    serializer = AddToCartSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {'product_id': 1, 'quantity': 1}

def test_add_to_cart_serializer_is_invalid_without_product_id():
    data = {'quantity': 3}
    serializer = AddToCartSerializer(data=data)
    assert not serializer.is_valid()
    assert 'product_id' in serializer.errors

def test_add_to_cart_serializer_is_invalid_when_product_id_is_not_integer():
    data = {'product_id': 'abc', 'quantity': 3}
    serializer = AddToCartSerializer(data=data)
    assert not serializer.is_valid()
    assert 'product_id' in serializer.errors

def test_add_to_cart_serializer_is_invalid_when_quantity_is_not_integer():
    data = {'product_id': 1, 'quantity': 'abc'}
    serializer = AddToCartSerializer(data=data)
    assert not serializer.is_valid()
    assert 'quantity' in serializer.errors

@pytest.mark.django_db
def test_cart_item_serializer_returns_correct_data():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    serializer = CartItemSerializer(cart_item)
    assert serializer.data == {
        'id': cart_item.id,
        'product_id': product.id,
        'product_name': 'iPhone 16',
        'price': '100000.00',
        'quantity': 2,
    }

@pytest.mark.django_db
def test_cart_serializer_returns_items():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product1 = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    product2 = Product.objects.create(
        category=category,
        name='Ксяоми',
        slug='xiaomi',
        description='Китайский телефон',
        price=5000,
        stock=10,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    cart_item_1 = CartItem.objects.create(cart=cart, product=product1, quantity=2)
    cart_item_2 = CartItem.objects.create(cart=cart, product=product2, quantity=5)
    serializer = CartSerializer(cart)
    assert serializer.data == {
        'id': cart.id,
        'items': [
            {
                'id': cart_item_1.id,
                'product_id': product1.id,
                'product_name': 'iPhone 16',
                'price': '100000.00',
                'quantity': 2,
            },
            {
                'id': cart_item_2.id,
                'product_id': product2.id,
                'product_name': 'Ксяоми',
                'price': '5000.00',
                'quantity': 5,
            },
        ],
    }

@pytest.mark.django_db
def test_order_item_serializer_returns_correct_data():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    order = Order.objects.create(user=user)
    order_item = OrderItem.objects.create(order=order, product=product, quantity=2, price=100000)
    serializer = OrderItemSerializer(order_item)
    assert serializer.data == {
        'id': order_item.id,
        'product_id': product.id,
        'product_name': 'iPhone 16',
        'price': '100000.00',
        'quantity': 2,
    }

@pytest.mark.django_db
def test_order_serializer_returns_items():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product1 = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    product2 = Product.objects.create(
        category=category,
        name='Ксяоми',
        slug='xiaomi',
        description='Китайский телефон',
        price=5000,
        stock=10,
        is_active=True,
    )
    order = Order.objects.create(user=user)
    order_item1 = OrderItem.objects.create(order=order, product=product1, quantity=2, price=100000)
    order_item2 = OrderItem.objects.create(order=order, product=product2, quantity=5, price=5000)
    serializer = OrderSerializer(order)
    assert serializer.data['id'] == order.id
    assert serializer.data['status'] == 'new'
    assert 'created_at' in serializer.data
    assert serializer.data['items'] == [
        {
            'id': order_item1.id,
            'product_id': product1.id,
            'product_name': 'iPhone 16',
            'price': '100000.00',
            'quantity': 2,
        },
        {
            'id': order_item2.id,
            'product_id': product2.id,
            'product_name': 'Ксяоми',
            'price': '5000.00',
            'quantity': 5,
        },
    ]