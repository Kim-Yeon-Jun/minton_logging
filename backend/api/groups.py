import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.group import Group, GroupMember

router = APIRouter()

# --- Pydantic Schemas ---

class GroupCreateRequest(BaseModel):
    group_name: str
    description: str | None = None
    owner_id: str

class GroupResponse(BaseModel):
    group_key: str
    group_name: str
    description: str | None = None
    owner_id: str | None = None
    member_count: int = 0
    created_at: str

class GroupMemberResponse(BaseModel):
    user_id: str
    username: str
    name: str | None = None
    role: str
    joined_at: str

class GroupDetailResponse(BaseModel):
    group_key: str
    group_name: str
    description: str | None = None
    owner_id: str | None = None
    created_at: str
    members: list[GroupMemberResponse] = []

class GroupJoinRequest(BaseModel):
    user_id: str
    role: str = "member"

class GroupLeaveRequest(BaseModel):
    user_id: str


# --- API Endpoints ---

@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(request: GroupCreateRequest, db: Session = Depends(get_db)):
    """새로운 그룹(동호회/모임)을 생성합니다."""
    owner = db.query(User).filter(User.id == request.owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자입니다."
        )

    new_group = Group(
        group_key=str(uuid.uuid4()),
        group_name=request.group_name,
        description=request.description,
        owner_id=request.owner_id
    )
    db.add(new_group)
    db.flush()

    # 생성자를 그룹 관리자(admin) 멤버로 등록
    owner_member = GroupMember(
        group_key=new_group.group_key,
        user_id=request.owner_id,
        role="admin"
    )
    db.add(owner_member)

    # 사용자의 대표 그룹 키가 지정되지 않았다면 현재 그룹으로 설정
    if not owner.group_key:
        owner.group_key = new_group.group_key

    db.commit()
    db.refresh(new_group)

    return GroupResponse(
        group_key=new_group.group_key,
        group_name=new_group.group_name,
        description=new_group.description,
        owner_id=new_group.owner_id,
        member_count=1,
        created_at=new_group.created_at.isoformat()
    )


@router.get("/groups", response_model=list[GroupResponse])
def get_groups(db: Session = Depends(get_db)):
    """활성화된 전체 그룹 목록을 조회합니다."""
    groups = db.query(Group).filter(Group.is_active == True).all()
    result = []
    for g in groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_key == g.group_key).count()
        result.append(GroupResponse(
            group_key=g.group_key,
            group_name=g.group_name,
            description=g.description,
            owner_id=g.owner_id,
            member_count=member_count,
            created_at=g.created_at.isoformat()
        ))
    return result


@router.get("/groups/user/{user_id}", response_model=list[GroupResponse])
def get_user_groups(user_id: str, db: Session = Depends(get_db)):
    """특정 사용자가 가입한 그룹 목록을 조회합니다."""
    memberships = db.query(GroupMember).filter(GroupMember.user_id == user_id).all()
    group_keys = [m.group_key for m in memberships]
    groups = db.query(Group).filter(Group.group_key.in_(group_keys), Group.is_active == True).all()

    result = []
    for g in groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_key == g.group_key).count()
        result.append(GroupResponse(
            group_key=g.group_key,
            group_name=g.group_name,
            description=g.description,
            owner_id=g.owner_id,
            member_count=member_count,
            created_at=g.created_at.isoformat()
        ))
    return result


@router.get("/groups/{group_key}", response_model=GroupDetailResponse)
def get_group_detail(group_key: str, db: Session = Depends(get_db)):
    """특정 그룹의 상세 정보 및 멤버 목록을 조회합니다."""
    group = db.query(Group).filter(Group.group_key == group_key, Group.is_active == True).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않거나 비활성화된 그룹입니다."
        )

    memberships = db.query(GroupMember).filter(GroupMember.group_key == group_key).all()
    member_responses = []
    for m in memberships:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            member_responses.append(GroupMemberResponse(
                user_id=user.id,
                username=user.login_id,
                name=user.name,
                role=m.role,
                joined_at=m.joined_at.isoformat()
            ))

    return GroupDetailResponse(
        group_key=group.group_key,
        group_name=group.group_name,
        description=group.description,
        owner_id=group.owner_id,
        created_at=group.created_at.isoformat(),
        members=member_responses
    )


@router.post("/groups/{group_key}/join")
def join_group(group_key: str, request: GroupJoinRequest, db: Session = Depends(get_db)):
    """사용자를 그룹에 가입시킵니다."""
    group = db.query(Group).filter(Group.group_key == group_key, Group.is_active == True).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 그룹입니다."
        )

    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자입니다."
        )

    existing_member = db.query(GroupMember).filter(
        GroupMember.group_key == group_key,
        GroupMember.user_id == request.user_id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 그룹입니다."
        )

    new_member = GroupMember(
        group_key=group_key,
        user_id=request.user_id,
        role=request.role
    )
    db.add(new_member)

    # 사용자의 대표 그룹 키가 없는 경우 가입한 그룹으로 변경
    if not user.group_key:
        user.group_key = group_key

    db.commit()

    return {"message": f"'{group.group_name}' 그룹에 성공적으로 가입했습니다.", "group_key": group_key}


@router.post("/groups/{group_key}/leave")
def leave_group(group_key: str, request: GroupLeaveRequest, db: Session = Depends(get_db)):
    """사용자가 그룹을 탈퇴합니다."""
    member = db.query(GroupMember).filter(
        GroupMember.group_key == group_key,
        GroupMember.user_id == request.user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 그룹의 멤버가 아닙니다."
        )

    db.delete(member)

    # 대표 그룹 키 삭제 처리 (동일한 경우)
    user = db.query(User).filter(User.id == request.user_id).first()
    if user and user.group_key == group_key:
        # 다른 속한 그룹이 있다면 첫 번째 그룹으로 변경, 없으면 None
        remaining = db.query(GroupMember).filter(GroupMember.user_id == request.user_id).first()
        user.group_key = remaining.group_key if remaining else None

    db.commit()

    return {"message": "그룹에서 탈퇴했습니다."}
