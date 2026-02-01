from pathlib import Path

SANDBOX_ROOT = Path("sandbox").resolve()

def is_path_allowed(path: str) -> bool:
    target = Path(path).resolve()
    return SANDBOX_ROOT in target.parents or target == SANDBOX_ROOT
