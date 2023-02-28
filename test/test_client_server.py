r"""
Tests basics of client-server communication
"""
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

import forsake.server
import forsake.client

from .client_server import ClientServer


class TestClientServerCommunication(ClientServer):
    def test_client_without_server(self, socket):
        # When starting a client without a server, the client crashes and
        # terminates immediately.
        client = self.spawn_client(socket=socket)
        client.join()
        assert client.exitcode != 0

    def test_exception(self, socket):
        # An exception on the forked process (the default server throws NotImplementedError) is reported on the client.
        server = self.spawn_server(socket=socket)
        client = self.spawn_client(socket=socket)

        client.join()

        server.kill()
        server.join()

        assert client.exitcode == 1
        assert server.exitcode == -9

    def test_connect(self, socket):
        # If the forked process does nothing, the client exits successfully.
        class Server(forsake.server.Server):
            def startup(self, _):
                pass

        server = self.spawn_server(socket=socket, server=Server)
        client = self.spawn_client(socket=socket)

        client.join()

        server.kill()
        server.join()

        assert client.exitcode == 0
        assert server.exitcode == -9

    def test_keyboard_interrupt(self, socket):
        # When C-c is pressed on the client, the forked process receives it.

        class Server(forsake.server.Server):
            def startup(self, _):
                try:
                    while True:
                        pass
                except KeyboardInterrupt:
                    import sys

                    sys.exit(42)

        class Client(forsake.client.Client):
            def _join(self):
                import signal
                import os

                os.kill(os.getpid(), signal.SIGINT)

                super()._join()

        server = self.spawn_server(socket=socket, server=Server)
        client = self.spawn_client(socket=socket, client=Client)

        client.join()

        server.kill()
        server.join()

        assert client.exitcode == 42
        assert server.exitcode == -9
