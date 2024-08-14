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

# @router.websocket("/ws/{client_type}/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_type: str, client_id: str):
#     await manager.connect(websocket, client_type, client_id)
#     logger.info(f"WebSocket connection open for {client_type} with ID {client_id}")
#     try:
#         while True:
#             message = await websocket.receive_text()  # 클라이언트로부터 메시지를 수신
#             logger.info(f"Received message from {client_type} {client_id}: {message}")
#             # 여기서 수신된 메시지를 기반으로 추가 처리할 수 있습니다
#     except WebSocketDisconnect:
#         manager.disconnect(websocket, client_type, client_id)
#         logger.info(f"WebSocket connection closed for {client_type} with ID {client_id}")
@router.websocket("/ws/{client_type}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_type: str, client_id: str):
    await manager.connect(websocket, client_type, client_id)
    logger.info(f"WebSocket connection open for {client_type} with ID {client_id}")

    try:
        while True:
            message = await websocket.receive_text()
            logger.info(f"Received message from {client_type} {client_id}: {message}")
            # Echo the message back to the client to ensure the connection is working
            await websocket.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_type, client_id)
        logger.info(f"WebSocket connection closed for {client_type} with ID {client_id}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await websocket.close()

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

        # 파일 존재 여부 확인
        if not os.path.exists(customer_file_path):
            logger.error(f"TTS file does not exist: {customer_file_path}")
            raise HTTPException(status_code=500, detail="TTS file was not created successfully.")

        # 가게에 주문이 접수되었다는 메시지 전송
        message = "주문이 도착했습니다."
        await manager.send_message(message, "store", store_id)
        logger.info(f"Sent message to store {store_id}: {message}")

        # 파일 반환
        response = FileResponse(customer_file_path, media_type='audio/mpeg', filename=os.path.basename(customer_file_path))

        return response

    except HTTPException as http_error:
        logger.error(f"HTTPException: {http_error.detail}")
        raise http_error

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")