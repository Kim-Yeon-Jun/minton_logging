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

class GameParticipantInput(BaseModel):
    user_id: str
    team_color: str
    score: int = 0

class GameCreateRequest(BaseModel):
    group_key: str
    game_type: str = "doubles"
    court_number: int | None = None
    participants: list[GameParticipantInput]

class GameUpdateRequest(BaseModel):
    game_type: str = "doubles"
    court_number: int | None = None
    participants: list[GameParticipantInput]

class GameParticipantResponse(BaseModel):
    user_id: str
    username: str
    name: str | None = None
    team_color: str
    score: int
    is_winner: bool | None = None

class GameResponse(BaseModel):
    game_id: str
    group_key: str
    game_type: str
    game_status: str
    court_number: int | None = None
    played_at: str
    created_at: str
    deleted_at: str | None = None
    participants: list[GameParticipantResponse] = []

class GameListResponse(BaseModel):
    items: list[GameResponse]
    total: int


# --- Helpers ---

def _build_game_response(db: Session, game: Game) -> GameResponse:
    participants = db.query(GameParticipant).filter(GameParticipant.game_id == game.game_id).all()
    participant_responses = []
    for p in participants:
        user = db.query(User).filter(User.id == p.user_id).first()
        participant_responses.append(GameParticipantResponse(
            user_id=p.user_id,
            username=user.login_id if user else p.user_id,
            name=user.name if user else None,
            team_color=p.team_color,
            score=p.score,
            is_winner=p.is_winner
        ))

    return GameResponse(
        game_id=game.game_id,
        group_key=game.group_key,
        game_type=game.game_type,
        game_status=game.game_status,
        court_number=game.court_number,
        played_at=game.played_at.isoformat(),
        created_at=game.created_at.isoformat(),
        deleted_at=game.deleted_at.isoformat() if game.deleted_at else None,
        participants=participant_responses
    )


def _validate_participants(db: Session, group_key: str, participants: list[GameParticipantInput]) -> dict[str, int]:
    if len(participants) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 2명 이상의 참가자가 필요합니다."
        )

    team_scores: dict[str, int] = {}
    for p in participants:
        member = db.query(GroupMember).filter(
            GroupMember.group_key == group_key,
            GroupMember.user_id == p.user_id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"해당 그룹의 멤버가 아닌 참가자가 포함되어 있습니다. (user_id: {p.user_id})"
            )
        if p.team_color in team_scores and team_scores[p.team_color] != p.score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="같은 팀 참가자의 점수가 일치하지 않습니다."
            )
        team_scores[p.team_color] = p.score

    if len(team_scores) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 두 팀 이상 배정되어야 합니다."
        )

    return team_scores


def _compute_winners(team_scores: dict[str, int]) -> tuple[list[str], bool]:
    max_score = max(team_scores.values())
    winning_teams = [team for team, score in team_scores.items() if score == max_score]
    is_draw = len(winning_teams) == len(team_scores)
    return winning_teams, is_draw


def _get_game_or_404(db: Session, game_id: str) -> Game:
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 경기입니다."
        )
    return game


# --- API Endpoints ---

@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    request: GameCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """그룹 내 경기 기록을 등록합니다."""
    group = db.query(Group).filter(Group.group_key == request.group_key, Group.is_active == True).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않거나 비활성화된 그룹입니다."
        )

    assert_group_member(db, request.group_key, current_user.id)

    team_scores = _validate_participants(db, request.group_key, request.participants)
    winning_teams, is_draw = _compute_winners(team_scores)

    new_game = Game(
        game_id=str(uuid.uuid4()),
        group_key=request.group_key,
        game_type=request.game_type,
        court_number=request.court_number,
        played_at=datetime.utcnow()
    )
    db.add(new_game)
    db.flush()

    for p in request.participants:
        db.add(GameParticipant(
            game_id=new_game.game_id,
            user_id=p.user_id,
            team_color=p.team_color,
            score=p.score,
            is_winner=None if is_draw else (p.team_color in winning_teams)
        ))

    db.commit()
    db.refresh(new_game)

    return _build_game_response(db, new_game)


@router.get("/games/group/{group_key}", response_model=GameListResponse)
def get_group_games(
    group_key: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 그룹의 경기 이력을 최신순으로 조회합니다 (삭제 예정 경기는 제외)."""
    assert_group_member(db, group_key, current_user.id)

    base_query = db.query(Game).filter(Game.group_key == group_key, Game.is_deleted == False)
    total = base_query.count()
    games = base_query.order_by(Game.played_at.desc()).offset(offset).limit(limit).all()

    return GameListResponse(items=[_build_game_response(db, g) for g in games], total=total)


@router.get("/games/group/{group_key}/trash", response_model=GameListResponse)
def get_group_games_trash(
    group_key: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 그룹의 삭제 예정 경기 목록을 조회합니다."""
    assert_group_member(db, group_key, current_user.id)

    base_query = db.query(Game).filter(Game.group_key == group_key, Game.is_deleted == True)
    total = base_query.count()
    games = base_query.order_by(Game.deleted_at.desc()).offset(offset).limit(limit).all()

    return GameListResponse(items=[_build_game_response(db, g) for g in games], total=total)


@router.get("/games/{game_id}", response_model=GameResponse)
def get_game_detail(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 경기의 상세 정보를 조회합니다."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)
    return _build_game_response(db, game)


@router.put("/games/{game_id}", response_model=GameResponse)
def update_game(
    game_id: str,
    request: GameUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """경기 기록을 수정합니다 (그룹 멤버 누구나 가능)."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태의 경기는 수정할 수 없습니다. 먼저 복구해 주세요."
        )

    team_scores = _validate_participants(db, game.group_key, request.participants)
    winning_teams, is_draw = _compute_winners(team_scores)

    db.query(GameParticipant).filter(GameParticipant.game_id == game_id).delete()

    game.game_type = request.game_type
    game.court_number = request.court_number

    for p in request.participants:
        db.add(GameParticipant(
            game_id=game_id,
            user_id=p.user_id,
            team_color=p.team_color,
            score=p.score,
            is_winner=None if is_draw else (p.team_color in winning_teams)
        ))

    db.commit()
    db.refresh(game)

    return _build_game_response(db, game)


@router.delete("/games/{game_id}")
def delete_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """경기 기록을 삭제 예정 목록으로 이동합니다 (소프트 삭제, 그룹 멤버 누구나 가능)."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 삭제 예정 상태입니다."
        )

    game.is_deleted = True
    game.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "경기가 삭제 예정 목록으로 이동했습니다."}


@router.post("/games/{game_id}/restore")
def restore_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """삭제 예정 경기를 복구합니다 (그룹 멤버 누구나 가능)."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if not game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태가 아닙니다."
        )

    game.is_deleted = False
    game.deleted_at = None
    db.commit()

    return {"message": "경기가 복구되었습니다."}


@router.delete("/games/{game_id}/permanent")
def permanent_delete_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """삭제 예정 상태의 경기를 영구적으로 삭제합니다 (그룹 멤버 누구나 가능)."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if not game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태의 경기만 영구 삭제할 수 있습니다."
        )

    db.delete(game)
    db.commit()

    return {"message": "경기 기록이 영구적으로 삭제되었습니다."}
