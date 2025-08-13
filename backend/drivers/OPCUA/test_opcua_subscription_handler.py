import time
from asyncua import Node


class SubscriptionHandler:
    """
        Testing subscription handler to log in .txt file values 
        client_id = id of tag from DB
        filename = to save values in
    """
    def __init__(self, tag_id: int):
        self.tag_id = tag_id
        self.filename = f"tag_{self.tag_id}.txt"

    async def datachange_notification(self, node: Node, val, data):
        with open(self.filename, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {val}\n")
        # print(f"[Client {self.client_id}] 🔔 Zmiana wartości: {node}, Nowa wartość: {val}")