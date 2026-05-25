import pytest
import requests
from apps.shop.integrations.notification_client import notify_order_created


@pytest.mark.django_db
def test_notify_order_created_sends_post_request(monkeypatch, settings):
    settings.NOTIFICATION_SERVICE_URL = 'http://testserver/api/notifications'
    called = {}
    class FakeResponse:
        def raise_for_status(self):
            return None
    def fake_post(url, json, timeout):
        called['url'] = url
        called['json'] = json
        called['timeout'] = timeout
        return FakeResponse()
    monkeypatch.setattr(requests, 'post', fake_post)
    notify_order_created(order_id=10, user_id=5)
    assert called == {
        'url': 'http://testserver/api/notifications/order-created/',
        'json': {
            'order_id': 10,
            'user_id': 5,
            'message': 'Order 10 created.',
        },
        'timeout': 3,
    }


@pytest.mark.django_db
def test_notify_order_created_does_not_raise_on_request_error(monkeypatch, settings):
    settings.NOTIFICATION_SERVICE_URL = 'http://testserver/api/notifications'
    def fake_post(url, json, timeout):
        raise requests.RequestException('Service unavailable')
    monkeypatch.setattr(requests, 'post', fake_post)
    notify_order_created(order_id=10, user_id=5)