

class CleanupHandler:
    def __init__(self, trigger_value=True):
        self.trigger_value = trigger_value

    async def datachange_notification(self, node, val, data):
        if val == self.trigger_value:
            print("🧹 Trigger cleanup/report logic")
            await self.generate_report()

    async def generate_report(self):
        # np. agregacja danych i zapis do pliku
        print("📄 Generowanie raportu...")
