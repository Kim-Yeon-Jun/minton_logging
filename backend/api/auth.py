import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str | None = None
    login_id: str | None = None
    password: str | None = None
    login_pw: str | None = None
    name: str | None = None
    group_key: str | None = None

    def get_login_id(self) -> str:
        return self.login_id or self.username or ""

    def get_login_pw(self) -> str:
        return self.login_pw or self.password or ""

class RegisterResponse(BaseModel):
    message: str
    id: str
    username: str
    login_id: str
    name: str | None = None
    group_key: str | None = None

class LoginRequest(BaseModel):
    username: str | None = None
    login_id: str | None = None
    password: str | None = None
    login_pw: str | None = None

    def get_login_id(self) -> str:
        return self.login_id or self.username or ""

    def get_login_pw(self) -> str:
        return self.login_pw or self.password or ""

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    id: str
    username: str
    login_id: str
    name: str | None = None
    group_key: str | None = None

class MeResponse(BaseModel):
    id: str
    username: str
    login_id: str
    name: str | None = None
    group_key: str | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    message: str

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    req_login_id = request.get_login_id()
    req_login_pw = request.get_login_pw()

    if not req_login_id or not req_login_pw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="아이디와 비밀번호를 모두 입력해 주세요."
        )

    existing_user = db.query(User).filter(User.login_id == req_login_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 아이디입니다."
        )

    new_user = User(
        id=str(uuid.uuid4()),
        login_id=req_login_id,
        login_pw=hash_password(req_login_pw),
        name=request.name,
        group_key=request.group_key
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RegisterResponse(
        message="회원가입이 완료되었습니다.",
        id=new_user.id,
        username=new_user.login_id,
        login_id=new_user.login_id,
        name=new_user.name,
        group_key=new_user.group_key
    )

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    req_login_id = request.get_login_id()
    req_login_pw = request.get_login_pw()

    user = db.query(User).filter(User.login_id == req_login_id).first()

    if not user or not verify_password(req_login_pw, user.login_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다."
        )

    access_token = create_access_token(user.id)

    return LoginResponse(
        message="로그인 성공",
        access_token=access_token,
        id=user.id,
        username=user.login_id,
        login_id=user.login_id,
        name=user.name,
        group_key=user.group_key
    )

@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        id=current_user.id,
        username=current_user.login_id,
        login_id=current_user.login_id,
        name=current_user.name,
        group_key=current_user.group_key
    )

@router.put("/users/me/password", response_model=ChangePasswordResponse)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.current_password, current_user.login_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 일치하지 않습니다."
        )

    if not request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호를 입력해 주세요."
        )

    current_user.login_pw = hash_password(request.new_password)
    db.commit()

    return ChangePasswordResponse(message="비밀번호가 변경되었습니다.")
