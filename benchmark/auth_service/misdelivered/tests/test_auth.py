from app import AppService


def test_valid_login():
    app = AppService()
    assert app.login("alice", "s3cret") is True


def test_invalid_password():
    app = AppService()
    assert app.login("alice", "wrong") is False


def test_unknown_user():
    app = AppService()
    assert app.login("mallory", "pw") is False
