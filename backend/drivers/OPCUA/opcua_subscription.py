import asyncio
import time
from asyncua import Client, Node


class SubscriptionHandler:
    def __init__(self, tag_id):
        self.tag_id = tag_id

    async def datachange_notification(self, node: Node, val, data):
        pass
 

class OpcuaSubscription:
    def __init__(self, id: int, client: Client, polls: int, subscription_handler: SubscriptionHandler):
        self.id = id
        self.client = client
        self.polls = polls
        self.subscription_handler = subscription_handler

        self.subscription = None
        self.subscription_handle = None
        self.running = False
        self.subscription_handles = []
        self._lock = asyncio.Lock()


    async def run(self, tag_addresses: list[str]):
        try:
            async with self._lock:
                if self.subscription is None:
                    self.subscription = await self.client.create_subscription(self.polls, self.subscription_handler)
                    self.running = True
                for node_id in tag_addresses:
                    node = self.client.get_node(node_id)
                    # await self.subscription.subscribe_data_change(node)
                    handle = await self.subscription.subscribe_data_change(node)
                    self.subscription_handles.append(handle)
                    print(f"[Client {self.id}] 🔔 Subskrybowano {node_id}")

        except Exception as e:
            print(f"[Client {self.id}] ❌ Błąd: {e}")



    async def stop(self):
        if self.subscription:
            for handle in self.subscription_handles:
                try:
                    await self.subscription.unsubscribe(handle)
                except Exception as e:
                    print(f"[Client {self.id}] ⚠️ Błąd przy odsubskrybowaniu: {e}")
            await self.subscription.delete()
            print(f"[Client {self.id}] 🛑 Subskrypcja zakończona.")
        self.running = False

    def is_running(self) -> bool:
        return self.running
