"""Discover the commands provided by bbox."""

import argparse
from importlib.metadata import distribution
from importlib.resources import files


def command_names():
    return sorted(
        entry.name for entry in distribution("saltbo-bbox").entry_points
        if entry.group == "console_scripts"
    )


def zsh_completion():
    script = files("bbox").joinpath("completion.zsh").read_text()
    return script.replace("# __BBOX_COMPDEF__", "compdef _bbox " + " ".join(command_names()))


def main():
    parser = argparse.ArgumentParser(description="Saltbo's personal command-line toolbox")
    parser.add_argument("--version", action="version", version=distribution("saltbo-bbox").version)
    subparsers = parser.add_subparsers(dest="action")
    completion = subparsers.add_parser("completion", help="Print shell completion script")
    completion.add_argument("shell", choices=["zsh"])
    args = parser.parse_args()
    if args.action == "completion":
        print(zsh_completion(), end="")
        return
    print("Commands installed by bbox:")
    for name in command_names():
        print(f"  {name}")
