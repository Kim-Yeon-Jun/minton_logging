# 🏸 Minton Logging - 배드민턴 기록 및 통계 웹 애플리케이션

## 🎯 프로젝트 개요

`minton_logging`은 배드민턴 동호인들의 경기 기록, 전적 통계, 상대 전적 등을 체계적으로 관리할 수 있도록 설계된 풀스택 웹 애플리케이션입니다.
FastAPI 백엔드와 React(Vite) 프론트엔드가 결합되어 사용자 친화적인 인터페이스를 제공합니다.

## 🚀 주요 기능

### 👤 인증 시스템
- **회원가입/로그인**: 아이디/비밀번호 기반 회원가입 및 로그인 API 구현

### 🏸 경기 기록 관리 (개발 예정)
- **경기 등록**: 파트너, 상대, 점수, 장소, 날짜 등 상세 기록
- **경기 목록 조회**: 필터링 및 페이징 지원
- **경기 수정/삭제**: 기록 오류 수정 및 데이터 관리

### 📊 통계 및 대시보드 (개발 예정)
- **개인 전적**: 승률, 경기 수, MVP 횟수 등 시각화
- **상대 전적**: 특정 상대와의 전적 및 승률 분석
- **월별 통계**: 월별 경기 추이 및 성적 그래프 제공

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
│   │   └── auth.py       # 인증 관련 API (/api/register, /api/login)
│   ├── models/           # 데이터베이스 모델
│   │   └── user.py       # User 모델
│   ├── config.py         # 환경 설정 (포트, DB 설정 등)
│   ├── database.py       # SQLAlchemy DB 연결 및 세션 설정
│   ├── main.py           # FastAPI 애플리케이션 진입점
│   ├── pyproject.toml    # Python 의존성 및 패키지 설정
│   └── run.sh            # 백엔드 실행 스크립트
├── frontend/            # React 프론트엔드 애플리케이션
│   ├── src/
│   │   ├── features/     # 기능별 모듈 (auth, dashboard 등)
│   │   ├── pages/        # 페이지 컴포넌트 (AuthPage 등)
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
| POST | `/api/login` | 로그인 |

### 그룹 API (구현 완료)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/groups` | 그룹(동호회/모임) 생성 |
| GET | `/api/groups` | 전체 그룹 목록 조회 |
| GET | `/api/groups/{group_key}` | 그룹 상세 정보 및 멤버 목록 조회 |
| GET | `/api/groups/user/{user_id}` | 특정 사용자가 속한 그룹 목록 조회 |
| POST | `/api/groups/{group_key}/join` | 그룹 가입 |
| POST | `/api/groups/{group_key}/leave` | 그룹 탈퇴 |


### 경기 API (개발 예정)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/matches` | 경기 기록 추가 |
| GET | `/api/matches` | 경기 목록 조회 |
| GET | `/api/matches/{id}` | 특정 경기 조회 |
| PUT | `/api/matches/{id}` | 경기 정보 수정 |
| DELETE | `/api/matches/{id}` | 경기 삭제 |

### 통계 API (개발 예정)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/statistics/personal` | 개인 통계 |
| GET | `/api/statistics/opponent/{username}` | 상대 전적 |
| GET | `/api/statistics/monthly` | 월별 통계 |

## 📜 변경 로그

- v0.1.0 (2026-08-02): 초기 프로젝트 구조 설정 및 FastAPI / React 19 연동 (기본 회원가입/로그인 API 구현)

## 🎯 향후 계획

- [ ] JWT 인증 및 보안 강화 (비밀번호 해싱 적용)
- [ ] 경기 기록 (Matches) API 및 화면 구현
- [ ] 통계 및 대시보드 화면 구현
- [ ] 반응형 UI 및 모바일 지원
- [ ] 소셜 로그인 기능 추가
- [ ] 이메일 알림 및 추가 편의 기능
- [ ] 공용 셔틀콕 재고 관리
- [ ] 카카오톡 투표/일정 연동
- [ ] 스프레드 시트 연동 

## 🎯 프로젝트 상태

**⚙️ 개발 진행 중**

- [x] FastAPI 백엔드 기본 서버 구조
- [x] React (Vite) 프론트엔드 기본 구조
- [x] 기본 회원가입 / 로그인 API 및 페이지
- [ ] 경기 기록 관리 기능
- [ ] 통계 및 대시보드 기능
- [ ] JWT 기반 세션 및 보안 강화

## 📄 라이선스 정보

Copyright (c) 2026 Kim Yeon-Jun

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.