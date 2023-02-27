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

class Server:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def start(self):
        r"""
        Start the server and listen on the connected host and port.

        This method blocks forever to serve requests.
        """
        from xmlrpc.server import SimpleXMLRPCServer
        with SimpleXMLRPCServer((self._host, self._port)) as server:
            server.register_function(self.spawn, "spawn")            

            server.serve_forever()

    def spawn(self):
        return 0
