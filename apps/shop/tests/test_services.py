import pytest
from django.contrib.auth.models import User
from apps.shop.models import Product, Category, Cart, CartItem, Order, OrderItem
from apps.shop.services.cart_service import add_product_to_cart, update_cart_item_quantity, delete_cart_item
from apps.shop.services.order_service import create_order_from_cart
from apps.shop.domain.exceptions import InvalidQuantity, ProductNotFound, EmptyCart, NotEnoughStock


@pytest.mark.django_db
def test_add_product_to_cart_creates_item():
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
    cart_item = add_product_to_cart(user=user, product_id=product.id, quantity=2)
    assert cart_item.product == product
    assert cart_item.quantity == 2
    assert Cart.objects.filter(user=user).exists()
    assert CartItem.objects.count() == 1

@pytest.mark.django_db
def test_add_product_to_cart_updates_quantity():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iPhone-16',
        description='Предпоследний айфон',
        price=100000,
        stock=7,
        is_active=True,
    )
    add_product_to_cart(user=user, product_id=product.id, quantity=2)
    cart_item = add_product_to_cart(user=user, product_id=product.id, quantity=3)
    assert cart_item.quantity == 5
    assert CartItem.objects.count() == 1

@pytest.mark.django_db
def test_add_product_to_cart_raises_invalid_quantity():
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
    with pytest.raises(InvalidQuantity):
        add_product_to_cart(user=user, product_id=product.id, quantity=0)

@pytest.mark.django_db
def test_add_product_to_cart_raises_product_not_found():
    user = User.objects.create(username='max', password='12345')
    with pytest.raises(ProductNotFound):
        add_product_to_cart(user=user, product_id=500, quantity=1)

@pytest.mark.django_db
def test_create_order_from_cart_success():
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
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    order = create_order_from_cart(user=user)
    product.refresh_from_db()
    assert isinstance(order, Order)
    assert order.user == user
    assert OrderItem.objects.count() == 1
    assert OrderItem.objects.first().quantity == 2
    assert OrderItem.objects.first().price == product.price
    assert product.stock == 3
    assert CartItem.objects.count() == 0

@pytest.mark.django_db
def test_create_order_from_cart_raises_empty_cart():
    user = User.objects.create(username='max', password='12345')
    cart = Cart.objects.create(user=user)
    with pytest.raises(EmptyCart):
        create_order_from_cart(user=user)

@pytest.mark.django_db
def test_create_order_from_cart_raises_not_enough_stock():
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
    CartItem.objects.create(cart=cart, product=product, quantity=10)
    with pytest.raises(NotEnoughStock):
        create_order_from_cart(user=user)
    assert Order.objects.count() == 0
    assert OrderItem.objects.count() == 0
    assert CartItem.objects.count() == 1

@pytest.mark.django_db
def test_update_cart_item_quantity_success():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iphone-16',
        description='айфон',
        price=100000,
        stock=10,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    updated_item = update_cart_item_quantity(
        user=user,
        cart_item_id=cart_item.id,
        quantity=5,
    )
    cart_item.refresh_from_db()
    assert updated_item.id == cart_item.id
    assert cart_item.quantity == 5

@pytest.mark.django_db
def test_update_cart_item_quantity_raises_invalid_quantity():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iphone-16',
        description='айфон',
        price=100000,
        stock=10,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    with pytest.raises(InvalidQuantity):
        update_cart_item_quantity(
            user=user,
            cart_item_id=cart_item.id,
            quantity=0,
        )
    cart_item.refresh_from_db()
    assert cart_item.quantity == 2


@pytest.mark.django_db
def test_update_cart_item_quantity_raises_product_not_found_for_other_user_item():
    owner = User.objects.create(username='owner', password='12345')
    stranger = User.objects.create(username='stranger', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iphone-16',
        description='айфон',
        price=100000,
        stock=10,
        is_active=True,
    )
    cart = Cart.objects.create(user=owner)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    with pytest.raises(ProductNotFound):
        update_cart_item_quantity(
            user=stranger,
            cart_item_id=cart_item.id,
            quantity=5,
        )
    cart_item.refresh_from_db()
    assert cart_item.quantity == 2


@pytest.mark.django_db
def test_delete_cart_item_success():
    user = User.objects.create(username='max', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iphone-16',
        description='айфон',
        price=100000,
        stock=10,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    delete_cart_item(
        user=user,
        cart_item_id=cart_item.id,
    )
    assert not CartItem.objects.filter(id=cart_item.id).exists()

@pytest.mark.django_db
def test_delete_cart_item_raises_product_not_found_for_other_user_item():
    owner = User.objects.create(username='owner', password='12345')
    stranger = User.objects.create(username='stranger', password='12345')
    category = Category.objects.create(name='Телефоны', slug='phones')
    product = Product.objects.create(
        category=category,
        name='iPhone 16',
        slug='iphone-16',
        description='айфон',
        price=100000,
        stock=10,
        is_active=True,
    )
    cart = Cart.objects.create(user=owner)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    with pytest.raises(ProductNotFound):
        delete_cart_item(
            user=stranger,
            cart_item_id=cart_item.id,
        )
    assert CartItem.objects.filter(id=cart_item.id).exists()