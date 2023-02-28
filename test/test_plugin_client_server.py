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

from multiprocessing import SimpleQueue

from .client_server import ClientServer

import forsake.server
import forsake.client


class TestPluginClientServer(ClientServer):
    def test_without_plugins(self, socket):
        server = self.spawn_server(socket=socket)
        client = self.spawn_client(socket=socket)

        client.join()

        server.kill()
        server.join()

        assert client.exitcode == 1
        assert server.exitcode == -9

    def test_cwd(self, socket):
        cwd = SimpleQueue()

        class Server(forsake.server.PluginServer):
            def startup(self, args):
                super().startup(args)

                import os

                cwd.put(os.getcwd())

        class Client(forsake.client.PluginClient):
            def start(self):
                super().start(parameters=self.collect_cwd())

        server = self.spawn_server(socket=socket, server=Server)

        import os

        previous = os.getcwd()

        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                client = self.spawn_client(socket=socket, client=Client)
            finally:
                os.chdir(previous)

            client.join()
            assert cwd.get() == tmpdir

        server.kill()
        server.join()

        assert client.exitcode == 0
        assert server.exitcode == -9

    def test_env(self, socket):
        env = SimpleQueue()

        class Server(forsake.server.PluginServer):
            def startup(self, args):
                super().startup(args)

                import os

                env.put(dict(os.environ))

        class Client(forsake.client.PluginClient):
            def start(self):
                super().start(parameters=self.collect_env())

        server = self.spawn_server(socket=socket, server=Server)

        KEY = "TEST_PLUGIN_CLIENT_SERVER"

        import os

        os.environ[KEY] = "1337"
        try:
            client = self.spawn_client(socket=socket, client=Client)
        finally:
            del os.environ[KEY]

            client.join()
            assert env.get()[KEY] == "1337"

        server.kill()
        server.join()

        assert client.exitcode == 0
        assert server.exitcode == -9

    def test_stdio(self, socket):
        import tempfile

        with tempfile.NamedTemporaryFile() as stdout:

            class Server(forsake.server.PluginServer):
                def startup(self, args):
                    super().startup(args)

                    print("Hello World!")

            class Client(forsake.client.PluginClient):
                def start(self):
                    import sys

                    sys.stdout = open(stdout.name, "w")
                    super().start(parameters=self.collect_stdio())

            server = self.spawn_server(socket=socket, server=Server)

            client = self.spawn_client(socket=socket, client=Client)
            client.join()

            stdout = open(stdout.name, "r")
            assert stdout.read() == "Hello World!\n"

            server.kill()
            server.join()

            assert client.exitcode == 0
            assert server.exitcode == -9
