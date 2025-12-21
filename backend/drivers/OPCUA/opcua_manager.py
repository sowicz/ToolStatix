import asyncio
from backend.drivers.OPCUA.opcua_client import OpcUaConnection


class OpcUaConnectionManager:
    _connections: dict[str, OpcUaConnection] = {}
    _lock = asyncio.Lock()


    @classmethod
    async def get_connection(cls, server_url: str) -> OpcUaConnection:
        async with cls._lock:
            if server_url not in cls._connections:
                cls._connections[server_url] = OpcUaConnection(server_url)

            conn = cls._connections[server_url]

        if not conn.is_connected():
            await conn.connect()

        return conn


    @classmethod
    def is_connected(cls, server_url: str) -> bool:
        conn = cls._connections.get(server_url)
        return conn.is_connected() if conn else False
