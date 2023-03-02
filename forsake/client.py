# ********************************************************************
#  This file is part of forsake
#
#        Copyright (C) 2023 Julian Rüth
#
#  forsake is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  forsake is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with forsake. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

import contextlib
import forsake.rpc


class Client:
    def __init__(self, socket):
        self._socket = socket
        self._server = None
        self._exitcode = None
        self.pid = None

    def start(self, args=None):
        r"""
        Connect to the server.

        This method blocks until the server signals to us that the forked
        process has terminated.
        """
        with self._create_client() as remote:
            with self._create_server() as socket:
                self._request_fork(remote, socket, args)
                self._handle_signals(remote)
                self._join()

        import sys

        sys.exit(self._exitcode)

    def interrupt(self):
        print("INT")
        import signal

        self.signal(signal.SIGINT)

    def kill(self):
        import signal

        self.signal(signal.SIKILL)

    def signal(self, signal):
        import os

        print("Signaling", self.pid)
        os.kill(self.pid, signal)

    def on_exit(self, exitcode):
        print("EXIT")
        self._exitcode = exitcode

        from threading import Thread

        Thread(target=self._server.shutdown).start()

    @contextlib.contextmanager
    def _create_client(self):
        with forsake.rpc.Client(self._socket) as remote:
            yield remote

    @contextlib.contextmanager
    def _create_server(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as sockdir:
            import os.path

            socket = os.path.join(sockdir, "socket")

            with forsake.rpc.Server(socket) as server:
                self._server = server

                server.register_function(self.on_exit, "exit")
                server.register_function(self.on_tcgetattr, "tcgetattr")
                server.register_function(self.on_tcsetattr, "tcsetattr")

                yield socket

    def on_tcgetattr(self, *args, **kwargs):
        import sys
        import termios
        return termios.tcgetattr(sys.stdin.fileno(), *args, **kwargs)

    def on_tcsetattr(self, *args, **kwargs):
        import sys
        import termios
        return termios.tcsetattr(sys.stdin.fileno(), *args, **kwargs)

    def _request_fork(self, remote, socket, args):
        self.pid = remote.spawn(socket, args)

        from sys import stderr

        print(f"Attached to process with PID {self.pid}", file=stderr, flush=True)

    def _handle_signals(self, remote):
        import signal

        signal.signal(signal.SIGINT, lambda *args: remote.interrupt(self.pid))

    def _join(self):
        self._server.serve_forever()


class PluginClient(Client):
    def start(self, plugins=None):
        from pickle import dumps

        super().start(dumps(plugins))

    @classmethod
    def collect_stdio(cls):
        import sys
        import os

        stdin = f"/proc/{os.getpid()}/fd/{sys.stdin.fileno()}"
        stdout = f"/proc/{os.getpid()}/fd/{sys.stdout.fileno()}"
        stderr = f"/proc/{os.getpid()}/fd/{sys.stderr.fileno()}"

        return {"stdio": (stdin, stdout, stderr)}

    @classmethod
    def collect_cwd(cls):
        import os

        return {"cwd": (os.getcwd(),)}

    @classmethod
    def collect_env(cls):
        import os

        return {"env": (dict(os.environ),)}

    @classmethod
    def collect_stdio2(cls):
        import tempfile
        import os

        tmpdir = tempfile.mkdtemp()
        stdin = os.path.join(tmpdir, "stdin")
        stdout = os.path.join(tmpdir, "stdout")
        stderr = os.path.join(tmpdir, "stderr")

        os.mkfifo(stdin)
        os.mkfifo(stdout)
        os.mkfifo(stderr)

        import forsake.forker

        import subprocess

        def read_stdin():
            os.system(f"cat -u /dev/fd/0 > {stdin}")

        def write_stdout():
            os.system(f"cat -u {stdout} > /dev/fd/1")

        def write_stderr():
            os.system(f"cat -u {stderr} > /dev/fd/2")

        forsake.forker.context.Process(target=read_stdin, name="cat stdin", daemon=True).start()
        forsake.forker.context.Process(target=write_stdout, name="cat stdout", daemon=True).start()
        forsake.forker.context.Process(target=write_stderr, name="cat stderr", daemon=True).start()

        return {"stdio2": (stdin, stdout, stderr)}
