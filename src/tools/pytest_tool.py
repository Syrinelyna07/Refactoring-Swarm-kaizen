import subprocess

def run_pytest(target_dir: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["pytest", target_dir],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr
