"""Run the packaged shell tools without depending on executable file modes."""

import os
from pathlib import Path
import sys


def main():
    name = Path(sys.argv[0]).name
    script = Path(__file__).parent / "scripts" / name
    if not script.is_file():
        raise SystemExit(f"Unknown bbox shell command: {name}")
    with script.open() as stream:
        shebang = stream.readline().strip()
    interpreter = "/bin/bash" if "bash" in shebang else "/bin/sh"
    os.execv(interpreter, [interpreter, str(script), *sys.argv[1:]])
