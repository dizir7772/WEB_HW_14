import unittest
from unittest.mock import patch, AsyncMock

from src.services.auth import auth_service


def test_get_birthday_list(client, token, monkeypatch, contact, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        shift = 360

        response = client.get(
            f"/api/search/shift/{shift}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        assert response.json() == []


def test_find_contacts_by_partial_info_ok(client, token, monkeypatch, contact, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        partial_info = contact.get('firstname')

        response = client.get(
            f"/api/search/find/{partial_info}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text


def test_find_contacts_by_partial_info_fail(client, token, monkeypatch, contact, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        partial_info = "wrong info"

        response = client.get(
            f"/api/search/find/{partial_info}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == []


if __name__ == '__main__':
    unittest.main()
