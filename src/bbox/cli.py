"""Discover the commands provided by bbox."""

import argparse
from importlib.metadata import distribution


def main():
    parser = argparse.ArgumentParser(description="Saltbo's personal command-line toolbox")
    parser.add_argument("--version", action="version", version=distribution("saltbo-bbox").version)
    parser.parse_args()
    print("Commands installed by bbox:")
    for entry in sorted(distribution("saltbo-bbox").entry_points, key=lambda item: item.name):
        if entry.group == "console_scripts":
            print(f"  {entry.name}")
