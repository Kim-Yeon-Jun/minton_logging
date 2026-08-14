import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.group import Group, GroupMember
from models.game import Game, GameParticipant
from permissions import assert_group_member
from security import get_current_user

router = APIRouter()

# --- Pydantic Schemas ---

class GroupCreateRequest(BaseModel):
    group_name: str
    description: str | None = None

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
    role: str = "member"

class MyRecordResponse(BaseModel):
    wins: int
    losses: int
    draws: int
    win_rate: float

class HeadToHeadResponse(BaseModel):
    opponent_id: str
    opponent_name: str
    wins: int
    losses: int

class MonthlyTrendResponse(BaseModel):
    month: str
    games: int
    wins: int

class MonthlyLeaderResponse(BaseModel):
    user_id: str
    name: str
    wins: int
    losses: int
    draws: int
    win_rate: float
    score_diff: int

class GroupStatsResponse(BaseModel):
    my_record: MyRecordResponse
    head_to_head: list[HeadToHeadResponse]
    monthly_trend: list[MonthlyTrendResponse]
    monthly_best: MonthlyLeaderResponse | None = None
    monthly_worst: MonthlyLeaderResponse | None = None


# --- API Endpoints ---

@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    request: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새로운 그룹(동호회/모임)을 생성합니다."""
    new_group = Group(
        group_key=str(uuid.uuid4()),
        group_name=request.group_name,
        description=request.description,
        owner_id=current_user.id
    )
    db.add(new_group)
    db.flush()

    # 생성자를 그룹 관리자(admin) 멤버로 등록
    owner_member = GroupMember(
        group_key=new_group.group_key,
        user_id=current_user.id,
        role="admin"
    )
    db.add(owner_member)

    # 사용자의 대표 그룹 키가 지정되지 않았다면 현재 그룹으로 설정
    if not current_user.group_key:
        current_user.group_key = new_group.group_key

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
def get_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
def get_user_groups(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
def get_group_detail(
    group_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
def join_group(
    group_key: str,
    request: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자를 그룹에 가입시킵니다."""
    group = db.query(Group).filter(Group.group_key == group_key, Group.is_active == True).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 그룹입니다."
        )

    existing_member = db.query(GroupMember).filter(
        GroupMember.group_key == group_key,
        GroupMember.user_id == current_user.id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 그룹입니다."
        )

    new_member = GroupMember(
        group_key=group_key,
        user_id=current_user.id,
        role=request.role
    )
    db.add(new_member)

    # 사용자의 대표 그룹 키가 없는 경우 가입한 그룹으로 변경
    if not current_user.group_key:
        current_user.group_key = group_key

    db.commit()

    return {"message": f"'{group.group_name}' 그룹에 성공적으로 가입했습니다.", "group_key": group_key}


