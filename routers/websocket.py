from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException, Query
from services.connection import ConnectionManager
from fastapi.responses import FileResponse
from utils.tts import generate_tts
import os
import logging

router = APIRouter()

manager = ConnectionManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

status_messages = {
    "order-received": "주문이 접수되었습니다.",
    "dispatch-completed": "배차가 완료되었습니다.",
    "delivery-completed": "배달이 완료되었습니다."
}

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

@router.post("/notify/order-completed")
async def notify_order_completed(request: Request):
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


@router.get("/notify/order-status")
async def notify_order_status(order_status: str = Query(..., description="The status of the order")):
    try:
        # 주문 상태에 따른 메시지 설정
        store_message = status_messages.get(order_status)
        if not store_message:
            logger.error(f"Invalid order status: {order_status}")
            raise HTTPException(status_code=400, detail="Invalid order status provided.")

        # TTS 파일 생성
        store_file_path = generate_tts(store_message)
        logger.info(f"Generated TTS file path: {store_file_path}")

        # 파일 존재 여부 확인
        if not os.path.exists(store_file_path):
            logger.error(f"TTS file does not exist: {store_file_path}")
            raise HTTPException(status_code=500, detail="TTS file was not created successfully.")

        # 파일 반환
        response = FileResponse(store_file_path, media_type='audio/mpeg', filename=os.path.basename(store_file_path))

        return response

    except HTTPException as http_error:
        logger.error(f"HTTPException: {http_error.detail}")
        raise http_error

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")