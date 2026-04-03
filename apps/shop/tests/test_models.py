import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from apps.shop.models import Category, Product, Cart, CartItem, Order, OrderItem

@pytest.mark.django_db
def test_category_str_returns_name():
    category = Category.objects.create(name='Тест', slug='test')
    assert str(category) == 'Тест'

@pytest.mark.django_db
def test_product_str_returns_name():
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
    assert str(product) == 'iPhone 16'

@pytest.mark.django_db
def test_product_is_linked_to_category():
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
    assert product.category == category
    assert product in category.products.all()

@pytest.mark.django_db
def test_user_can_have_only_one_cart():
    user = User.objects.create(username='max', password='12345')
    Cart.objects.create(user=user)
    with pytest.raises(IntegrityError):
        Cart.objects.create(user=user)

@pytest.mark.django_db
def test_cart_item_is_linked_to_cart_and_product():
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
    assert cart_item.product == product
    assert cart_item.quantity == 2
    assert cart_item.cart == cart
    assert cart_item in cart.items.all()

@pytest.mark.django_db
def test_cart_item_quantity_default_is_1():
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
    cart_item = CartItem.objects.create(cart=cart, product=product)
    assert cart_item.quantity == 1

@pytest.mark.django_db
def test_cart_cannot_have_duplicate_product_items():
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
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)
    with pytest.raises(IntegrityError):
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)

@pytest.mark.django_db
def test_order_status_default_is_new():
    user = User.objects.create(username='max', password='12345')
    order = Order.objects.create(user=user)
    assert order.status == 'new'

@pytest.mark.django_db
def test_order_item_is_linked_to_order_and_product():
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
    assert order_item.product == product
    assert order_item.quantity == 2
    assert order_item.order == order
    assert order_item.price == 100000
    assert order_item in order.items.all()

@pytest.mark.django_db
def test_order_cannot_duplicate_product_items():
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
    OrderItem.objects.create(order=order, product=product, quantity=1, price=100000)
    with pytest.raises(IntegrityError):
        OrderItem.objects.create(order=order, product=product, quantity=2, price=100000)