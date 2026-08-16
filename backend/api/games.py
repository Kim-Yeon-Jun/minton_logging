import uuid
from datetime import datetime
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.group import Group, GroupMember
from models.game import Game, GameComment, GameLike, GameParticipant
from permissions import assert_group_member
from security import get_current_user
from timeutil import now_kst

router = APIRouter()

# --- Pydantic Schemas ---

ALLOWED_VIDEO_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
    "vimeo.com", "www.vimeo.com",
    "tv.naver.com", "video.naver.com",
}

ALLOWED_GAME_STATUSES = {"scheduled", "in_progress", "finished"}

class GameParticipantInput(BaseModel):
    user_id: str
    team_color: str
    score: int = 0

class GameCreateRequest(BaseModel):
    group_key: str
    game_type: str = "doubles"
    # 기존 클라이언트(웹)는 이 필드를 보내지 않으므로 기본값 "finished"로
    # 과거 동작을 그대로 유지한다. 워치 등에서 실시간 기록을 시작할 때만
    # "in_progress"로 명시해서 생성한다.
    game_status: str = "finished"
    court_number: int | None = None
    video_url: str | None = None
    played_at: str | None = None
    participants: list[GameParticipantInput]

class GameStatusUpdateRequest(BaseModel):
    game_status: str

class TeamScoreUpdateRequest(BaseModel):
    score: int = Field(ge=0)

class GameUpdateRequest(BaseModel):
    game_type: str = "doubles"
    court_number: int | None = None
    video_url: str | None = None
    played_at: str | None = None
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
    video_url: str | None = None
    played_at: str
    created_at: str
    deleted_at: str | None = None
    participants: list[GameParticipantResponse] = []
    comment_count: int = 0
    like_count: int = 0
    liked_by_me: bool = False

class GameListResponse(BaseModel):
    items: list[GameResponse]
    total: int

class CommentCreateRequest(BaseModel):
    content: str

class CommentUpdateRequest(BaseModel):
    content: str

class CommentResponse(BaseModel):
    comment_id: str
    game_id: str
    user_id: str
    username: str
    name: str | None = None
    content: str
    created_at: str
    updated_at: str

class LikeActionResponse(BaseModel):
    message: str
    like_count: int


# --- Helpers ---

def _parse_played_at(played_at: str | None) -> datetime:
    """KST 벽시계 기준으로 해석합니다. 값이 없으면 현재 KST 시각을 사용합니다."""
    if not played_at:
        return now_kst()

    try:
        return datetime.fromisoformat(played_at)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="경기 일시 형식이 올바르지 않습니다."
        )


def _validate_game_status(game_status: str) -> str:
    if game_status not in ALLOWED_GAME_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"경기 상태는 {sorted(ALLOWED_GAME_STATUSES)} 중 하나여야 합니다."
        )
    return game_status


def _validate_video_url(video_url: str | None) -> str | None:
    if not video_url:
        return None

    parsed = urlparse(video_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 형식의 URL이 아닙니다."
        )

    if parsed.netloc.lower() not in ALLOWED_VIDEO_HOSTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원하지 않는 동영상 사이트입니다. (유튜브, 비메오, 네이버TV만 등록 가능합니다.)"
        )

    return video_url


def _build_game_response(db: Session, game: Game, current_user_id: str) -> GameResponse:
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

    comment_count = db.query(GameComment).filter(GameComment.game_id == game.game_id).count()
    like_count = db.query(GameLike).filter(GameLike.game_id == game.game_id).count()
    liked_by_me = db.query(GameLike).filter(
        GameLike.game_id == game.game_id,
        GameLike.user_id == current_user_id
    ).first() is not None

    return GameResponse(
        game_id=game.game_id,
        group_key=game.group_key,
        game_type=game.game_type,
        game_status=game.game_status,
        court_number=game.court_number,
        video_url=game.video_url,
        played_at=game.played_at.isoformat(),
        created_at=game.created_at.isoformat(),
        deleted_at=game.deleted_at.isoformat() if game.deleted_at else None,
        participants=participant_responses,
        comment_count=comment_count,
        like_count=like_count,
        liked_by_me=liked_by_me
    )


