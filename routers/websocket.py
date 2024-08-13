from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from services.connection import ConnectionManager
from fastapi.responses import FileResponse
from utils.tts import generate_tts
import os
import logging

router = APIRouter()

manager = ConnectionManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.websocket("/ws/{client_type}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_type: str, client_id: str):
    await manager.connect(websocket, client_type, client_id)
    logger.info(f"WebSocket connection open for {client_type} with ID {client_id}")
    try:
        while True:
            await websocket.receive_text()  # 클라이언트로부터 메시지를 수신
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_type, client_id)
        logger.info(f"WebSocket connection closed for {client_type} with ID {client_id}")


@router.post("/notify")
async def notify(request: Request):
    try:
        # JSON 데이터 파싱
        data = await request.json()

        # 'store_id' 확인
        store_id = data.get('store_id')
        if not store_id:
            logger.error("Missing 'store_id' in request data")
            raise HTTPException(status_code=400, detail="Missing 'store_id' in request data")

        logger.info(f"Received notify request for store_id: {store_id}")

        # TTS 파일 생성
        customer_message = "주문이 완료되었습니다."
        customer_file_path = generate_tts(customer_message)
        logger.info(f"Generated TTS file path: {customer_file_path}")

        store_message = "주문이 접수되었습니다."
        store_file_path = generate_tts(store_message)

        # 파일 존재 여부 확인
        if not os.path.exists(customer_file_path):
            logger.error(f"TTS file does not exist: {customer_file_path}")
            raise HTTPException(status_code=500, detail="TTS file was not created successfully.")

        # 파일 반환
        response = FileResponse(customer_file_path, media_type='audio/mpeg', filename=os.path.basename(customer_file_path))

        with open(store_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
            await manager.send_personal_message(audio_data, f"store_{store_id}")

        return response

    except HTTPException as http_error:
        logger.error(f"HTTPException: {http_error.detail}")
        raise http_error

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")