"""PostToolUse hook: format a Python file after Claude edits it.

Reads the hook JSON from stdin. Runs `ruff format` on .py files.
Exit 0 always, so a missing formatter never blocks work.
"""

import json
import subprocess
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = (payload.get("tool_input") or {}).get("file_path", "")
    if not path.endswith(".py"):
        return 0
    try:
        subprocess.run(
            [sys.executable, "-m", "ruff", "format", path],
            check=False,
            capture_output=True,
        )
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
