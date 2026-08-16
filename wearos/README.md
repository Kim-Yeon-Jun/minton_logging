# Minton Wear (Wear OS 앱 골격)

`backend/`가 제공하는 기기 페어링·경기 API를 사용해, 워치 단독으로 경기 등록/실시간 점수 기록을
할 수 있게 하는 Wear OS 네이티브 앱입니다. 폰 컴패니언 앱 없이 워치가 Wi-Fi로 백엔드에 직접
통신합니다 (`AndroidManifest.xml`의 `com.google.android.wearable.standalone` 참고).

## 여는 법

1. Android Studio로 이 `wearos/` 폴더를 **Open**합니다 (상위 `minton_logging/` 전체가 아니라
   `wearos/`를 프로젝트 루트로 열어야 합니다).
2. Gradle 래퍼(`gradlew`/`gradle-wrapper.jar`)를 아직 커밋해두지 않았습니다 — 처음 열면
   Android Studio가 "Gradle wrapper가 없다"며 자동 생성을 제안합니다. 제안을 그대로 따르면
   됩니다 (버전 카탈로그에 이미 Gradle 9.4.1 이상을 요구하는 AGP 9.2.0을 지정해뒀습니다).
3. 첫 동기화 시 Android Studio가 설치된 SDK/AGP 버전에 맞춰 일부 버전 조정을 제안할 수 있습니다
   (`gradle/libs.versions.toml`). 골격 단계이니 Studio의 제안(Upgrade Assistant)을 따라가도
   무방합니다.

## 버전 (2026-08 기준 확인)

| 항목 | 버전 |
|---|---|
| Android Gradle Plugin | 9.2.0 |
| Gradle | 9.4.1+ |
| Kotlin | 2.3.20 |
| Compose BOM | 2026.08.00 |
| Wear Compose (Material) | 1.4.1 |
| compileSdk / targetSdk | 36 |
| minSdk | 30 (Wear OS 3+) |

## 로컬 백엔드에 연결하기

- **에뮬레이터**: 별도 설정 없이 됩니다. `10.0.2.2`는 에뮬레이터 안에서 호스트 PC의
  `localhost`를 가리키는 표준 별칭이라, `app/build.gradle.kts`의 debug 빌드가
  `http://10.0.2.2:8080/`을 기본 API 주소로 씁니다 (`backend/`를 `uv run python main.py`로
  기본 포트에 띄워둔 상태여야 함).
- **실제 워치**: 워치와 PC가 같은 Wi-Fi에 있어야 하고, `10.0.2.2` 대신 PC의 LAN IP
  (`ipconfig`로 확인)로 바꿔야 합니다. `app/build.gradle.kts`의 `debug { buildConfigField(...) }`
  값을 수정하세요.
- 백엔드의 CORS는 현재 `allow_origins=["*"]`라 네이티브 앱의 직접 호출 자체는 막히지 않습니다.

## 폴더 구조

```
app/src/main/java/com/mintonlogging/wear/
├── MainActivity.kt        앱 진입점, PairingViewModel 조립
├── MintonWearApplication.kt
├── navigation/             SwipeDismissableNavHost 기반 화면 전환
├── data/
│   ├── remote/             Retrofit 인터페이스 + DTO (backend/api/*.py 응답 스키마 그대로 매핑)
│   │   └── dto/
│   └── auth/                TokenStore (JWT 보관, DataStore 기반)
├── pairing/                 기기 페어링 화면/뷰모델 (완성 — /api/device/* 실제 연동됨)
├── group/                   그룹·참가자 선택 화면 (TODO — 자리만 잡아둔 상태)
├── scoring/                 실시간 점수 기록 화면 (TODO — 자리만 잡아둔 상태)
└── theme/                   Wear Compose 테마
```

`data/remote`의 인터페이스(`DeviceApi`, `GameApi`)는 `backend/`의 실제 엔드포인트·요청/응답
스키마와 필드명까지 그대로 맞춰뒀습니다. 백엔드 스키마가 바뀌면 이 DTO들도 같이 바꿔야 합니다.

## 지금 상태 (골격)

- ✅ Gradle 프로젝트 구조, 의존성, 매니페스트
- ✅ 페어링 흐름 (`pairing/`) — 코드 발급 → 화면 표시 → 폴링 → 토큰 저장까지 실제로 동작
- ✅ 백엔드 API에 대응하는 Retrofit 인터페이스/DTO 전부 (`data/remote/`)
- ⬜ 그룹 선택 화면 (`group/GroupSelectScreen.kt`) — `GameApi.getGroups()`/`getGroupDetail()` 연동 필요
- ⬜ 참가자 선택 (단식 2명 / 복식 4명, 팀 배정)
- ⬜ 실시간 점수 기록 화면 (`scoring/LiveScoreScreen.kt`) — `GameApi.createGame()` /
  `updateTeamScore()` / `updateGameStatus()` 연동 필요
- ⬜ 오프라인 재시도 큐 (경기 중 네트워크 끊김 대비)
- ⬜ 실제 런처 아이콘 (지금은 초록 원 플레이스홀더, Android Studio Image Asset 도구로 교체)
- ⬜ 토큰 암호화 저장 (`TokenStore`의 TODO 참고)

## 왜 이런 구조인가

- `backend/`, `frontend/`와 동일하게, 플랫폼별로 독립된 툴체인(Gradle)을 갖는 최상위 폴더로
  분리했습니다.
- 코드 안 폴더(`pairing/`, `group/`, `scoring/`)는 백엔드 `api/` 모듈 구분(`device.py`,
  `games.py`)과 최대한 대응시켜서, 화면 하나가 어떤 백엔드 엔드포인트를 쓰는지 바로 보이게
  했습니다.
- Retrofit + kotlinx.serialization을 선택한 이유: 코드 생성(kapt/KSP) 없이 Kotlin
  `@Serializable` data class만으로 백엔드 Pydantic 스키마를 그대로 옮길 수 있어서, 백엔드
  API가 늘어날 때 DTO 추가 비용이 가장 적습니다.
