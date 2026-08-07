import uuid
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "bd_usr_mt"

    id = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    login_id = Column(String(40), unique=True, index=True, nullable=False)
    login_pw = Column(String(255), nullable=False)
    group_key = Column(String(40), nullable=True)
    name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

