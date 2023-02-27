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


class TestClientServerCommunication:
    def test_client_without_server(self):
        # When starting a client without a server, the client crashes and
        # terminates immediately.
        from forsake.client import Client

        from random import randrange
        client = Client(f"http://localhost:{randrange(9000, 2**16)}")

        from multiprocessing import Process
        client_process = Process(target=client.start, args=())
        client_process.start()
        client_process.join()
