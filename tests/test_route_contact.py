import unittest
from unittest.mock import patch, AsyncMock

from src.database.models import User
from src.services.auth import auth_service


def test_create_contact(client, token, contact, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.post("/api/contacts/",
                               json=contact,
                               headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["firstname"] == contact["firstname"]
        assert data["lastname"] == contact["lastname"]
        assert data["email"] == contact["email"]
        assert data["phone"] == contact["phone"]
        assert data["birthday"] == contact["birthday"]
        assert data["additional_info"] == contact["additional_info"]
        assert data["is_favorite"] == contact["is_favorite"]


def test_get_contacts(client, token, monkeypatch):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            "api/contacts/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text


def test_get_contact_ok(client, token, monkeypatch, contact):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        contact_id = 1
        response = client.get(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data["firstname"] == contact["firstname"]
        assert data["lastname"] == contact["lastname"]
        assert data["email"] == contact["email"]
        assert data["phone"] == contact["phone"]
        assert data["birthday"] == contact["birthday"]
        assert data["additional_info"] == contact["additional_info"]
        assert data["is_favorite"] == contact["is_favorite"]


def test_get_contact_fail(client, token, monkeypatch):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        contact_id = 100
        response = client.get(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


def test_favorite_contact_ok(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "admin"
        session.commit()

        contact_id = 1
        response = client.patch(
            f"/api/contacts/{contact_id}/favorite", json={"is_favorite": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["is_favorite"] == True


def test_favorite_contact_fail_role(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "user"
        session.commit()

        contact_id = 1
        response = client.patch(
            f"/api/contacts/{contact_id}/favorite", json={"is_favorite": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, response.text


def test_favorite_contact_contact_not_exist(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "admin"
        session.commit()

        contact_id = 100
        response = client.patch(
            f"/api/contacts/{contact_id}/favorite", json={"is_favorite": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


def test_update_contact(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "moderator"
        session.commit()

        contact_id = 1
        updated_contact = {
            "firstname": "Some",
            "lastname": "Body",
            "email": "some@example.com",
            "phone": "0987654321",
            "birthday": "2023-05-04",
            "additional_info": "some text",
            "is_favorite": False,
            "user_id": 1
        }
        response = client.put(
            f"/api/contacts/{contact_id}",
            json=updated_contact,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data
        assert data["firstname"] == updated_contact["firstname"]
        assert data["lastname"] == updated_contact["lastname"]
        assert data["email"] == updated_contact["email"]
        assert data["phone"] == updated_contact["phone"]
        assert data["birthday"] == updated_contact["birthday"]
        assert data["additional_info"] == updated_contact["additional_info"]
        assert data["is_favorite"] == updated_contact["is_favorite"]


def test_update_contact_fail_role(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "user"
        session.commit()

        contact_id = 1
        updated_contact = {
            "firstname": "Some",
            "lastname": "Body",
            "email": "some@example.com",
            "phone": "0987654321",
            "birthday": "2023-05-04",
            "additional_info": "some text",
            "is_favorite": False,
            "user_id": 1
        }
        response = client.put(
            f"/api/contacts/{contact_id}",
            json=updated_contact,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, response.text


def test_update_contact_fail_contact_not_exist(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "moderator"
        session.commit()

        contact_id = 100
        updated_contact = {
            "firstname": "Some",
            "lastname": "Body",
            "email": "some@example.com",
            "phone": "0987654321",
            "birthday": "2023-05-04",
            "additional_info": "some text",
            "is_favorite": False,
            "user_id": 1
        }
        response = client.put(
            f"/api/contacts/{contact_id}",
            json=updated_contact,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


def test_remove_contact_ok(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "admin"
        session.commit()

        contact_id = 1
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204, response.text


def test_remove_contact_fail_role(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "user"
        session.commit()

        contact_id = 1
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, response.text


def test_remove_contact_fail_id(client, token, monkeypatch, contact, session, user):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user: User = session.query(User).filter(User.email == user.get("email")).first()
        current_user.roles = "admin"
        session.commit()

        contact_id = 100
        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


if __name__ == '__main__':
    unittest.main()
