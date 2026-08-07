import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

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
    id: str
    username: str
    login_id: str
    name: str | None = None
    group_key: str | None = None

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
        login_pw=req_login_pw,
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
    
    if not user or user.login_pw != req_login_pw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다."
        )

    return LoginResponse(
        message="로그인 성공",
        id=user.id,
        username=user.login_id,
        login_id=user.login_id,
        name=user.name,
        group_key=user.group_key
    )

