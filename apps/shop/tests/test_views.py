import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.shop.models import Product, Category, Cart, CartItem

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
    assert len(response.data) == 1
    assert response.data[0]['id'] == active_product.id
    assert response.data[0]['name'] == 'iPhone 16'

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
    response = client.post('/api/shop/cart/add/', {'product_id': 1, 'quantity': 3}, format='json')
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
    response = client.post('/api/shop/cart/add/', {'product_id': 1, 'quantity': 3}, format='json')
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
    response = client.post('/api/shop/cart/add/', {'product_id': 1, 'quantity': 1}, format='json')
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
