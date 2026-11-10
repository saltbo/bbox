"""Verify installed entry points and shell dispatch without real side effects."""

from contextlib import redirect_stdout
from importlib import import_module
from importlib.metadata import distribution
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from bbox import charts_mirror, shell


class InstallationTests(unittest.TestCase):
    def test_all_entry_points_resolve_and_shell_resources_exist(self):
        for entry in distribution("saltbo-bbox").entry_points:
            if entry.group != "console_scripts":
                continue
            with self.subTest(command=entry.name):
                self.assertTrue(callable(entry.load()))
                if entry.value == "bbox.shell:main":
                    script = Path(shell.__file__).parent / "scripts" / entry.name
                    self.assertTrue(script.is_file())
                    interpreter = "/bin/bash" if "bash" in script.read_text().splitlines()[0] else "/bin/sh"
                    subprocess.run([interpreter, "-n", str(script)], check=True)

    def test_shell_dispatch_preserves_arguments(self):
        with patch.object(sys, "argv", ["/tmp/bin/git-fire", "a spaced argument", "--help"]):
            with patch("bbox.shell.os.execv") as execute:
                shell.main()
        interpreter, arguments = execute.call_args.args
        self.assertEqual(interpreter, "/bin/sh")
        self.assertEqual(arguments[2:], ["a spaced argument", "--help"])
        self.assertTrue(arguments[1].endswith("/scripts/git-fire"))

    def test_installed_shell_wrapper_preserves_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "lima"
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\nexit 23\n')
            fake.chmod(0o755)
            command = Path(sys.executable).parent / "buildctl"
            result = subprocess.run([str(command), "a spaced argument"], env={**os.environ, "PATH": directory}, text=True, capture_output=True)
        self.assertEqual(result.returncode, 23)
        self.assertEqual(result.stdout.splitlines(), ["sudo", "buildctl", "a spaced argument"])

    def test_mirror_uses_installed_modules_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "mirror.yaml"
            config.write_text('target: oci://example.invalid/charts\ncharts:\n  - name: sample\n    url: https://example.invalid\n    since: 2025-01-01\n    limit: 2\n')
            with patch.object(sys, "argv", ["charts-mirror", str(config)]):
                with patch("bbox.charts_mirror.subprocess.run") as run, redirect_stdout(io.StringIO()):
                    charts_mirror.main()
        pull, push = [call.args[0] for call in run.call_args_list]
        self.assertEqual(pull[:3], [sys.executable, "-m", "bbox.charts_pull"])
        self.assertIn("2025-01-01", pull)
        self.assertEqual(push[:3], [sys.executable, "-m", "bbox.charts_push"])
        self.assertEqual(push[-1], "oci://example.invalid/charts/sample")


if __name__ == "__main__":
    unittest.main()
