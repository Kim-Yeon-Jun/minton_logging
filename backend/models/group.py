import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Group(Base):
    __tablename__ = "bd_grp_mt"

    group_key = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id])
    memberships = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "bd_grp_usr_map"

    group_key = Column(String(40), ForeignKey("bd_grp_mt.group_key", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(20), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="memberships")
    user = relationship("User")
