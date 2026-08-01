# 🏸 Minton Logging - 배드민턴 기록 및 통계 웹 애플리케이션

## 🎯 프로젝트 개요

`minton_logging`은 배드민턴 동호인들의 경기 기록, 전적 통계, 상대 전적 등을 체계적으로 관리할 수 있도록 설계된 풀스택 웹 애플리케이션입니다.
Flask 백엔드와 React 프론트엔드가 결합되어 사용자 친화적인 인터페이스를 제공합니다.

## 🚀 주요 기능

### 👤 인증 시스템
- **회원가입/로그인**: 이메일 기반 인증 및 JWT 기반 세션 관리
- **회원정보 관리**: 프로필 조회, 수정, 비밀번호 변경
- **비밀번호 재설정**: 이메일을 통한 안전한 비밀번호 찾기 기능

### 🏸 경기 기록 관리
- **경기 등록**: 파트너, 상대, 점수, 장소, 날짜 등 상세 기록
- **경기 목록 조회**: 필터링 및 페이징 지원
- **경기 수정/삭제**: 기록 오류 수정 및 데이터 관리

### 📊 통계 및 대시보드
- **개인 전적**: 승률, 경기 수, MVP 횟수 등 시각화
- **상대 전적**: 특정 상대와의 전적 및 승률 분석
- **월별 통계**: 월별 경기 추이 및 성적 그래프 제공

## 🛠️ 기술 스택

### 백엔드 (Backend)
- **Framework**: [Flask](https://flask.palletsprojects.com/)
- **Language**: Python 3.11+
- **Database**: SQLite (개발용), PostgreSQL (운영)
- **Security**:
  - 비밀번호: Argon2 (bcrypt 대체)
  - 인증: JWT (JSON Web Tokens)
- **CORS**: Flask-CORS

### 프론트엔드 (Frontend)
- **Framework**: [React 18](https://react.dev/)
- **Language**: TypeScript
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: CSS Modules, Tailwind CSS
- **API Client**: Axios

### 인프라
- **Containerization**: Docker, Docker Compose

## 📂 프로젝트 구조

```
minton_logging/
├── backend/             # Flask 백엔드 애플리케이션
│   ├── api/              # API 엔드포인트
│   │   ├── auth.py       # 인증 관련 API
│   │   ├── matches.py    # 경기 기록 API
│   │   └── profile.py    # 사용자 프로필 API
│   ├── config.py         # 환경 설정
│   ├── main.py           # 애플리케이션 진입점
│   └── models.py         # 데이터베이스 모델
├── frontend/            # React 프론트엔드 애플리케이션
│   ├── src/
│   │   ├── auth/         # 인증 관련 컴포넌트 및 hooks
│   │   ├── components/   # 재사용 가능한 UI 컴포넌트
│   │   ├── features/     # 기능별 모듈
│   │   ├── pages/        # 페이지 컴포넌트
│   │   └── services/     # API 서비스
│   └── tsconfig.json     # TypeScript 설정
└── docker-compose.yml   # Docker 컨테이너 오케스트레이션
```

## ⚙️ 설치 및 실행

### 사전 요구 사항
- Docker Desktop
- Git

### 1. 저장소 클론
```bash
git clone https://github.com/Kim-Yeon-Jun/minton_logging.git
cd minton_logging
```

### 2. 컨테이너 빌드 및 실행
```bash
docker-compose up --build
```

### 3. 애플리케이션 접속
- 프론트엔드: [http://localhost:5173](http://localhost:5173)
- API 서버: [http://localhost:5000](http://localhost:5000)

## 🚀 개발 가이드

### 백엔드 개발
1. 가상환경 활성화:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. 개발 서버 실행:
```bash
flask run
```

### 프론트엔드 개발
1. 의존성 설치:
```bash
cd frontend
npm install
```

2. 개발 서버 실행:
```bash
npm run dev
```

## 🧪 테스트

### 백엔드 테스트
```bash
cd backend
python -m pytest tests/
```

### 프론트엔드 테스트
```bash
cd frontend
npm test
```

## 🔒 보안

### 비밀번호 보안
- Argon2 알고리즘을 사용하여 강력한 비밀번호 해싱
- 최소 12자 이상의 비밀번호 정책

### 인증 보안
- JWT 토큰 기반 인증
- 토큰 만료 시간 1시간
- Refresh token 미사용 (세션 기반)

## 🔌 API 문서

### 일반 인증 API
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/auth/register` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |
| GET | `/api/auth/me` | 현재 사용자 정보 조회 |

### 경기 API
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/matches` | 경기 기록 추가 |
| GET | `/api/matches` | 경기 목록 조회 |
| GET | `/api/matches/{id}` | 특정 경기 조회 |
| PUT | `/api/matches/{id}` | 경기 정보 수정 |
| DELETE | `/api/matches/{id}` | 경기 삭제 |

### 통계 API
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/statistics/personal` | 개인 통계 |
| GET | `/api/statistics/opponent/{username}` | 상대 전적 |
| GET | `/api/statistics/monthly` | 월별 통계 |

## 📝 라이선스

본 프로젝트는 MIT 라이선스 하에 배포됩니다.
자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👨‍💻 기여

기여 방법은 다음과 같습니다:

1. 저장소를 fork합니다.
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`).
4. 브랜치를 push합니다 (`git push origin feature/AmazingFeature`).
5. Pull Request를 생성합니다.

## 🤝 컨택

- 프로젝트 리더: 김연준
- 이메일: [EMAIL_ADDRESS]

## 📜 변경 로그

- v1.0.0 (2026-08-02): 초기 프로젝트 구조 설정
- v1.1.0 (2026-08-03): 인증 시스템 구현
- v1.2.0 (2026-08-04): 경기 기록 관리 기능 구현
- v1.3.0 (2026-08-05): 통계 및 대시보드 기능 구현
- v1.4.0 (2026-08-06): 모바일 반응형 디자인 적용

## 🎯 향후 계획

- [ ] 소셜 로그인 기능 추가
- [ ] 이메일 알림 기능
- [ ] 관리자 페이지 구현
- [ ] 경기 일정 관리 기능
- [ ] 배드민턴 용품 리뷰 기능

## 🎯 프로젝트 상태

**✅ 진행 중**

- [x] 백엔드 API 서버
- [x] 프론트엔드 웹 애플리케이션
- [x] 인증 시스템
- [x] 경기 기록 관리
- [x] 통계 및 대시보드
- [x] 반응형 디자인
- [x] Docker 컨테이너

## 📄 라이선스 정보

Copyright (c) 2026 Kim Yeon-Jun

이 프로젝트는 MIT 라이선스 하에 배포됩니다