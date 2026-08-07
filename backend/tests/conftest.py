import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# main.py 등을 import하기 전에 반드시 스키마를 오버라이드해야 한다.
# config.py의 Settings()는 import 시점에 환경변수를 읽어서 고정되기 때문.
TEST_SCHEMA = f"test_bd_log_{uuid.uuid4().hex[:8]}"
os.environ["DATABASE_SCHEMA"] = TEST_SCHEMA

import psycopg2  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from config import settings  # noqa: E402


def _admin_connect():
    return psycopg2.connect(
        host=settings.DATABASE_URL,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        dbname=settings.DATABASE_NAME,
    )


@pytest.fixture(scope="session", autouse=True)
def _test_schema():
    conn = _admin_connect()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{TEST_SCHEMA}"')
    conn.close()

    yield

    conn = _admin_connect()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE')
    conn.close()


@pytest.fixture(scope="session")
def app(_test_schema):
    from main import app as fastapi_app
    return fastapi_app


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def db_session():
    from database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def register_user(client):
    """회원가입 + 로그인까지 마친 사용자 정보를 돌려주는 팩토리 픽스처."""

    def _register(prefix: str = "user"):
        username = f"{prefix}_{uuid.uuid4().hex[:8]}"
        reg = client.post(
            "/api/register",
            json={"username": username, "password": "pass1234", "name": prefix},
        )
        assert reg.status_code == 201, reg.text
        user_id = reg.json()["id"]

        login = client.post(
            "/api/login",
            json={"username": username, "password": "pass1234"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]

        return {
            "id": user_id,
            "username": username,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    return _register
