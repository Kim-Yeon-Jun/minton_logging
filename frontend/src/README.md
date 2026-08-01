# Frontend Source Architecture (`src/`)

이 디렉토리는 Feature-Driven (도메인/기능 중심) 아키텍처 패턴을 따릅니다.

## 📂 폴더 구조 안내

```
src/
├── features/                 # 기능(도메인) 단위 독립 모듈
│   ├── auth/                 # 인증 (로그인, 회원가입 등) 기능
│   │   ├── components/       # Auth 기능 전용 UI 컴포넌트 (LoginForm, RegisterForm)
│   │   ├── hooks/            # Auth 관련 커스텀 훅 (useLogin, useRegister)
│   │   ├── services/         # Auth API 요청 처리 (authApi.ts)
│   │   ├── types/            # Auth 전용 TypeScript 타입 정의 (auth.types.ts)
│   │   └── index.ts          # External module export 배럴 파일
│   │
│   └── dashboard/            # 대시보드 관련 기능
│       ├── components/       # WelcomeScreen 등 대시보드 UI 컴포넌트
│       └── index.ts
│
├── components/               # 비즈니스 로직 없이 전역에서 공통으로 쓰이는 UI (Button, Modal, Input 등)
├── pages/                    # 라우팅 단위 페이지 (features의 컴포넌트 조합)
├── hooks/                    # 프로젝트 전역 공통 커스텀 훅
└── utils/                    # 프로젝트 전역 헬퍼 및 유틸리티 함수
```

## 💡 아키텍처 개발 지침

1. **기능의 독립성 (`features/`)**
   - 특정 도메인(인증, 사용자, 대시보드 등)에 종속된 UI, 비즈니스 로직, API 연동, 타입은 해당 `features/<domain>` 폴더 내부에서 관리합니다.
   - 외부 파일에서 참조할 때는 `features/<domain>` 의 `index.ts`를 통해 퍼블릭 API로 노출된 요소만 임포트합니다.

2. **공통 UI (`components/`)**
   - 도메인 비즈니스 로직에 의존하지 않는 순수 프레젠테이션 UI 컴포넌트만 위치합니다.

3. **페이지 컴포넌트 (`pages/`)**
   - 라우터와 직접 연결되는 고수준 페이지 컴포넌트로, `features`의 컴포넌트들을 조합하여 페이지 화면을 구성합니다.
