import subprocess

def run_pylint(target_dir: str) -> str:
    result = subprocess.run(
        ["pylint", target_dir],
        capture_output=True,
        text=True
    )
    return result.stdout
