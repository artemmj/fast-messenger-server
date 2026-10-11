import uuid
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from typing import Dict, List, Any


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        """Регистрация нового подключения пользователя"""
        await websocket.accept()
        user_key = str(user_id)
        if user_key not in self.active_connections:
            self.active_connections[user_key] = []
        self.active_connections[user_key].append(websocket)
        print(
            f"📡 [WS] Пользователь {user_key} добавлен в онлайн. "
            f"Всего устройств: {len(self.active_connections[user_key])}"
        )

    def disconnect(self, user_id: uuid.UUID, websocket: WebSocket):
        """Удаление закрытого подключения"""
        user_key = str(user_id)
        if user_key in self.active_connections:
            self.active_connections[user_key].remove(websocket)
            if not self.active_connections[user_key]:
                del self.active_connections[user_key]
        print(f"🔌 [WS] Устройство пользователя {user_key} отключено.")

    async def send_personal_message(self, message: dict, user_id_str: str):
        """Отправить сообщение на все устройства конкретного пользователя по его строковому ID"""
        if user_id_str in self.active_connections:
            safe_message = jsonable_encoder(message)
            for connection in self.active_connections[user_id_str]:
                try:
                    await connection.send_json(safe_message)
                except Exception as e:
                    print(f"🚨 [WS] Ошибка отправки пользователю {user_id_str}: {e}")

    async def broadcast_to_chat(self, message: dict, member_ids: List[Any]):
        """Разослать сообщение списку участников чата"""
        print(
            f"📤 [WS] Запуск рассылки события '{message.get('event')}' для участников: {member_ids}"
        )
        print(
            f"👥 [WS] Сейчас в онлайне строки-ID: {list(self.active_connections.keys())}"
        )

        for member_id in member_ids:
            # Принудительно превращаем ID участника в строку для поиска в словаре онлайна
            member_key = str(member_id)
            if member_key in self.active_connections:
                print(f"🎯 [WS] Отправка пользователю {member_key}")
                await self.send_personal_message(message, member_key)
            else:
                print(f"💤 [WS] Пользователь {member_key} сейчас оффлайн, пропускаем")


ws_manager = ConnectionManager()
