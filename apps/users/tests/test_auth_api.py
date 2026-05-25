import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_user_success():
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'max',
        'email': 'max@test.ru',
        'password': 'strongpass123',
        'password_confirm': 'strongpass123',
    }, format='json')
    assert response.status_code == 201
    assert response.data['message'] == 'Пользователь зарегистрирован.'
    assert response.data['user']['username'] == 'max'
    assert response.data['user']['email'] == 'max@test.ru'
    user = User.objects.get(username='max')
    assert user.email == 'max@test.ru'
    assert user.check_password('strongpass123')


@pytest.mark.django_db
def test_register_user_passwords_do_not_match():
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'max',
        'email': 'max@test.ru',
        'password': 'strongpass123',
        'password_confirm': 'wrongpass123',
    }, format='json')
    assert response.status_code == 400
    assert 'password_confirm' in response.data


@pytest.mark.django_db
def test_register_user_duplicate_username():
    User.objects.create_user(
        username='max',
        email='old@test.ru',
        password='strongpass123',
    )
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'max',
        'email': 'new@test.ru',
        'password': 'strongpass123',
        'password_confirm': 'strongpass123',
    }, format='json')
    assert response.status_code == 400
    assert 'username' in response.data


@pytest.mark.django_db
def test_register_user_duplicate_email():
    User.objects.create_user(
        username='oldmax',
        email='max@test.ru',
        password='strongpass123',
    )
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'max',
        'email': 'max@test.ru',
        'password': 'strongpass123',
        'password_confirm': 'strongpass123',
    }, format='json')
    assert response.status_code == 400
    assert 'email' in response.data


@pytest.mark.django_db
def test_register_user_without_username():
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'email': 'max@test.ru',
        'password': 'strongpass123',
        'password_confirm': 'strongpass123',
    }, format='json')
    assert response.status_code == 400
    assert 'username' in response.data


@pytest.mark.django_db
def test_register_user_without_password():
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'max',
        'email': 'max@test.ru',
        'password_confirm': 'strongpass123',
    }, format='json')
    assert response.status_code == 400
    assert 'password' in response.data


@pytest.mark.django_db
def test_login_success():
    User.objects.create_user(
        username='max',
        email='max@test.ru',
        password='strongpass123',
    )
    client = APIClient()
    response = client.post('/api/auth/login/', {
        'username': 'max',
        'password': 'strongpass123',
    }, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_login_wrong_password():
    User.objects.create_user(
        username='max',
        email='max@test.ru',
        password='strongpass123',
    )
    client = APIClient()
    response = client.post('/api/auth/login/', {
        'username': 'max',
        'password': 'wrongpass123',
    }, format='json')
    assert response.status_code == 401
    assert 'detail' in response.data


@pytest.mark.django_db
def test_me_without_token_returns_401():
    client = APIClient()
    response = client.get('/api/auth/me/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_with_token_returns_current_user():
    User.objects.create_user(
        username='max',
        email='max@test.ru',
        password='strongpass123',
    )
    client = APIClient()
    login_response = client.post('/api/auth/login/', {
        'username': 'max',
        'password': 'strongpass123',
    }, format='json')
    access_token = login_response.data['access']
    response = client.get(
        '/api/auth/me/',
        HTTP_AUTHORIZATION=f'Bearer {access_token}',
    )
    assert response.status_code == 200
    assert response.data == {
        'id': User.objects.get(username='max').id,
        'username': 'max',
        'email': 'max@test.ru',
    }


@pytest.mark.django_db
def test_refresh_token_success():
    User.objects.create_user(
        username='max',
        email='max@test.ru',
        password='strongpass123',
    )
    client = APIClient()
    login_response = client.post('/api/auth/login/', {
        'username': 'max',
        'password': 'strongpass123',
    }, format='json')
    refresh_token = login_response.data['refresh']
    response = client.post('/api/auth/refresh/', {
        'refresh': refresh_token,
    }, format='json')
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_refresh_token_invalid():
    client = APIClient()
    response = client.post('/api/auth/refresh/', {
        'refresh': 'invalid-token',
    }, format='json')
    assert response.status_code == 401
    assert 'detail' in response.data