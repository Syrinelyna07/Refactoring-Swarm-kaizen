from pathlib import Path
from datetime import datetime
from src.tools.sandbox_guard import is_path_allowed
import shutil

def read_file(path: str) -> str:
    if not is_path_allowed(path):
        raise PermissionError("Forbidden path")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")

def write_file(path: str, content: str):
    if not is_path_allowed(path):
        raise PermissionError("Forbidden path")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def backup_file(path: str) -> str:
    """Crée une sauvegarde avec timestamp"""
    if not is_path_allowed(path):
        raise PermissionError("Forbidden path")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Cannot backup: {path}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}"
    shutil.copy(path, backup_path)
    return str(backup_path)

def get_file_info(path: str) -> dict:
    """Retourne infos sur un fichier"""
    if not is_path_allowed(path):
        raise PermissionError("Forbidden path")
    path = Path(path)
    if not path.exists():
        return {"exists": False}
    stat = path.stat()
    return {
        "exists": True,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": path.is_file(),
        "extension": path.suffix
    }
