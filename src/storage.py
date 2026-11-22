import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_records(file_name):
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        return []
    records = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(f"{file_name} must contain a JSON list.")
    return records


def save_records(file_name, records):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / file_name
    file_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )