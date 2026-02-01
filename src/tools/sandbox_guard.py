from pathlib import Path

ALLOWED_BASE = Path(__file__).parent.parent.parent / "sandbox"

def is_path_allowed(target: str) -> bool:
    return Path(target).resolve().is_relative_to(ALLOWED_BASE.resolve())

def validate_path(target: str, base_dir: str = None) -> bool:
    """Validates if a path is within the allowed directory"""
    if base_dir:
        allowed = Path(base_dir).resolve()
    else:
        allowed = ALLOWED_BASE.resolve()
    
    try:
        target_path = Path(target).resolve()
        return target_path.is_relative_to(allowed)
    except (ValueError, OSError):
        return False
