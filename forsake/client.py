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

class Client:
    def __init__(self, url):
        self._url = url

    def start(self):
        r"""
        Connect to the server.

        This method blocks until the server signals to us that the forked
        process has terminated.
        """
        from xmlrpc.client import ServerProxy
        with ServerProxy(self._url) as proxy:
            proxy.connect()

            while True:
                pass
