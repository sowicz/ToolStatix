import random
import time
import threading


class RandomValueWorker:
    def __init__(self, id: int, filename="output.txt"):
        self.id = id
        self.filename = filename
        self.running = False
        self.thread = None

    def _save_to_file(self, value: float):
        with open(self.filename, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {value}\n")

    def _run(self):
        while self.running:
            value = round(random.uniform(10.000, 30.000), 3)
            self._save_to_file(value)
            time.sleep(1)
        print(f"[Worker {self.id}] Zatrzymano.")

    def start(self):
        if self.running:
            return False
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if not self.running:
            return False
        self.running = False
        if self.thread:
            self.thread.join()
        return True

    def is_running(self):
        return self.running
