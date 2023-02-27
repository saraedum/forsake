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

from multiprocessing import Process


class TestClientServerCommunication:
    HOST="localhost"
    PORT=random.randrange(10000, 2**16-1)

    def spawn_server(self):
        from forsake.server import Server

        server = Server(self.HOST, self.PORT)
        process = Process(target=server.start, args=(), daemon=True)
        process.start()
        return process

    def spawn_client(self, host=HOST, port=PORT):
        from forsake.client import Client

        client = Client(host, port)
        process = Process(target=client.start, args=(), daemon=True)
        process.start()
        return process

    def test_client_without_server(self):
        # When starting a client without a server, the client crashes and
        # terminates immediately.
        client = self.spawn_client()
        client.join()
        assert client.exitcode != 0

    def test_connect(self):
        server = self.spawn_server()
        client = self.spawn_client()

        client.join()

        server.terminate()
        server.join()

        assert client.exitcode == 0
        assert server.exitcode == -15
