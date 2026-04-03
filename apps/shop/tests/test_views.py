import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.shop.models import Product, Category, Cart, CartItem, Order, OrderItem

@pytest.mark.django_db
def test_product_list_returns_only_active_products():
    category = Category.objects.create(name='Телефоны', slug='phones')
    active_product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    Product.objects.create(
        category=category,
        name='Old phone',
        slug='old-phone',
        description='Неактивный',
        price=1000,
        stock=1,
        is_active=False,
    )
    client = APIClient()
    response = client.get('/api/shop/products/')
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == active_product.id
    assert response.data['results'][0]['name'] == 'iPhone 16'

@pytest.mark.django_db
def test_product_detail_returns_active_product():
    category = Category.objects.create(name='Телефоны', slug='phones')
    active_product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    client = APIClient()
    response = client.get(f'/api/shop/products/{active_product.id}/')
    assert response.status_code == 200
    assert response.data['id'] == active_product.id
    assert response.data['name'] == 'iPhone 16'

@pytest.mark.django_db
def test_product_detail_returns_404_for_not_active_product():
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=False,
    )
    client = APIClient()
    response = client.get(f'/api/shop/products/{product.id}/')
    assert response.status_code == 404

@pytest.mark.django_db
def test_add_to_cart_returns_401_for_not_authenticated_user():
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
    client = APIClient()
    response = client.post('/api/shop/cart/add/', {'product_id': product.id, 'quantity': 3}, format='json')
    assert response.status_code == 401
    assert response.data == {'error': 'Not authenticated'}

@pytest.mark.django_db
def test_add_to_cart_creates_cart_and_cart_item():
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
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/shop/cart/add/', {'product_id': product.id, 'quantity': 3}, format='json')
    assert response.status_code == 200
    assert response.data == {'message': 'Товар добавлен в корзину.'}
    cart = Cart.objects.get(user=user)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    assert cart_item.quantity == 3

@pytest.mark.django_db
def test_add_to_cart_increases_quantity_if_item_already_exists():
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
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/shop/cart/add/', {'product_id': product.id, 'quantity': 1}, format='json')
    assert response.status_code == 200
    cart_item.refresh_from_db()
    assert cart_item.quantity == 3

@pytest.mark.django_db
def test_add_to_cart_returns_404_for_nonexistent_product():
    user = User.objects.create(username='max', password='12345')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/shop/cart/add/', {'product_id': 9999, 'quantity': 1}, format='json')
    assert response.status_code == 404

@pytest.mark.django_db
def test_cart_view_returns_403_for_not_authenticated_user():
    client = APIClient()
    response = client.get('/api/shop/cart/')
    assert response.status_code == 403

@pytest.mark.django_db
def test_cart_view_returns_user_cart():
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
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/shop/cart/')
    assert response.status_code == 200
    assert response.data == {
        'id': cart.id,
        'items': [
            {
                'id': cart_item.id,
                'product_id': product.id,
                'product_name': 'iPhone 16',
                'price': '100000.00',
                'quantity': 2,
            },
        ],
    }

@pytest.mark.django_db
def test_cart_view_creates_empty_cart_for_authenticated_user():
    user = User.objects.create(username='max', password='12345')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/shop/cart/')
    assert response.status_code == 200
    assert response.data['items'] == []
    assert Cart.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_product_list_filters_by_category():
    phones = Category.objects.create(name='Телефоны', slug='phones')
    laptops = Category.objects.create(name='Ноутбуки', slug='laptops')
    phone = Product.objects.create(
        category=phones,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=5,
        is_active=True,
    )
    Product.objects.create(
        category=laptops,
        name='MacBook Air',
        slug='macbook-air',
        description='макбук',
        price=105000,
        stock=3,
        is_active=True,
    )
    client = APIClient()
    response = client.get('/api/shop/products/?category=phones')
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == phone.id
    assert response.data['results'][0]['name'] == 'iPhone 16'

@pytest.mark.django_db
def test_product_list_searches_by_names():
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
    Product.objects.create(
        category=category,
        name='Ксяоми',
        slug='xiaomi',
        description='Китайский телефон',
        price=5000,
        stock=10,
        is_active=True,
    )
    client = APIClient()
    response = client.get('/api/shop/products/?search=iphone')
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == product.id
    assert response.data['results'][0]['name'] == 'iPhone 16'

