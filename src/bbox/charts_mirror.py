#!/usr/bin/env python

import yaml
import subprocess
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Mirror charts using a YAML configuration")
    parser.add_argument("config", nargs="?", default="mirror.yaml")
    args = parser.parse_args()
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as error:
        parser.error(f"Cannot read configuration {args.config}: {error}")

    target = config['target']
    charts = config['charts']

    for chart in charts:
        name = chart['name']
        url = chart['url']
        since = chart.get('since')
        limit = chart.get('limit')
        local_path = f'charts/{name}'

        # Download charts
        download_command = [
            sys.executable, '-m', 'bbox.charts_pull', url, local_path]
        if since:
            download_command += ["--since", str(since)]
        if limit:
            download_command += ["--limit", str(limit)]
        print(f"Running: {' '.join(download_command)}")
        subprocess.run(download_command, check=True)

        # Upload charts
        remote = target
        if target.startswith("oci://") or target.startswith("http"):
            remote = "{}/{}".format(target, name)

        upload_command = [
            sys.executable, '-m', 'bbox.charts_push', local_path, remote]
        print(f"Running: {' '.join(upload_command)}")
        subprocess.run(upload_command, check=True)


if __name__ == '__main__':
    main()
