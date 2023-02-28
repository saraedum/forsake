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


import pytest

from multiprocessing import Process

import forsake.server
import forsake.client


class ClientServer:
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
        process = Process(target=server.start, daemon=False)
        process.server = server
        process.start()
        return process

    def spawn_client(self, socket=None, client=forsake.client.Client):
        client = client(socket or self._socket)
        process = Process(target=client.start, daemon=True)
        process.client = client
        process.start()
        return process
