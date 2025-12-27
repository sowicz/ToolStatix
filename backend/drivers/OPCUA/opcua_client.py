import asyncio
from asyncua import Client



class OpcUaConnection:
    def __init__(self, url: str):
        self.url = url
        self.client = Client(url=self.url)
        self.connected = False
        self._lock = asyncio.Lock()

    async def connect(self):
        async with self._lock:
            if not self.connected:
                await self.client.connect()
                self.connected = True
                print(f"[OpcUa] ✅ Connected {self.url}")

    async def disconnect(self):
        async with self._lock:
            if self.connected:
                await self.client.disconnect()
                self.connected = False
                print(f"[OpcUa] 🔌 Disconnected {self.url}")

    def is_connected(self) -> bool:
        return self.connected

    def get_client(self) -> Client:
        return self.client
