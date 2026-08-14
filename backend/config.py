import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    SERVER_PORT: int = int(os.getenv("SEVER_PORT", os.getenv("SERVER_PORT", "8080")))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "localhost")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "BD_LOG")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "yjkim")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "kk1234kk")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_SCHEMA: str = os.getenv("DATABASE_SCHEMA", "BD_MAIN")

    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-only-insecure-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", str(60 * 24 * 7)))  # 7일

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_URL}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

settings = Settings()
