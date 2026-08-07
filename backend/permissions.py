from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.group import GroupMember


def assert_group_member(db: Session, group_key: str, user_id: str) -> GroupMember:
    """user_id가 group_key 그룹의 멤버인지 확인합니다. 아니면 403."""
    member = db.query(GroupMember).filter(
        GroupMember.group_key == group_key,
        GroupMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 그룹의 멤버만 접근할 수 있습니다."
        )

    return member
