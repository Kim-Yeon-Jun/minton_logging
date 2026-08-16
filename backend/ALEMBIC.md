# Alembic 가이드

`backend/`에 Alembic을 적용해서, DB 스키마 변경을 앞으로는 마이그레이션 파일로 추적합니다.
기존에는 `main.py`가 시작할 때 `Base.metadata.create_all()`로 없는 테이블만 만들고, 이미 있는 테이블에
컬럼을 추가할 땐 수동으로 `ALTER TABLE`을 날렸습니다(`bd_game_mt`의 소프트 삭제 컬럼 등). 이제부터
스키마를 바꾸는 작업은 Alembic 마이그레이션으로 남기는 게 원칙입니다.

## 왜 필요한가

- 스키마 변경 이력이 git에 파일로 남는다 (누가/언제/무엇을 바꿨는지 diff로 확인 가능)
- 여러 환경(로컬/스테이징/운영)에 같은 순서로 안전하게 적용 가능
- `upgrade`/`downgrade`로 롤백 경로가 명확해짐

`main.py`의 `create_all()`은 그대로 남아 있습니다 — 테스트 스위트(`backend/tests/conftest.py`)가 매 테스트
세션마다 임시 스키마를 통째로 새로 만들 때 이걸 그대로 활용하기 때문입니다. `create_all()`은 이미 있는
테이블/컬럼에는 아무 영향을 주지 않는 no-op이라 Alembic과 공존해도 안전합니다. 다만 **실제 DB(로컬 dev,
운영) 스키마를 바꿀 때는 `ALTER TABLE`을 직접 치지 말고 Alembic 마이그레이션으로 작성**하세요.

## 구조

```
backend/
├── alembic.ini          # Alembic 설정 (DB URL은 여기 없음 — env.py가 동적으로 채움)
├── alembic/
│   ├── env.py            # 마이그레이션 실행 환경 설정 (아래 참고)
│   ├── script.py.mako     # 새 리비전 생성 시 사용하는 템플릿
│   └── versions/
│       └── d028a621bc49_baseline_schema.py   # 최초 baseline (아래 참고)
```

`env.py`가 하는 일:
- DB 접속 정보를 `alembic.ini`에 하드코딩하지 않고, 앱과 동일한 `config.settings`(`.env`)에서 읽어옴 →
  URL을 두 곳에서 따로 관리할 필요 없음
- `models/` 전체를 import해서 `Base.metadata`를 `target_metadata`로 사용 → `alembic revision
  --autogenerate`가 모델 변경사항을 스캔할 수 있음
- 앱 스키마가 `public`이 아니라 `DATABASE_SCHEMA`(`.env`의 `bd_log` 등)라서, `alembic_version` 테이블도
  `public`이 아니라 같은 스키마 안에 생기도록 `version_table_schema`를 지정
- 스키마가 아직 없는 새 DB에도 대응하도록, 마이그레이션 실행 전에 `CREATE SCHEMA IF NOT EXISTS`를 실행
- `alembic_version` 테이블 자체가 autogenerate diff에 "삭제된 테이블"로 잘못 잡히는 걸 막는
  `include_object` 필터 적용
- (중요) DB 커넥션에 `search_path`를 설정하지 않음 — `database.py`(앱 런타임)는 편의상 search_path를
  쓰지만, Alembic 쪽 커넥션에 search_path를 걸면 리플렉션된 FK의 참조 스키마가 `None`으로 잡혀서
  `target_metadata`의 명시적 스키마(`bd_log`)와 다르다고 판단해 버립니다. 그 결과 실제로는 동일한
  FK인데도 매번 "삭제 후 재생성"하는 노이즈 diff가 생겼습니다 — `include_schemas=True` +
  스키마 한정 `MetaData` 조합에서 흔히 겪는 함정이라 기록해 둡니다.

## 자주 쓰는 명령어

전부 `backend/` 디렉터리에서 실행합니다.

