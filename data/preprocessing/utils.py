import json
from pathlib import Path


def load_json(file_path):
    """Load a JSON file and return its contents."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, file_path):
    """Save data as formatted JSON."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def clean_text(text):
    """Basic text cleaning."""
    if not text:
        return ""

    return " ".join(str(text).split())