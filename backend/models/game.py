import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from database import Base


class Game(Base):
    __tablename__ = "bd_game_mt"

    game_id = Column(String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_key = Column(String(40), ForeignKey("bd_grp_mt.group_key", ondelete="CASCADE"), nullable=False)
    game_type = Column(String(20), default="doubles")
    game_status = Column(String(20), default="finished")
    court_number = Column(Integer, nullable=True)
    played_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)


class GameParticipant(Base):
    __tablename__ = "bd_game_usr_map"

    game_id = Column(String(40), ForeignKey("bd_game_mt.game_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE"), primary_key=True)
    team_color = Column(String(10), nullable=False)
    score = Column(Integer, default=0)
    is_winner = Column(Boolean, nullable=True)