```bash
# 현재 DB가 어느 리비전에 있는지 확인
uv run alembic current

# 리비전 이력 전체 보기
uv run alembic history

# 모델을 바꾼 뒤, 그 변경을 감지해서 마이그레이션 파일 자동 생성
uv run alembic revision --autogenerate -m "설명"
# 생성된 파일은 반드시 열어서 내용을 검토/수정할 것 (autogenerate는 참고용이지 100% 정답이 아님)

# 마이그레이션을 실제 DB에 적용 (가장 최신 리비전까지)
uv run alembic upgrade head

# 한 단계만 되돌리기
uv run alembic downgrade -1

# 실제로 실행하지 않고 SQL만 출력해서 미리 검토 (DB 연결 없이도 가능)
uv run alembic upgrade head --sql
uv run alembic downgrade <직전리비전>:base --sql
```

## 새 스키마 변경을 추가하는 흐름

1. `backend/models/*.py`에서 모델을 수정한다 (컬럼 추가/삭제, 인덱스 추가 등)
2. `uv run alembic revision --autogenerate -m "add xxx column"` 실행
3. `alembic/versions/`에 생긴 새 파일을 열어서, 의도한 변경만 들어있는지 확인하고 필요하면 손으로 수정
   (특히 컬럼 삭제/이름 변경은 autogenerate가 "삭제 후 새로 추가"로 오인하는 경우가 많으니 확인 필수)
4. 로컬 DB에 `uv run alembic upgrade head`로 적용해서 실제로 잘 되는지 확인
5. 커밋 (마이그레이션 파일은 코드 리뷰 대상)
6. 배포 시 운영 DB에도 `alembic upgrade head` 실행

## 기존 DB(이미 테이블이 있는 dev/운영)에 처음 적용하는 법

이 프로젝트에는 이미 라이브 DB에 `Base.metadata.create_all()` 및 수동 `ALTER TABLE`로 만들어진 테이블이
있었습니다. 그래서 첫 마이그레이션(`d028a621bc49_baseline_schema.py`)은 **그 기존 스키마를 그대로
재현하는 baseline**으로 작성했고, 실제 라이브 DB(`bd_log` 스키마)에는 다음처럼 적용했습니다.

```bash
uv run alembic stamp head
```

`stamp`는 CREATE TABLE 등 실제 SQL을 실행하지 않고, "이 DB는 이미 `d028a621bc49`까지 반영된 상태다"라고
`alembic_version` 테이블에 기록만 합니다. 이미 테이블이 있는 DB에 `alembic upgrade head`를 실행하면
"테이블이 이미 존재한다" 오류가 나므로 반드시 `stamp`를 써야 합니다.

반대로 **완전히 비어있는 새 DB**(신규 개발 환경, CI 등)라면 `alembic upgrade head`를 그대로 실행해서
baseline부터 최신 리비전까지 전부 생성하면 됩니다.

## 알아두면 좋은 점

- baseline 마이그레이션과 `models/*.py`의 제약조건/인덱스 이름(`fk_grp_owner`, `idx_grp_name` 등)은
  실제 라이브 DB에 있는 이름과 정확히 맞춰뒀습니다. 원래 모델에는 이런 이름이 명시돼 있지 않아서
  Postgres/SQLAlchemy가 자동으로 다른 이름을 붙였다면, `--autogenerate`를 돌릴 때마다 기존 테이블에
  대해 "이름이 다르다"는 가짜 diff가 매번 나왔을 것입니다 — 지금은 정리되어 있어서 `--autogenerate`는
  실제로 바뀐 것만 보여줍니다.
- `bd_usr_mt.is_active` 컬럼은 실제 DB에는 있었지만 `User` 모델에는 선언돼 있지 않았습니다. 추가해
  뒀습니다 — 안 그러면 autogenerate가 "이 컬럼을 지워야 한다"고 제안했을 것이고, 무심코 그 마이그레이션을
  적용하면 실제 데이터가 있는 컬럼이 삭제될 수 있었습니다.
