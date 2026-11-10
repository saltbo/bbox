"""Exercise native zsh tab completion in a real terminal without running tools."""

import errno
import os
from pathlib import Path
import pty
import select
import signal
import tempfile
import time
import unittest

from bbox.cli import command_names, zsh_completion


class CompletionTests(unittest.TestCase):
    def test_generated_registration_matches_installed_commands(self):
        script = zsh_completion()
        registration = next(line for line in script.splitlines() if line.startswith("compdef "))
        self.assertEqual(registration.split()[2:], command_names())
        self.assertNotIn("completion-install", registration)
        self.assertNotIn("create-local-script", registration)

    def test_real_zsh_tab_completion(self):
        with tempfile.TemporaryDirectory(prefix="bbox-completion-") as directory:
            root = Path(directory)
            (root / "completion.zsh").write_text(zsh_completion())
            (root / "audio samples").mkdir()
            (root / "mirror.yaml").touch()
            cache = root / "data/bbox/kubectl"
            cache.mkdir(parents=True)
            (cache / "kubectl1.22").touch()
            env = {**os.environ, "TERM": "dumb", "XDG_DATA_HOME": str(root / "data")}
            pid, master = pty.fork()
            if pid == 0:
                os.chdir(root)
                os.execve("/bin/zsh", ["/bin/zsh", "-f"], env)

            def read_until(token):
                output = b""
                deadline = time.monotonic() + 10
                while token not in output:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        self.fail(f"Timed out waiting for {token!r}: {output!r}")
                    readable, _, _ = select.select([master], [], [], remaining)
                    if readable:
                        try:
                            block = os.read(master, 65536)
                        except OSError as error:
                            if error.errno == errno.EIO:
                                self.fail(f"zsh closed unexpectedly: {output!r}")
                            raise
                        if not block:
                            self.fail(f"zsh closed unexpectedly: {output!r}")
                        output += block
                return output

            try:
                setup = (
                    "autoload -Uz compinit; compinit -D; source ./completion.zsh; "
                    "PS1='BBOX_READY> '; "
                    "_capture_bbox_buffer() { print -r -- CAPTURE:$BUFFER; BUFFER=''; zle reset-prompt; }; "
                    "zle -N _capture_bbox_buffer; bindkey '^X^B' _capture_bbox_buffer; "
                    "unsetopt BEEP\n"
                )
                os.write(master, setup.encode())
                read_until(b"\rBBOX_READY> ")
                cases = [
                    ("git-cm --fea", "git-cm --feat "),
                    ("charts-pull --lim", "charts-pull --limit "),
                    ("bbox comp", "bbox completion "),
                    ("bbox completion z", "bbox completion zsh "),
                    ("kubectl-vsw 1.2", "kubectl-vsw 1.22 "),
                    ("charts-mirror mir", "charts-mirror mirror.yaml "),
                    ("mkcourse aud", "mkcourse audio\\ samples/"),
                ]
                for text, expected in cases:
                    with self.subTest(input=text):
                        os.write(master, text.encode() + b"\t")
                        # Let ZLE finish completion before queuing the capture key;
                        # pending input can deliberately interrupt _arguments.
                        while select.select([master], [], [], 0.2)[0]:
                            os.read(master, 65536)
                        os.write(master, b"\x18\x02")
                        output = read_until(b"\rBBOX_READY> ")
                        self.assertIn(("CAPTURE:" + expected).encode(), output)
            finally:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
                os.close(master)


if __name__ == "__main__":
    unittest.main()
