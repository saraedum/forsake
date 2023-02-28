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

import forsake.rpc


class Client:
    def __init__(self, socket):
        self._socket = socket
        self._server = None
        self._exitcode = None

    def start(self, args=None):
        r"""
        Connect to the server.

        This method blocks until the server signals to us that the forked
        process has terminated.
        """
        with forsake.rpc.Client(self._socket) as proxy:
            from xmlrpc.server import SimpleXMLRPCServer

            from random import randrange
            port = randrange(2**13, 2**16)

            from tempfile import TemporaryDirectory
            with TemporaryDirectory() as sockdir:
                import os.path
                socket = os.path.join(sockdir, "socket")

                with forsake.rpc.Server(socket) as server:
                    self._server = server
                    server.register_function(self.on_exit, "exit")

                    pid = proxy.spawn(socket, args)

                    from sys import stderr
                    stderr.write(f"Forked process with PID {pid}")

                    server.serve_forever()

        import sys
        sys.exit(self._exitcode)

    def on_exit(self, exitcode):
        self._exitcode = exitcode

        from threading import Thread
        Thread(target=self._server.shutdown).start()
