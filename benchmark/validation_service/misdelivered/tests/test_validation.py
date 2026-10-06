import pytest

from user_service import UserService


def test_valid_registration():
    service = UserService()
    user = service.register("user@example.com", "pass1234")
    assert user["email"] == "user@example.com"


def test_invalid_email_raises():
    service = UserService()
    with pytest.raises(ValueError):
        service.register("bad-email", "pass1234")


def test_weak_password_raises():
    service = UserService()
    with pytest.raises(ValueError):
        service.register("user@example.com", "short")
