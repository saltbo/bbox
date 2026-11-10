#!/usr/bin/env python

import os
import subprocess
import sys


def push_charts(directory, repo):
    try:
        tgz_files = [f for f in os.listdir(directory) if f.endswith(".tgz")]
    except OSError as error:
        raise SystemExit(f"Cannot read chart directory {directory}: {error}") from error
    total_files = len(tgz_files)

    for index, filename in enumerate(tgz_files, 1):
        chart_path = os.path.join(directory, filename)
        command = ["helm", "cm-push", chart_path, repo, "-f"]
        if repo.startswith("oci://"):
            command = ["helm", "push", chart_path, repo]

        print(f"↑ Pushing [{index}/{total_files}] {filename} to {repo}")
        try:
            subprocess.run(
                command, check=True, capture_output=True, text=True)
            print(f"✓ Successfully pushed {filename} to {repo}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to push {filename} to {repo}: {e}")
            print(f"Error output: {e.stderr}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Upload Helm chart archives")
    parser.add_argument("directory")
    parser.add_argument("repo")
    args = parser.parse_args()
    push_charts(args.directory, args.repo)


if __name__ == "__main__":
    main()
