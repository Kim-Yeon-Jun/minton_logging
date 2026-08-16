import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Group(Base):
    __tablename__ = "bd_grp_mt"
    # Names/columns here are pinned to match the live DB (built from the
    # out-of-repo create_table.sql, not create_all()'s auto-naming) so that
    # `alembic revision --autogenerate` doesn't flag legacy objects as diffs.
    __table_args__ = (Index("idx_grp_name", "group_name"),)

    group_key = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="SET NULL", name="fk_grp_owner"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id])
    memberships = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "bd_grp_usr_map"
    __table_args__ = (Index("idx_map_user_id", "user_id"),)

    group_key = Column(String(40), ForeignKey("bd_grp_mt.group_key", ondelete="CASCADE", name="fk_map_group"), primary_key=True)
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE", name="fk_map_user"), primary_key=True)
    role = Column(String(20), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="memberships")
    user = relationship("User")
