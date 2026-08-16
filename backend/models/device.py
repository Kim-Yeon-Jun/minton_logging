from sqlalchemy import Column, DateTime, ForeignKey, String
from database import Base
from timeutil import now_kst


class DeviceAuthCode(Base):
    """워치처럼 텍스트 입력이 불편한 기기를 페어링하기 위한 1회용 인증 코드.

    OAuth 2.0 Device Authorization Grant(RFC 8628)와 같은 흐름: 기기가 이
    레코드를 만들어 user_code를 화면에 띄우고, 이미 로그인된 사용자가
    웹/폰에서 그 코드를 입력해 승인하면, 기기는 폴링 중이던 device_code로
    access_token을 받아간다.
    """
    __tablename__ = "bd_device_auth_mt"

    device_code = Column(String(64), primary_key=True)
    user_code = Column(String(10), nullable=False, unique=True)
    status = Column(String(20), default="pending")
    user_id = Column(String(40), ForeignKey("bd_usr_mt.id", ondelete="CASCADE", name="fk_device_auth_user"), nullable=True)
    device_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=now_kst)
    expires_at = Column(DateTime, nullable=False)
