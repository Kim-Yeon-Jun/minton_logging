"""1회성 마이그레이션: 평문으로 저장된 기존 비밀번호를 bcrypt 해시로 변환합니다.

이미 bcrypt 해시 형식($2b$/$2a$/$2y$)인 값은 건드리지 않으므로 여러 번 실행해도 안전합니다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import SessionLocal
from models.user import User
from security import hash_password


def is_bcrypt_hash(value: str) -> bool:
    return value.startswith(("$2b$", "$2a$", "$2y$"))


def main():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        migrated = 0
        for user in users:
            if not is_bcrypt_hash(user.login_pw):
                user.login_pw = hash_password(user.login_pw)
                migrated += 1
        db.commit()
        print(f"총 {len(users)}명 중 {migrated}명의 비밀번호를 해싱했습니다.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
