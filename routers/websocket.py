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
    customer_file_path = None
    try:
        try:
            data = await request.json()
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        store_id = data.get('store_id')
        if not store_id:
            logger.error("Missing 'store_id' in request data")
            raise HTTPException(status_code=400, detail="Missing 'store_id' in request data")

        logger.info(f"Received notify request for store_id: {store_id}")

        customer_message = "주문이 완료되었습니다."
        customer_file_path = generate_tts(customer_message)
        logger.info(f"Generated TTS file path: {customer_file_path}")

        if not os.path.exists(customer_file_path):
            logger.error(f"Failed to generate TTS or file does not exist: {customer_file_path}")
            raise HTTPException(status_code=500, detail="TTS file was not created successfully.")

        response = FileResponse(customer_file_path, media_type='audio/mpeg', filename=os.path.basename(customer_file_path))

        return response

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")