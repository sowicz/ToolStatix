import asyncio
from asyncua import Client


class OpcUaConnection:
    _instance = None

    def __new__(cls, url: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, url: str):
        if self._initialized:
            return
        self.url = url
        self.client = Client(url=self.url)
        self.connected = False
        self._lock = asyncio.Lock()
        self._initialized = True

    async def connect(self):
        async with self._lock:
            if not self.connected:
                await self.client.connect()
                self.connected = True
                print(f"[OpcUaConnection] ✅ Connected {self.url}")
            # else:
            #     print(f"[OpcUaConnection] 🔁 Already connected with {self.url}")

    async def disconnect(self):
        async with self._lock:
            if self.connected:
                await self.client.disconnect()
                self.connected = False
                print(f"[OpcUaConnection] 🔌 Disconnected {self.url}")

    def is_connected(self) -> bool:
        return self.connected

    def get_client(self) -> Client:
        return self.client
