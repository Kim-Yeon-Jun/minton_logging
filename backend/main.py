import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from api.auth import router as auth_router
from api.groups import router as groups_router
from api.games import router as games_router
from api.device import router as device_router

# 스키마 및 데이터베이스 테이블 자동 생성
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[Warning] DB 테이블 생성 또는 연결 중 예외 발생: {e}")

app = FastAPI(title="Minton Logging API")

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(groups_router, prefix="/api", tags=["Groups"])
app.include_router(games_router, prefix="/api", tags=["Games"])
app.include_router(device_router, prefix="/api", tags=["Device"])


@app.get("/")
def read_root():
    return {"message": "Minton Logging Backend API Running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVER_PORT, reload=settings.RELOAD)
