import uuid
from sqlalchemy import Boolean, Column, String, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "bd_usr_mt"

    id = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    # unique=True alone (no index=True) matches the live DB, which only has
    # the inline UNIQUE constraint (auto-named bd_usr_mt_login_id_key) and no
    # separate index -- keeps `alembic revision --autogenerate` quiet.
    login_id = Column(String(40), unique=True, nullable=False)
    login_pw = Column(String(255), nullable=False)
    group_key = Column(String(40), nullable=True)
    name = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

