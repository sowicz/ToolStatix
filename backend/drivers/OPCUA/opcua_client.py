import asyncio
import time
from asyncua import Client, Node


class SubscriptionHandler:
    def __init__(self, tag_id):
        self.tag_id = tag_id

    async def datachange_notification(self, node: Node, val, data):
        pass
 

class OpcUaClient:
    def __init__(self, id: int, url: str, polls: int, subscription_handler: SubscriptionHandler):
        self.id = id
        self.url = url
        self.client = Client(url=self.url)
        self.polls = polls
        self.subscription_handler = subscription_handler

        self.subscription = None
        self.subscription_handle = None
        self.running = False


    async def run(self, tag_addresses: list[str]):
        try:
            await self.client.connect()
            self.running = True
            print(f"[Client {self.id}] ✅ Połączono z: {self.url}")

            self.subscription = await self.client.create_subscription(self.polls, self.subscription_handler)
            
            for node_id in tag_addresses:
                node = self.client.get_node(node_id)
                await self.subscription.subscribe_data_change(node)
                print(f"[Client {self.id}] 🔔 Subskrybowano {node_id}")

            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"[Client {self.id}] ❌ Błąd: {e}")

        finally:
            await self.stop()


    async def stop(self):
        if self.subscription and self.subscription_handle:
            await self.subscription.unsubscribe(self.subscription_handle)
            await self.subscription.delete()
            print(f"[Client {self.id}] 🛑 Subskrypcja zakończona.")

        if self.client:
            await self.client.disconnect()
            print(f"[Client {self.id}] 🔌 Rozłączono.")
        self.running = False

    def is_running(self) -> bool:
        return self.running
