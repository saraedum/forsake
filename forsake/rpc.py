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

from http.client import HTTPConnection
import xmlrpc.server
import xmlrpc.client
import socketserver

class UnixStreamHTTPConnection(HTTPConnection):
    def connect(self):
        import socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.host)


class UnixStreamTransport(xmlrpc.client.Transport):
    def __init__(self, socket):
        self._socket = socket
        super().__init__()

    def make_connection(self, host):
        return UnixStreamHTTPConnection(self._socket)


class UnixStreamXMLRPCRequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
    disable_nagle_algorithm = False

    def address_string(self):
        # The builtin address_string fails when used with a Unix Stream.
        # It is only used for logging so we replace it with some dummy.
        return "unix-socket"


class Server(socketserver.UnixStreamServer, xmlrpc.server.SimpleXMLRPCDispatcher):
    def __init__(self, socket):
        self.logRequests = True
        xmlrpc.server.SimpleXMLRPCDispatcher.__init__(self, allow_none=True, encoding=None, use_builtin_types=True)
        socketserver.UnixStreamServer.__init__(self, socket, UnixStreamXMLRPCRequestHandler, bind_and_activate=True)


class Client(xmlrpc.client.ServerProxy):
    def __init__(self, socket):
        super().__init__("http://ignored.invalid", transport=UnixStreamTransport(socket), allow_none=True, use_builtin_types=True)
