from asyncua import Node
import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from db.models.tags_data import TagsData


class DataHandler:
    def __init__(self, tag_id: int, main_nodeid: str, nodeid_to_name: dict[str, str], threshold: float, db: Session):
        self.tag_id = tag_id
        self.main_nodeid = main_nodeid
        self.nodeid_to_name = nodeid_to_name
        self.threshold = threshold
        self.collecting = False
        self.current_batch = []
        self.timestamp = None
        self.db = db
        

    def datachange_notification(self, node: Node, val, data):
        nodeid_str = node.nodeid.to_string()
        tag_name = self.nodeid_to_name.get(nodeid_str, nodeid_str)
        ts = datetime.datetime.now()

        # Check state of collection based on main tag
        if nodeid_str == self.main_nodeid:
            if val > self.threshold and not self.collecting:
                self.collecting = True
                print(f"[{self.tag_id}] 🟢 Start zbierania (main tag: {val})")
                self.timestamp = ts
                self.current_batch = []

            elif val <= self.threshold and self.collecting:
                print(f"[{self.tag_id}] 🔴 Koniec zbierania (main tag: {val})")
                self.save_to_db(self.db)
                self.collecting = False
                self.current_batch = []

        # Collect tags when collecting = True
        if self.collecting:
            record = {
                "timestamp": ts,
                "tag": tag_name,
                "value": val
            }
            self.current_batch.append(record)
            print(f"[{self.tag_id}] 📥 Zebrano: {tag_name} = {val}")


    def save_to_db(self, db: Session):
        if not self.current_batch:
            print(f"[{self.tag_id}] ⚠️ Brak danych do zapisania.")
            return

        print(f"[{self.tag_id}] 💾 Zapisuję {len(self.current_batch)} rekordów do bazy danych")

        # Grupowanie po tag_name
        grouped = defaultdict(list)
        for record in self.current_batch:
            tag_name = record["tag"]  # ← używamy 'tag' zamiast 'nodeid'
            grouped[tag_name].append((record["timestamp"], record["value"]))

        for tag_name, samples in grouped.items():
            timestamps, values = zip(*samples)
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            work_time = int((max(timestamps) - min(timestamps)).total_seconds()) if len(timestamps) > 1 else 0

            data_row = TagsData(
                main_tag_id=self.tag_id,
                tag_name=tag_name,
                min=min_val,
                max=max_val,
                avg=avg_val,
                work_time=work_time
            )

            db.add(data_row)

        db.commit()
        print(f"[{self.tag_id}] ✅ Zapisano {len(grouped)} tagów do bazy.")