def _build_comment_response(db: Session, comment: GameComment) -> CommentResponse:
    user = db.query(User).filter(User.id == comment.user_id).first()
    return CommentResponse(
        comment_id=comment.comment_id,
        game_id=comment.game_id,
        user_id=comment.user_id,
        username=user.login_id if user else comment.user_id,
        name=user.name if user else None,
        content=comment.content,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat()
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


def _recompute_winners(db: Session, game_id: str) -> None:
    """게임의 현재 참가자 점수를 바탕으로 팀별 승자(is_winner)를 다시 계산해 반영합니다."""
    participants = db.query(GameParticipant).filter(GameParticipant.game_id == game_id).all()
    team_scores = {p.team_color: p.score for p in participants}
    if len(team_scores) < 2:
        return
    winning_teams, is_draw = _compute_winners(team_scores)
    for p in participants:
        p.is_winner = None if is_draw else (p.team_color in winning_teams)


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
    video_url = _validate_video_url(request.video_url)
    played_at = _parse_played_at(request.played_at)
    game_status = _validate_game_status(request.game_status)

    new_game = Game(
        game_id=str(uuid.uuid4()),
        group_key=request.group_key,
        game_type=request.game_type,
        game_status=game_status,
        court_number=request.court_number,
        video_url=video_url,
        played_at=played_at
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

    return _build_game_response(db, new_game, current_user.id)


@router.get("/games/group/{group_key}", response_model=GameListResponse)
def get_group_games(
    group_key: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    year_month: str | None = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM. 지정 시 해당 월의 경기만 조회합니다."),
    sort: str = Query("desc", pattern="^(desc|asc)$", description="played_at 기준 정렬 방향"),
    my_games_only: bool = Query(False, description="현재 로그인한 사용자가 참가한 경기만 조회"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 그룹의 경기 이력을 조회합니다 (삭제 예정 경기는 제외)."""
    assert_group_member(db, group_key, current_user.id)

    base_query = db.query(Game).filter(Game.group_key == group_key, Game.is_deleted == False)

    if year_month:
        year, month = (int(part) for part in year_month.split("-"))
        month_start = datetime(year, month, 1)
        month_end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        base_query = base_query.filter(Game.played_at >= month_start, Game.played_at < month_end)

    if my_games_only:
        my_game_ids = db.query(GameParticipant.game_id).filter(GameParticipant.user_id == current_user.id)
        base_query = base_query.filter(Game.game_id.in_(my_game_ids))

    total = base_query.count()
    order_col = Game.played_at.asc() if sort == "asc" else Game.played_at.desc()
    games = base_query.order_by(order_col).offset(offset).limit(limit).all()

    return GameListResponse(items=[_build_game_response(db, g, current_user.id) for g in games], total=total)


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

    return GameListResponse(items=[_build_game_response(db, g, current_user.id) for g in games], total=total)


@router.get("/games/{game_id}", response_model=GameResponse)
def get_game_detail(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 경기의 상세 정보를 조회합니다."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)
    return _build_game_response(db, game, current_user.id)


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
    video_url = _validate_video_url(request.video_url)

    db.query(GameParticipant).filter(GameParticipant.game_id == game_id).delete()

    game.game_type = request.game_type
    game.court_number = request.court_number
    game.video_url = video_url
    if request.played_at is not None:
        game.played_at = _parse_played_at(request.played_at)

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

    return _build_game_response(db, game, current_user.id)


@router.patch("/games/{game_id}/status", response_model=GameResponse)
def update_game_status(
    game_id: str,
    request: GameStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """경기 상태만 변경합니다 (그룹 멤버 누구나 가능). 워치 등에서 경기 시작/종료를 표시할 때 사용."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태의 경기는 수정할 수 없습니다. 먼저 복구해 주세요."
        )

    game.game_status = _validate_game_status(request.game_status)
    db.commit()
    db.refresh(game)

    return _build_game_response(db, game, current_user.id)


@router.patch("/games/{game_id}/teams/{team_color}/score", response_model=GameResponse)
def update_team_score(
    game_id: str,
    team_color: str,
    request: TeamScoreUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """한 팀의 점수를 갱신합니다 (그룹 멤버 누구나 가능).

    절대값을 받는다 — 워치처럼 통신이 불안정한 클라이언트가 재시도해도
    중복 반영되지 않도록, 증가분(delta)이 아니라 "지금 점수는 N이다"를
    보내는 방식으로 설계했다.
    """
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태의 경기는 수정할 수 없습니다. 먼저 복구해 주세요."
        )

    team_participants = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.team_color == team_color
    ).all()
    if not team_participants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 팀을 찾을 수 없습니다."
        )

    for p in team_participants:
        p.score = request.score

    _recompute_winners(db, game_id)
    db.commit()
    db.refresh(game)

    return _build_game_response(db, game, current_user.id)


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
    game.deleted_at = now_kst()
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


# --- Comment Endpoints ---

def _get_comment_or_404(db: Session, game_id: str, comment_id: str) -> GameComment:
    comment = db.query(GameComment).filter(
        GameComment.comment_id == comment_id,
        GameComment.game_id == game_id
    ).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 댓글입니다."
        )
    return comment


