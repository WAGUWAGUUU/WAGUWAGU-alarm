from os import environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.websocket import router as websocket_router

app = FastAPI()

# CORS 설정 추가
origins = [
    "http://localhost",
    "http://192.168.28.135",
    "http://192.168.0.15:8081",
    "http://192.168.0.15:5173",
    "http://localhost:5173",
    "https://waguwagu.shop",
    # 필요한 경우 다른 출처도 추가 가능
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    # allow_origins=["*"],  # 모든 출처 허용 (주의 필요)
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 HTTP 헤더
)

app.include_router(websocket_router)

@app.get("/alarm")
async def read_root():
    return {"message": "Welcome to the FastAPI application"}

if __name__ == '__main__':
    import uvicorn
    profiles = environ.get("profiles")

    # if profiles != "prod":
    #     app.add_middleware(
    #         CORSMiddleware,
    #         allow_origins=origins,  # 허용할 출처 목록
    #         # allow_origins=["*"],  # 모든 출처 허용 (주의 필요)
    #         allow_credentials=True,
    #         allow_methods=["*"],  # 허용할 HTTP 메서드
    #         allow_headers=["*"],  # 허용할 HTTP 헤더
    #     )

    # 애플리케이션 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)
