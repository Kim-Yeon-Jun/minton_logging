# 🏸 Minton Logging - 배드민턴 기록 및 통계 웹 애플리케이션

## 🎯 프로젝트 개요

`minton_logging`은 배드민턴 동호인들의 경기 기록, 전적 통계, 상대 전적 등을 체계적으로 관리할 수 있도록 설계된 풀스택 웹 애플리케이션입니다.
FastAPI 백엔드와 React(Vite) 프론트엔드가 결합되어 사용자 친화적인 인터페이스를 제공합니다.

## 🚀 주요 기능

### 👤 인증 시스템 (구현 완료)
- **회원가입/로그인**: 아이디/비밀번호 기반 회원가입 및 로그인 (bcrypt 해싱)
- **JWT 세션**: `Authorization: Bearer` 토큰 기반 인증, `/api/me`로 세션 복원
- **비밀번호 변경**: 현재 비밀번호 확인 후 변경

### 👥 그룹(동호회/모임) 관리 (구현 완료)
- **그룹 생성/조회**: 그룹 생성, 전체/사용자별 그룹 목록, 그룹 상세(멤버 목록 포함) 조회
- **가입/탈퇴**: 그룹 가입 및 탈퇴, 대표 그룹(`group_key`) 자동 갱신
- 그룹 소유자뿐 아니라 멤버 누구나 해당 그룹의 경기 기록을 관리할 수 있는 권한 모델

### 🏸 경기 기록 관리 (구현 완료)
- **경기 등록**: 팀 구성(2팀 이상), 팀별 점수, 코트 번호 등 기록, 참가자는 반드시 해당 그룹 멤버
- **경기 목록/상세 조회**: 그룹별 최신순 목록(페이징 `limit`/`offset`), 경기 상세 조회
- **경기 수정**: 참가자/점수/코트 정보 수정 (삭제 예정 상태에서는 수정 불가)
- **소프트 삭제 라이프사이클**: 삭제(휴지통 이동) → 휴지통 조회 → 복구 → 영구 삭제

### 📊 통계 및 대시보드 (구현 완료)
- **개인 전적**: 로그인한 사용자 기준 승/패/무 및 승률 (그룹별)
- **상대 전적**: 그룹 내 상대별 승/패 집계
- **월별 통계**: 최근 6개월 경기 수 및 승리 추이

## 🛠️ 기술 스택

### 백엔드 (Backend)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.11+
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **ASGI Server**: Uvicorn
- **Package Manager**: uv / pip

