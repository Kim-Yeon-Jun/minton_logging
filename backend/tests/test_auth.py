def test_register_and_login_success(register_user):
    user = register_user("auth")
    assert user["id"]
    assert user["token"]


def test_login_rejects_wrong_password(client, register_user):
    user = register_user("auth")
    resp = client.post(
        "/api/login",
        json={"username": user["username"], "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_password_is_hashed_not_plaintext(register_user, db_session):
    from models.user import User

    user = register_user("auth")
    db_user = db_session.query(User).filter(User.id == user["id"]).first()

    assert db_user.login_pw != "pass1234"
    assert db_user.login_pw.startswith("$2b$")


def test_me_requires_token(client):
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, register_user):
    user = register_user("auth")
    resp = client.get("/api/me", headers=user["headers"])

    assert resp.status_code == 200
    assert resp.json()["id"] == user["id"]


def test_change_password_requires_correct_current_password(client, register_user):
    user = register_user("auth")
    resp = client.put(
        "/api/users/me/password",
        headers=user["headers"],
        json={"current_password": "wrong", "new_password": "newpass123"},
    )
    assert resp.status_code == 401


def test_change_password_success_and_relogin(client, register_user):
    user = register_user("auth")
    resp = client.put(
        "/api/users/me/password",
        headers=user["headers"],
        json={"current_password": "pass1234", "new_password": "newpass123"},
    )
    assert resp.status_code == 200

    relogin = client.post(
        "/api/login",
        json={"username": user["username"], "password": "newpass123"},
    )
    assert relogin.status_code == 200
