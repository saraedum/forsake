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

from .client_server import ClientServer

import forsake.server
import forsake.client
from forsake.forker import context


class TestPluginClientServer(ClientServer):
    def test_without_plugins(self, socket):
        with self.spawn_server(socket=socket):
            with self.spawn_client(socket=socket, exitcode=1):
                pass

    def test_cwd(self, socket):
        cwd = context.SimpleQueue()

        class Server(forsake.server.PluginServer):
            def startup(self, args):
                super().startup(args)

                import os

                cwd.put(os.getcwd())

        class Client(forsake.client.PluginClient):
            def start(self):
                super().start(parameters=self.collect_cwd())

        with self.spawn_server(socket=socket, server=Server):
            import os

            previous = os.getcwd()

            from tempfile import TemporaryDirectory
            with TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)

                with self.spawn_client(socket=socket, client=Client):
                    pass

                os.chdir(previous)

                assert cwd.get() == tmpdir

    def test_env(self, socket):
        env = context.SimpleQueue()

        class Server(forsake.server.PluginServer):
            def startup(self, args):
                super().startup(args)

                import os

                env.put(dict(os.environ))

        class Client(forsake.client.PluginClient):
            def start(self):
                super().start(parameters=self.collect_env())

        with self.spawn_server(socket=socket, server=Server):
            KEY = "TEST_PLUGIN_CLIENT_SERVER"

            import os

            os.environ[KEY] = "1337"
            with self.spawn_client(socket=socket, client=Client):
                pass

            del os.environ[KEY]

            assert env.get()[KEY] == "1337"

    def test_stdio(self, socket, capfd):
        class Server(forsake.server.PluginServer):
            def startup(self, args):
                super().startup(args)

                print("Hello World!", flush=True)

        class Client(forsake.client.PluginClient):
            def start(self):
                super().start(parameters=self.collect_stdio())

        with self.spawn_server(socket=socket, server=Server):
            with self.spawn_client(socket=socket, client=Client):
                pass

        captured = capfd.readouterr()
        assert captured.out == "Hello World!\n"
