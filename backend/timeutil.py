from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    """KST 벽시계 기준 naive datetime. DB에는 타임존 정보 없이 KST 값 그대로 저장/조회한다."""
    return datetime.now(KST).replace(tzinfo=None)
