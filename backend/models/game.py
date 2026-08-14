import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from database import Base
from timeutil import now_kst


class Game(Base):
    __tablename__ = "bd_game_mt"

    game_id = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_key = Column(String(40), ForeignKey("bd_grp_mt.group_key", ondelete="CASCADE"), nullable=False)
    game_type = Column(String(20), default="doubles")
    game_status = Column(String(20), default="finished")
    court_number = Column(Integer, nullable=True)
    played_at = Column(DateTime, default=now_kst)
    created_at = Column(DateTime, default=now_kst)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    video_url = Column(String(500), nullable=True)


class GameParticipant(Base):
    __tablename__ = "bd_game_usr_map"

    game_id = Column(String(40), ForeignKey("bd_game_mt.game_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE"), primary_key=True)
    team_color = Column(String(10), nullable=False)
    score = Column(Integer, default=0)
    is_winner = Column(Boolean, nullable=True)


class GameComment(Base):
    __tablename__ = "bd_game_comment_mt"

    comment_id = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(40), ForeignKey("bd_game_mt.game_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=now_kst)
    updated_at = Column(DateTime, default=now_kst, onupdate=now_kst)


class GameLike(Base):
    __tablename__ = "bd_game_like_map"

    game_id = Column(String(40), ForeignKey("bd_game_mt.game_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=now_kst)