@pytest.mark.django_db
def test_product_list_filters_by_category_and_search():
    phones = Category.objects.create(name='Телефоны', slug='phones')
    laptops = Category.objects.create(name='Ноутбуки', slug='laptops')
    phone = Product.objects.create(
        category=phones,
        name='iPhone Air',
        slug='iPhone-air',
        description='айфон эир',
        price=150000,
        stock=17,
        is_active=True,
    )
    Product.objects.create(
        category=phones,
        name='Ксяоми',
        slug='xiaomi',
        description='Китайский телефон',
        price=5000,
        stock=10,
        is_active=True,
    )
    Product.objects.create(
        category=laptops,
        name='MacBook Air',
        slug='macbook-air',
        description='макбук',
        price=105000,
        stock=3,
        is_active=True,
    )
    client = APIClient()
    response = client.get('/api/shop/products/?category=phones&search=air')
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == phone.id
    assert response.data['results'][0]['name'] == 'iPhone Air'

@pytest.mark.django_db
def test_product_list_is_paginated():
    phones = Category.objects.create(name='Телефоны', slug='phones')
    for i in range(6):
        Product.objects.create(
            category=phones,
            name=f'iPhone {i}',
            slug=f'iPhone-{i}',
            description=f'айфон {i}',
            price=150000 + i,
            stock=17 + i,
            is_active=True,
        )
    client = APIClient()
    response = client.get('/api/shop/products/')
    assert response.status_code == 200
    assert response.data['count'] == 6
    assert len(response.data['results']) == 5
    assert response.data['next'] is not None
    assert response.data['previous'] is None

@pytest.mark.django_db
def test_create_order_returns_403_for_not_authenticated_user():
    client = APIClient()
    response = client.post('/api/shop/orders/create/', format='json')
    assert response.status_code == 403

@pytest.mark.django_db
def test_create_order_returns_400_for_empty_cart():
    user = User.objects.create(username='max', password='12345')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/shop/orders/create/', format='json')
    assert response.status_code == 400
    assert response.data == {'error': 'Корзина пуста.'}

@pytest.mark.django_db
def test_create_order_from_cart():
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
    CartItem.objects.create(cart=cart, product=product1, quantity=2)
    CartItem.objects.create(cart=cart, product=product2, quantity=3)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/shop/orders/create/', format='json')
    assert response.status_code == 201
    assert response.data['message'] == 'Заказ создан.'
    order = Order.objects.get(id=response.data['order_id'])
    order_items = OrderItem.objects.filter(order=order)
    assert order.user == user
    assert order_items.count() == 2
    assert not CartItem.objects.filter(cart=cart).exists()
    product1.refresh_from_db()
    product2.refresh_from_db()
    assert product1.stock == 3
    assert product2.stock == 7

@pytest.mark.django_db
def test_create_order_returns_400_if_not_enough_stock():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=1,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/shop/orders/create/', format='json')
    assert response.status_code == 400
    assert response.data == {'error': 'Недостаточно товара "iPhone 16" на складе.'}
    assert Order.objects.count() == 0
    product.refresh_from_db()
    assert product.stock == 1
    assert CartItem.objects.filter(cart=cart).exists()

@pytest.mark.django_db
def test_order_list_returns_403_for_not_authenticated_user():
    client = APIClient()
    response = client.get('/api/shop/orders/')
    assert response.status_code == 403

@pytest.mark.django_db
def test_order_list_retuens_only_current_user_orders():
    user1 = User.objects.create(username='original', password='12345')
    user2 = User.objects.create(username='fake_parodia', password='12345')
    order1 = Order.objects.create(user=user1)
    order2 = Order.objects.create(user=user1)
    Order.objects.create(user=user2)
    client = APIClient()
    client.force_authenticate(user=user1)
    response = client.get('/api/shop/orders/')
    assert response.status_code == 200
    assert response.data['count'] == 2
    returned_ids = [order['id'] for order in response.data['results']]
    assert order1.id in returned_ids
    assert order2.id in returned_ids
    assert len(returned_ids) == 2

@pytest.mark.django_db
def test_order_detail_returns_403_for_not_authenticated_user():
    user = User.objects.create(username='max', password='12345')
    order = Order.objects.create(user=user)
    client = APIClient()
    response = client.get(f'/api/shop/orders/{order.id}/', format='json')
    assert response.status_code == 403

@pytest.mark.django_db
def test_order_detail_returns_user_order():
    user = User.objects.create(username='max', password='12345')
    order = Order.objects.create(user=user)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/shop/orders/{order.id}/', format='json')
    assert response.status_code == 200
    assert response.data['id'] == order.id
    assert response.data['status'] == 'new'

@pytest.mark.django_db
def test_order_detail_returns_404_for_other_user_order():
    user1 = User.objects.create(username='original', password='12345')
    user2 = User.objects.create(username='fake_parodia', password='12345')
    order = Order.objects.create(user=user1)
    client = APIClient()
    client.force_authenticate(user=user2)
    response = client.get(f'/api/shop/orders/{order.id}/', format='json')
    assert response.status_code == 404
