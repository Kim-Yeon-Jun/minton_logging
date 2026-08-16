import secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.device import DeviceAuthCode
from models.user import User
from security import create_access_token, get_current_user
from timeutil import now_kst

router = APIRouter()

CODE_TTL_MINUTES = 10
DEVICE_CODE_ENTROPY_BYTES = 32

# --- Pydantic Schemas ---

class DeviceCodeRequest(BaseModel):
    device_name: str | None = None

class DeviceCodeResponse(BaseModel):
    device_code: str
    user_code: str
    expires_in: int

class DeviceApproveRequest(BaseModel):
    user_code: str

class DeviceApproveResponse(BaseModel):
    message: str
    device_name: str | None = None

class DeviceTokenRequest(BaseModel):
    device_code: str

class DeviceTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: str
    username: str
    name: str | None = None
    group_key: str | None = None


# --- Helpers ---

def _generate_user_code(db: Session) -> str:
    """워치 화면에 띄울 6자리 숫자 코드를 생성합니다 (겹치면 재시도)."""
    for _ in range(5):
        code = f"{secrets.randbelow(1_000_000):06d}"
        if not db.query(DeviceAuthCode).filter(DeviceAuthCode.user_code == code).first():
            return code
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="코드 발급에 실패했습니다. 잠시 후 다시 시도해 주세요."
    )


# --- API Endpoints ---
# 워치 등 신뢰할 수 없는 입력 수단을 가진 기기를 페어링하는 3단계 흐름:
#   1) POST /device/code    - 기기가 로그인 없이 코드 한 쌍을 발급받는다 (device_code는 기기만, user_code는 화면에 표시)
#   2) POST /device/approve - 이미 로그인된 사용자가 웹/폰에서 user_code를 입력해 승인한다
#   3) POST /device/token   - 기기가 device_code로 폴링하다가 승인되면 access_token을 받는다

@router.post("/device/code", response_model=DeviceCodeResponse, status_code=status.HTTP_201_CREATED)
def create_device_code(request: DeviceCodeRequest, db: Session = Depends(get_db)):
    """워치 등 기기가 페어링을 시작할 때 호출합니다 (로그인 불필요)."""
    db.query(DeviceAuthCode).filter(DeviceAuthCode.expires_at < now_kst()).delete()

    user_code = _generate_user_code(db)
    record = DeviceAuthCode(
        device_code=secrets.token_urlsafe(DEVICE_CODE_ENTROPY_BYTES),
        user_code=user_code,
        device_name=request.device_name,
        expires_at=now_kst() + timedelta(minutes=CODE_TTL_MINUTES)
    )
    db.add(record)
    db.commit()

    return DeviceCodeResponse(
        device_code=record.device_code,
        user_code=record.user_code,
        expires_in=CODE_TTL_MINUTES * 60
    )


@router.post("/device/approve", response_model=DeviceApproveResponse)
def approve_device_code(
    request: DeviceApproveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이미 로그인된 사용자가 기기 화면에 뜬 user_code를 입력해 연결을 승인합니다."""
    record = db.query(DeviceAuthCode).filter(DeviceAuthCode.user_code == request.user_code).first()
    if not record or record.expires_at < now_kst():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않거나 만료된 코드입니다."
        )
    if record.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 승인된 코드입니다."
        )

    record.status = "approved"
    record.user_id = current_user.id
    db.commit()

    return DeviceApproveResponse(message="기기 연결을 승인했습니다.", device_name=record.device_name)


@router.post("/device/token", response_model=DeviceTokenResponse)
def issue_device_token(request: DeviceTokenRequest, db: Session = Depends(get_db)):
    """기기가 승인 여부를 확인하려고 주기적으로(polling) 호출합니다."""
    record = db.query(DeviceAuthCode).filter(DeviceAuthCode.device_code == request.device_code).first()
    if not record or record.expires_at < now_kst():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="expired_code")
    if record.status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="authorization_pending")

    user = db.query(User).filter(User.id == record.user_id).first()
    db.delete(record)
    if not user:
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="expired_code")

    access_token = create_access_token(user.id)
    db.commit()

    return DeviceTokenResponse(
        access_token=access_token,
        id=user.id,
        username=user.login_id,
        name=user.name,
        group_key=user.group_key
    )
