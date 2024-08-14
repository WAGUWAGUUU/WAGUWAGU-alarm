from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.customer_connections: Dict[str, List[WebSocket]] = {}
        self.store_connections: Dict[str, List[WebSocket]] = {}
        self.driver_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_type: str, client_id: str):
        await websocket.accept()
        if client_type == "customer":
            if client_id not in self.customer_connections:
                self.customer_connections[client_id] = []
            self.customer_connections[client_id].append(websocket)
        elif client_type == "store":
            if client_id not in self.store_connections:
                self.store_connections[client_id] = []
            self.store_connections[client_id].append(websocket)
        elif client_type == "rider":
            if client_id not in self.driver_connections:
                self.driver_connections[client_id] = []
            self.driver_connections[client_id].append(websocket)

        # 로그 추가
        logger.info(f"Connected {client_type} with ID {client_id}. Total connections: {len(self.store_connections.get(client_id, []))}")

    def disconnect(self, websocket: WebSocket, client_type: str, client_id: str):
        if client_type == "customer" and client_id in self.customer_connections:
            self.customer_connections[client_id].remove(websocket)
            if not self.customer_connections[client_id]:  # 리스트가 비어 있으면
                del self.customer_connections[client_id]  # 해당 ID 삭제
        elif client_type == "store" and client_id in self.store_connections:
            self.store_connections[client_id].remove(websocket)
            if not self.store_connections[client_id]:  # 리스트가 비어 있으면
                del self.store_connections[client_id]  # 해당 ID 삭제
        elif client_type == "rider" and client_id in self.driver_connections:
            self.driver_connections[client_id].remove(websocket)
            if not self.driver_connections[client_id]:  # 리스트가 비어 있으면
                del self.driver_connections[client_id]  # 해당 ID 삭제

    # async def send_message(self, message: str, client_type: str, client_id: str):
    #     connections = []
    #     if client_type == "customer" and client_id in self.customer_connections:
    #         connections = self.customer_connections[client_id]
    #     elif client_type == "store" and client_id in self.store_connections:
    #         connections = self.store_connections[client_id]
    #     elif client_type == "rider" and client_id in self.driver_connections:
    #         connections = self.driver_connections[client_id]
    #
    #     for connection in connections:
    #         await connection.send_text(message)
    async def send_message(self, message: str, client_type: str, client_id: str):
        connections = []
        if client_type == "customer" and client_id in self.customer_connections:
            connections = self.customer_connections[client_id]
        elif client_type == "store" and client_id in self.store_connections:
            connections = self.store_connections[client_id]
        elif client_type == "rider" and client_id in self.driver_connections:
            connections = self.driver_connections[client_id]

        for connection in connections:
            try:
                await connection.send_text(message)
                logger.info(f"Message sent to {client_type} with ID {client_id}: {message}")
            except Exception as e:
                logger.error(f"Failed to send message to {client_type} with ID {client_id}: {e}")


    def is_connected(self, client_type: str, client_id: str) -> bool:
        """클라이언트가 현재 연결되어 있는지 확인"""
        if client_type == "customer":
            connected = client_id in self.customer_connections and bool(self.customer_connections[client_id])
        elif client_type == "store":
            connected = client_id in self.store_connections and bool(self.store_connections[client_id])
        elif client_type == "rider":
            connected = client_id in self.driver_connections and bool(self.driver_connections[client_id])
        else:
            connected = False

        # 로그 추가
        logger.info(f"Checking connection for {client_type} with ID {client_id}: {connected}")
        return connected