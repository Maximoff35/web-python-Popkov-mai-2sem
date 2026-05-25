import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from notification_service.main import app
from notification_service.auth import create_access_token
from notification_service.services import get_order_from_django


client = TestClient(app)


def test_health_check():
    response = client.get('/api/notifications/health/')
    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'service': 'notifications',
    }

def test_login_success():
    response = client.post('/api/notifications/auth/token', json={
        'username': 'admin',
        'password': 'admin',
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

def test_login_invalid_credentials():
    response = client.post('/api/notifications/auth/token', json={
        'username': 'admin',
        'password': 'wrong-password',
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username or password'

def test_protected_without_token():
    response = client.get('/api/notifications/protected/')
    assert response.status_code == 401

def test_protected_with_token():
    token = create_access_token('admin')
    response = client.get(
        '/api/notifications/protected/',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Доступ разрешен.',
        'user': 'admin',
    }

def test_create_order_notification():
    response = client.post(
        '/api/notifications/order-created/',
        json={
            'order_id': 1,
            'user_id': 1,
            'message': 'Order created.',
        },
       headers={
           'X-Service-Token': 'dev-service-token',
       },
    )
    assert response.status_code == 202
    assert response.json() == {
        'status': 'accepted',
        'detail': 'Notification for order 1 scheduled.',
    }

def test_create_order_notification_invalid_data():
    response = client.post('/api/notifications/order-created/', json={
        'order_id': -1,
        'user_id': 1,
        'message': '',
    })
    assert response.status_code == 422

def test_check_order_success(monkeypatch):
    async def fake_get_order_from_django(order_id: int):
        return {
            'id': order_id,
            'status': 'new',
            'items': [],
        }
    monkeypatch.setattr(
        'notification_service.main.get_order_from_django',
        fake_get_order_from_django,
    )
    response = client.get('/api/notifications/check-order/1/')
    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'order': {
            'id': 1,
            'status': 'new',
            'items': [],
        },
    }

def test_check_order_not_found(monkeypatch):
    async def fake_get_order_from_django(order_id: int):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found',
        )
    monkeypatch.setattr(
        'notification_service.main.get_order_from_django',
        fake_get_order_from_django,
    )
    response = client.get('/api/notifications/check-order/999/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Order not found'

def test_check_order_django_unavailable(monkeypatch):
    async def fake_get_order_from_django(order_id: int):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Django shop service unavailable',
        )
    monkeypatch.setattr(
        'notification_service.main.get_order_from_django',
        fake_get_order_from_django,
    )
    response = client.get('/api/notifications/check-order/1/')
    assert response.status_code == 503
    assert response.json()['detail'] == 'Django shop service unavailable'

def test_get_order_from_django_success(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                'id': 1,
                'status': 'new',
                'items': [],
            }

    async def fake_get(self, url):
        return FakeResponse()

    monkeypatch.setattr(httpx.AsyncClient, 'get', fake_get)
    result = asyncio.run(get_order_from_django(1))
    assert result == {
        'id': 1,
        'status': 'new',
        'items': [],
    }

def test_get_order_from_django_not_found(monkeypatch):
    class FakeResponse:
        status_code = 404

    async def fake_get(self, url):
        return FakeResponse()

    monkeypatch.setattr(httpx.AsyncClient, 'get', fake_get)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_order_from_django(999))
    assert exc.value.status_code == 404
    assert exc.value.detail == 'Order not found'

def test_get_order_from_django_unexpected_status(monkeypatch):
    class FakeResponse:
        status_code = 403

    async def fake_get(self, url):
        return FakeResponse()

    monkeypatch.setattr(httpx.AsyncClient, 'get', fake_get)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_order_from_django(1))
    assert exc.value.status_code == 503
    assert exc.value.detail == 'Unexpected response from Django shop service'

def test_get_order_from_django_service_unavailable(monkeypatch):
    async def fake_get(self, url):
        raise httpx.RequestError('Connection error')

    monkeypatch.setattr(httpx.AsyncClient, 'get', fake_get)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_order_from_django(1))
    assert exc.value.status_code == 503
    assert exc.value.detail == 'Django shop service unavailable'

def test_protected_with_invalid_token():
    response = client.get(
        '/api/notifications/protected/',
        headers={
            'Authorization': 'Bearer invalid-token',
        },
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'