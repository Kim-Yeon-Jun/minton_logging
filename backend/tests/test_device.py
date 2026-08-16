from datetime import timedelta


def _issue_device_code(client, device_name="Wear OS"):
    resp = client.post("/api/device/code", json={"device_name": device_name})
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_pairing_flow_success(client, register_user):
    user = register_user("owner")
    issued = _issue_device_code(client)

    approve = client.post(
        "/api/device/approve",
        headers=user["headers"],
        json={"user_code": issued["user_code"]},
    )
    assert approve.status_code == 200, approve.text

    token_resp = client.post("/api/device/token", json={"device_code": issued["device_code"]})
    assert token_resp.status_code == 200, token_resp.text
    body = token_resp.json()
    assert body["id"] == user["id"]
    assert body["username"] == user["username"]

    me = client.get("/api/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["id"] == user["id"]


def test_token_polling_before_approval_is_pending(client):
    issued = _issue_device_code(client)
    resp = client.post("/api/device/token", json={"device_code": issued["device_code"]})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "authorization_pending"


def test_approve_requires_login(client):
    issued = _issue_device_code(client)
    resp = client.post("/api/device/approve", json={"user_code": issued["user_code"]})
    assert resp.status_code == 401


def test_approve_rejects_unknown_code(client, register_user):
    user = register_user("owner")
    resp = client.post("/api/device/approve", headers=user["headers"], json={"user_code": "000000"})
    assert resp.status_code == 400


def test_token_rejects_unknown_device_code(client):
    resp = client.post("/api/device/token", json={"device_code": "not-a-real-device-code"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "expired_code"


def test_device_code_is_single_use(client, register_user):
    user = register_user("owner")
    issued = _issue_device_code(client)

    client.post("/api/device/approve", headers=user["headers"], json={"user_code": issued["user_code"]})
    first = client.post("/api/device/token", json={"device_code": issued["device_code"]})
    assert first.status_code == 200

    second = client.post("/api/device/token", json={"device_code": issued["device_code"]})
    assert second.status_code == 400


def test_expired_code_rejected_on_approve_and_token(client, register_user, db_session):
    from models.device import DeviceAuthCode

    user = register_user("owner")
    issued = _issue_device_code(client)

    record = db_session.query(DeviceAuthCode).filter(
        DeviceAuthCode.device_code == issued["device_code"]
    ).first()
    record.expires_at = record.expires_at - timedelta(minutes=20)
    db_session.commit()

    approve = client.post(
        "/api/device/approve",
        headers=user["headers"],
        json={"user_code": issued["user_code"]},
    )
    assert approve.status_code == 400

    token_resp = client.post("/api/device/token", json={"device_code": issued["device_code"]})
    assert token_resp.status_code == 400
