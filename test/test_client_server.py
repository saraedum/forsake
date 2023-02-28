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

import random
import pytest

from multiprocessing import Process

import forsake.server
import forsake.client


class TestClientServerCommunication:
    @pytest.fixture(autouse=True)
    def socket(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as sockdir:
            import os.path
            self._socket = os.path.join(sockdir, "socket")
            yield

    def spawn_server(self, server=forsake.server.Server):
        server = server(self._socket)
        # We have to set daemon=False so that the server can fork child processes.
        process = Process(target=server.start, args=(), daemon=False)
        process.start()
        return process

    def spawn_client(self, socket=None, client=forsake.client.Client):
        client = client(socket or self._socket)
        process = Process(target=client.start, args=(), daemon=True)
        process.start()
        return process

    def test_client_without_server(self):
        # When starting a client without a server, the client crashes and
        # terminates immediately.
        client = self.spawn_client()
        client.join()
        assert client.exitcode != 0

    def test_exception(self):
        # An exception on the forked process (the default server throws NotImplementedError) is reported on the client.
        server = self.spawn_server()
        client = self.spawn_client()

        client.join()

        server.terminate()
        server.join()

        assert client.exitcode == 1
        assert server.exitcode == -15

    def test_connect(self):
        # If the forked process does nothing, the client exits successfully.
        class Server(forsake.server.Server):
            def startup(self, _):
                pass

        server = self.spawn_server(server=Server)
        client = self.spawn_client()

        client.join()

        server.terminate()
        server.join()

        assert client.exitcode == 0
        assert server.exitcode == -15
