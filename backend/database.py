from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"options": f"-csearch_path={settings.DATABASE_SCHEMA},public"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=MetaData(schema=settings.DATABASE_SCHEMA))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