@router.get("/games/{game_id}/comments", response_model=list[CommentResponse])
def get_comments(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 경기의 댓글 목록을 등록순으로 조회합니다."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    comments = db.query(GameComment).filter(
        GameComment.game_id == game_id
    ).order_by(GameComment.created_at.asc()).all()

    return [_build_comment_response(db, c) for c in comments]


@router.post("/games/{game_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    game_id: str,
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """경기에 댓글을 등록합니다 (그룹 멤버 누구나 가능, 삭제 예정 경기는 불가)."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태의 경기에는 댓글을 남길 수 없습니다."
        )

    if not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="댓글 내용을 입력해 주세요."
        )

    comment = GameComment(
        comment_id=str(uuid.uuid4()),
        game_id=game_id,
        user_id=current_user.id,
        content=request.content.strip()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return _build_comment_response(db, comment)


@router.put("/games/{game_id}/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    game_id: str,
    comment_id: str,
    request: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """본인이 작성한 댓글을 수정합니다."""
    comment = _get_comment_or_404(db, game_id, comment_id)

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인이 작성한 댓글만 수정할 수 있습니다."
        )

    if not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="댓글 내용을 입력해 주세요."
        )

    comment.content = request.content.strip()
    db.commit()
    db.refresh(comment)

    return _build_comment_response(db, comment)


@router.delete("/games/{game_id}/comments/{comment_id}")
def delete_comment(
    game_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """본인이 작성한 댓글을 삭제합니다."""
    comment = _get_comment_or_404(db, game_id, comment_id)

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인이 작성한 댓글만 삭제할 수 있습니다."
        )

    db.delete(comment)
    db.commit()

    return {"message": "댓글이 삭제되었습니다."}


# --- Like Endpoints ---

@router.post("/games/{game_id}/like", response_model=LikeActionResponse)
def like_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """경기에 좋아요를 등록합니다 (그룹 멤버 누구나 가능, 삭제 예정 경기는 불가)."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    if game.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="삭제 예정 상태의 경기에는 좋아요를 누를 수 없습니다."
        )

    existing = db.query(GameLike).filter(
        GameLike.game_id == game_id,
        GameLike.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 좋아요를 눌렀습니다."
        )

    db.add(GameLike(game_id=game_id, user_id=current_user.id))
    db.commit()

    like_count = db.query(GameLike).filter(GameLike.game_id == game_id).count()
    return LikeActionResponse(message="좋아요를 눌렀습니다.", like_count=like_count)


@router.delete("/games/{game_id}/like", response_model=LikeActionResponse)
def unlike_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """경기에 등록한 좋아요를 취소합니다."""
    game = _get_game_or_404(db, game_id)
    assert_group_member(db, game.group_key, current_user.id)

    like = db.query(GameLike).filter(
        GameLike.game_id == game_id,
        GameLike.user_id == current_user.id
    ).first()
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="좋아요를 누르지 않았습니다."
        )

    db.delete(like)
    db.commit()

    like_count = db.query(GameLike).filter(GameLike.game_id == game_id).count()
    return LikeActionResponse(message="좋아요를 취소했습니다.", like_count=like_count)