### 프론트엔드 (Frontend)
- **Framework**: [React 19](https://react.dev/)
- **Language**: TypeScript
- **Build Tool**: [Vite](https://vite.dev/)
- **Styling**: Vanilla CSS

## 📂 프로젝트 구조

```
minton_logging/
├── backend/             # FastAPI 백엔드 애플리케이션
│   ├── api/              # API 엔드포인트
│   │   ├── auth.py       # 인증 API (/api/register, /api/login, /api/me, 비밀번호 변경)
│   │   ├── groups.py     # 그룹 API (생성/조회/가입/탈퇴, 그룹 통계)
│   │   └── games.py      # 경기 기록 API (등록/조회/수정/소프트삭제/복구/영구삭제)
│   ├── models/           # 데이터베이스 모델
│   │   ├── user.py       # User 모델
│   │   ├── group.py      # Group, GroupMember 모델
│   │   └── game.py       # Game, GameParticipant 모델
│   ├── scripts/          # 일회성 마이그레이션 스크립트 (비밀번호 해싱 등)
│   ├── tests/            # pytest 테스트 스위트 (인증/권한/소프트삭제 라이프사이클)
│   ├── config.py         # 환경 설정 (포트, DB 설정 등)
│   ├── database.py       # SQLAlchemy DB 연결 및 세션 설정
│   ├── permissions.py    # 그룹 멤버십 권한 검증 헬퍼
│   ├── security.py       # 비밀번호 해싱, JWT 발급/검증
│   ├── main.py           # FastAPI 애플리케이션 진입점
│   ├── pyproject.toml    # Python 의존성 및 패키지 설정
│   └── run.sh            # 백엔드 실행 스크립트
├── frontend/            # React 프론트엔드 애플리케이션
│   ├── src/
│   │   ├── features/     # 기능별 모듈 (auth, groups, games, stats, dashboard, mypage)
│   │   ├── pages/        # 페이지 컴포넌트 (AuthPage, HomePage, GroupPage)
│   │   ├── components/   # 공용 프레젠테이션 컴포넌트 (TopBar, CopyButton)
│   │   ├── App.tsx       # 메인 애플리케이션 컴포넌트
│   │   └── main.tsx      # 프론트엔드 진입점
│   ├── package.json      # Node.js 의존성 및 스크립트
│   ├── vite.config.js    # Vite 설정
│   └── run.sh            # 프론트엔드 실행 스크립트
├── LICENSE               # MIT 라이선스
└── check_port_status.sh  # 포트 상태 확인 스크립트
```

## ⚙️ 설치 및 실행

### 사전 요구 사항
- Python 3.11 이상
- Node.js (v18 이상 권장) 및 npm
- PostgreSQL 데이터베이스

### 1. 저장소 클론
```bash
git clone https://github.com/Kim-Yeon-Jun/minton_logging.git
cd minton_logging
```

### 2. 백엔드 실행
```bash
cd backend
python -m venv .venv
# Windows Command Prompt / PowerShell:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

pip install -e .  # 또는 uv sync
python main.py
```
> 기본 백엔드 서버 포트는 `8080`입니다.

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```
> 기본 프론트엔드 서버 포트는 `5173`입니다.

### 4. 애플리케이션 접속
- 프론트엔드: [http://localhost:5173](http://localhost:5173)
- API 문서 (Swagger UI): [http://localhost:8080/docs](http://localhost:8080/docs)

## 🔌 API 문서

### 인증 API (구현 완료)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/register` | 회원가입 |
| POST | `/api/login` | 로그인 (JWT 발급) |
| GET | `/api/me` | 현재 로그인한 사용자 정보 조회 (세션 복원) |
| PUT | `/api/users/me/password` | 비밀번호 변경 |

### 그룹 API (구현 완료)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/groups` | 그룹(동호회/모임) 생성 |
| GET | `/api/groups` | 전체 그룹 목록 조회 |
| GET | `/api/groups/{group_key}` | 그룹 상세 정보 및 멤버 목록 조회 |
| GET | `/api/groups/user/{user_id}` | 특정 사용자가 속한 그룹 목록 조회 |
| POST | `/api/groups/{group_key}/join` | 그룹 가입 |
| POST | `/api/groups/{group_key}/leave` | 그룹 탈퇴 |
| GET | `/api/groups/{group_key}/stats` | 그룹 내 개인 전적/상대 전적/월별 추이 통계 |

### 경기 API (구현 완료)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/games` | 경기 기록 등록 |
| GET | `/api/games/group/{group_key}` | 그룹의 경기 이력 조회 (페이징, 삭제 예정 제외) |
| GET | `/api/games/group/{group_key}/trash` | 그룹의 삭제 예정(휴지통) 경기 목록 조회 |
| GET | `/api/games/{game_id}` | 특정 경기 상세 조회 |
| PUT | `/api/games/{game_id}` | 경기 정보 수정 |
| DELETE | `/api/games/{game_id}` | 경기 소프트 삭제 (휴지통 이동) |
| POST | `/api/games/{game_id}/restore` | 삭제 예정 경기 복구 |
| DELETE | `/api/games/{game_id}/permanent` | 삭제 예정 경기 영구 삭제 |

## 📜 변경 로그

- v0.1.0 (2026-08-02): 초기 프로젝트 구조 설정 및 FastAPI / React 19 연동 (기본 회원가입/로그인 API 구현)
- v0.2.0 (2026-08-07): JWT 인증/비밀번호 해싱, 그룹(동호회) 생성·가입·탈퇴, 경기 기록 CRUD 및 소프트 삭제(휴지통·복구·영구삭제) 라이프사이클, 그룹별 통계(개인 전적/상대 전적/월별 추이) API 및 화면 구현

## 🎯 향후 계획

경기 기록·통계 등 핵심 로깅 기능은 구현이 완료되어, 이제는 배드민턴 동호회 운영에 실질적으로 도움이 되는 부가 기능 위주로 확장하면 좋을 것으로 보입니다.

### 인프라/기반
- [ ] 반응형 UI 및 모바일 지원
- [ ] 소셜 로그인 기능 추가
- [ ] DB 마이그레이션 도구 도입 (Alembic 등, 현재는 수동 `ALTER TABLE` 관리)
- [ ] 스프레드 시트 연동 (기존 기록 백업/이전용)

### 배드민턴 동호회 특화 기능 (제안)
- [ ] **실력 등급/레이팅 시스템**: 경기 결과 기반 ELO/글리코 레이팅 산출 및 급수(초급/중급/고급) 관리 — 파트너 매칭·팀 밸런스의 기초 데이터로 활용
- [ ] **자동 매치메이킹/팀 편성**: 출석 인원과 레이팅을 기반으로 밸런스 잡힌 복식 조 자동 편성
- [ ] **모임 일정 관리 및 참석 투표**: 다음 모임 일정 등록, 참석/불참 투표, 카카오톡 투표·일정 연동
- [ ] **출석 체크 및 노쇼 관리**: 회차별 출석률 집계, 잦은 노쇼 알림
- [ ] **랭킹보드/리더보드**: 그룹 내 승률·연승·레이팅 기준 순위표
- [ ] **회비 관리**: 월 회비 납부 현황 기록 및 미납자 조회, 정산 내역
- [ ] **코트 예약/이용 현황 관리**: 요일별 코트 예약 및 대여 비용 분담
- [ ] **공용 셔틀콕 재고 관리**: 셔틀콕 구매/사용 내역 기록, 재고 알림
- [ ] **MVP/베스트 파트너 투표**: 경기 후 그날의 MVP나 함께 치기 좋았던 파트너 투표
- [ ] **대회/토너먼트 브라켓 관리**: 내부 리그전·토너먼트 대진표 생성 및 결과 반영
- [ ] **경기 사진/하이라이트 첨부**: 경기 기록에 사진 첨부
- [ ] **이메일/푸시 알림**: 모임 리마인더, 회비 납부 안내 등 알림 기능

## 🎯 프로젝트 상태

**⚙️ 개발 진행 중**

- [x] FastAPI 백엔드 기본 서버 구조
- [x] React (Vite) 프론트엔드 기본 구조
- [x] JWT 기반 세션 및 보안 강화 (bcrypt 해싱, `/api/me` 세션 복원, 비밀번호 변경)
- [x] 그룹(동호회/모임) 생성·조회·가입·탈퇴 기능
- [x] 경기 기록 관리 기능 (등록/조회/수정/소프트삭제/복구/영구삭제)
- [x] 통계 및 대시보드 기능 (개인 전적/상대 전적/월별 추이)
- [ ] 매치 스케줄링/투표 기능
- [ ] 배드민턴 특화 부가 기능 (레이팅, 회비, 코트 예약 등 — 위 향후 계획 참고)

## 📄 라이선스 정보

Copyright (c) 2026 Kim Yeon-Jun

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.