@router.post("/groups/{group_key}/leave")
def leave_group(
    group_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자가 그룹을 탈퇴합니다."""
    member = db.query(GroupMember).filter(
        GroupMember.group_key == group_key,
        GroupMember.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 그룹의 멤버가 아닙니다."
        )

    db.delete(member)

    # 대표 그룹 키 삭제 처리 (동일한 경우)
    if current_user.group_key == group_key:
        # 다른 속한 그룹이 있다면 첫 번째 그룹으로 변경, 없으면 None
        remaining = db.query(GroupMember).filter(GroupMember.user_id == current_user.id).first()
        current_user.group_key = remaining.group_key if remaining else None

    db.commit()

    return {"message": "그룹에서 탈퇴했습니다."}


def _compute_monthly_leaders(
    db: Session, group_key: str, year_month: str
) -> tuple["MonthlyLeaderResponse | None", "MonthlyLeaderResponse | None"]:
    """해당 년월(year_month)의 그룹원별 승률/득실차를 계산해 베스트·워스트를 반환합니다."""
    year, month = (int(part) for part in year_month.split("-"))
    month_start = datetime(year, month, 1)
    month_end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    month_games = db.query(Game).filter(
        Game.group_key == group_key,
        Game.is_deleted == False,
        Game.played_at >= month_start,
        Game.played_at < month_end
    ).all()
    month_game_ids = [g.game_id for g in month_games]

    month_participants = []
    if month_game_ids:
        month_participants = db.query(GameParticipant).filter(
            GameParticipant.game_id.in_(month_game_ids)
        ).all()

    participants_by_game: dict[str, list[GameParticipant]] = {}
    for p in month_participants:
        participants_by_game.setdefault(p.game_id, []).append(p)

    member_stats: dict[str, dict[str, int]] = {}

    for game in month_games:
        game_participants = participants_by_game.get(game.game_id, [])
        for p in game_participants:
            stat = member_stats.setdefault(p.user_id, {"wins": 0, "losses": 0, "draws": 0, "score_diff": 0})
            opponents = [o for o in game_participants if o.team_color != p.team_color]
            opp_score = opponents[0].score if opponents else 0
            stat["score_diff"] += p.score - opp_score

            if p.is_winner is True:
                stat["wins"] += 1
            elif p.is_winner is False:
                stat["losses"] += 1
            else:
                stat["draws"] += 1

    if not member_stats:
        return None, None

    user_ids = list(member_stats.keys())
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    ranked = []
    for user_id, stat in member_stats.items():
        total_decided = stat["wins"] + stat["losses"]
        win_rate = round(stat["wins"] / total_decided * 100, 1) if total_decided > 0 else 0.0
        user = users.get(user_id)
        ranked.append(MonthlyLeaderResponse(
            user_id=user_id,
            name=(user.name or user.login_id) if user else user_id,
            wins=stat["wins"],
            losses=stat["losses"],
            draws=stat["draws"],
            win_rate=win_rate,
            score_diff=stat["score_diff"]
        ))

    ranked_best = sorted(ranked, key=lambda r: (r.win_rate, r.score_diff), reverse=True)
    best = ranked_best[0]
    worst = sorted(ranked, key=lambda r: (r.win_rate, r.score_diff))[0] if len(ranked) > 1 else None

    return best, worst


@router.get("/groups/{group_key}/stats", response_model=GroupStatsResponse)
def get_group_stats(
    group_key: str,
    year_month: str | None = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM. 지정 시 해당 월의 베스트/워스트 전적을 함께 반환합니다."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """로그인한 사용자의 그룹 내 개인 전적/상대 전적/월별 추이를 조회합니다."""
    assert_group_member(db, group_key, current_user.id)

    games = db.query(Game).filter(Game.group_key == group_key, Game.is_deleted == False).all()
    game_ids = [g.game_id for g in games]

    participants = []
    if game_ids:
        participants = db.query(GameParticipant).filter(GameParticipant.game_id.in_(game_ids)).all()

    participants_by_game: dict[str, list[GameParticipant]] = {}
    for p in participants:
        participants_by_game.setdefault(p.game_id, []).append(p)

    wins = losses = draws = 0
    head_to_head: dict[str, dict[str, int]] = {}
    monthly: dict[str, dict[str, int]] = {}

    for game in games:
        game_participants = participants_by_game.get(game.game_id, [])
        me = next((p for p in game_participants if p.user_id == current_user.id), None)
        if not me:
            continue

        month_key = game.played_at.strftime("%Y-%m")
        month_bucket = monthly.setdefault(month_key, {"games": 0, "wins": 0})
        month_bucket["games"] += 1

        if me.is_winner is True:
            wins += 1
            month_bucket["wins"] += 1
        elif me.is_winner is False:
            losses += 1
        else:
            draws += 1

        opponents = [p for p in game_participants if p.team_color != me.team_color]
        for opp in opponents:
            record = head_to_head.setdefault(opp.user_id, {"wins": 0, "losses": 0})
            if me.is_winner is True:
                record["wins"] += 1
            elif me.is_winner is False:
                record["losses"] += 1

    total_decided = wins + losses
    win_rate = round(wins / total_decided * 100, 1) if total_decided > 0 else 0.0

    opponent_ids = list(head_to_head.keys())
    opponent_users: dict[str, User] = {}
    if opponent_ids:
        for u in db.query(User).filter(User.id.in_(opponent_ids)).all():
            opponent_users[u.id] = u

    head_to_head_list = []
    for opponent_id, record in head_to_head.items():
        opponent = opponent_users.get(opponent_id)
        head_to_head_list.append(HeadToHeadResponse(
            opponent_id=opponent_id,
            opponent_name=(opponent.name or opponent.login_id) if opponent else opponent_id,
            wins=record["wins"],
            losses=record["losses"]
        ))
    head_to_head_list.sort(key=lambda h: h.wins + h.losses, reverse=True)

    monthly_trend = [
        MonthlyTrendResponse(month=month, games=bucket["games"], wins=bucket["wins"])
        for month, bucket in sorted(monthly.items())
    ][-6:]

    monthly_best = monthly_worst = None
    if year_month:
        monthly_best, monthly_worst = _compute_monthly_leaders(db, group_key, year_month)

    return GroupStatsResponse(
        my_record=MyRecordResponse(wins=wins, losses=losses, draws=draws, win_rate=win_rate),
        head_to_head=head_to_head_list,
        monthly_trend=monthly_trend,
        monthly_best=monthly_best,
        monthly_worst=monthly_worst
    )
