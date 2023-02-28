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
                self._handle_signals()
                self._join()

        import sys
        sys.exit(self._exitcode)

    def interrupt(self):
        import signal
        self.signal(signal.SIGINT)

    def kill(self):
        import signal
        self.signal(signal.SIKILL)

    def signal(self, signal):
        import os
        os.kill(self.pid, signal)

    def on_exit(self, exitcode):
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

                yield socket

    def _request_fork(self, remote, socket, args):
        self.pid = remote.spawn(socket, args)

        from sys import stderr
        stderr.write(f"Forked process with PID {self.pid}")

    def _handle_signals(self):
        import signal
        signal.signal(signal.SIGINT, lambda *args: self.interrupt())

    def _join(self):
        self._server.serve_forever()


class PluginClient(Client):
    def start(self, parameters={}):
        from pickle import dumps
        super().start(dumps(parameters))

    @classmethod
    def collect_stdio(cls):
        raise NotImplementedError

    @classmethod
    def collect_cwd(cls):
        import os
        return {"cwd": (os.getcwd(),)}

    @classmethod
    def collect_env(cls):
        raise NotImplementedError
