from pathlib import Path
from src.tools.sandbox_guard import is_path_allowed

def read_file(path: str) -> str:
    if not is_path_allowed(path):
        raise PermissionError("Forbidden path")
    return Path(path).read_text(encoding="utf-8")

def write_file(path: str, content: str):
    if not is_path_allowed(path):
        raise PermissionError("Forbidden path")
    Path(path).write_text(content, encoding="utf-8")
