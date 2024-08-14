from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.websocket import router as websocket_router

app = FastAPI()

# CORS 설정 추가
origins = [
    "http://localhost",
    "http://192.168.0.15:8081",  # React 개발 서버의 기본 포트
    "http://192.168.0.15:5173",  # Expo 개발 서버의 기본 포트
    "http://localhost:5173",  # Expo 개발 서버의 기본 포트
    # 필요한 경우 다른 출처도 추가 가능
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 HTTP 헤더
)
# 웹소켓 라우터 포함
app.include_router(websocket_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
