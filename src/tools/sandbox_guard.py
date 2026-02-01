from pathlib import Path

# Allow both sandbox and test_cases directories
ALLOWED_BASES = [
    Path(__file__).parent.parent.parent / "sandbox",
    Path(__file__).parent.parent.parent / "test_cases"
]

def is_path_allowed(target: str) -> bool:
    try:
        target_path = Path(target).resolve()
        
        # Check if target is within any allowed directory
        for allowed in ALLOWED_BASES:
            allowed_resolved = allowed.resolve()
            if target_path == allowed_resolved or target_path.is_relative_to(allowed_resolved):
                return True
        
        return False
    except (ValueError, OSError):
        return False

def validate_path(target: str, base_dir: str = None) -> bool:
    """Validates if a path is within the allowed directory"""
    if base_dir:
        allowed = Path(base_dir).resolve()
        try:
            target_path = Path(target).resolve()
            return target_path == allowed or target_path.is_relative_to(allowed)
        except (ValueError, OSError):
            return False
    
    # Use default allowed bases
    return is_path_allowed(target)
