import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
result = subprocess.run([sys.executable, str(root / "skill_outcome_delta.py"), str(root / "examples" / "runs.json")], capture_output=True, text=True)
if result.returncode != 0:
    raise SystemExit(result.stderr or result.stdout)
print(result.stdout, end="")
