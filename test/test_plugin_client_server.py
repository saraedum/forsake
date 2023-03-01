r"""
Tests the :class:`PluginClient` and :class:`PluginServer` classes
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

import os

from tempfile import TemporaryDirectory

import forsake.server
import forsake.client
from forsake.forker import context

from .client_server import ClientServer


class TestPluginClientServer(ClientServer):
    r"""
    Tests the client and server implementations that contain some predefined
    startup methods.
    """
    def test_cwd(self, socket):
        r"""
        Test that a client that provides its current working directory is
        connected to a forked process that has its current directory set to
        the same value.
        """
        cwd = context.SimpleQueue()

        class Server(forsake.server.PluginServer):
            r"""
            A server that reports its current working directory on startup.
            """
            def startup(self, plugins):
                super().startup(plugins)

                cwd.put(os.getcwd())

        class Client(forsake.client.PluginClient):
            r"""
            A client that requests its current working directory to be copied
            to the forked process.
            """
            def start(self, plugins=None):
                plugins = plugins or {}
                super().start(plugins={**plugins, **self.collect_cwd()})

        with self.spawn_server(socket=socket, server=Server):
            previous = os.getcwd()

            with TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)

                with self.spawn_client(socket=socket, client=Client):
                    pass

                os.chdir(previous)

                assert cwd.get() == tmpdir

    def test_env(self, socket):
        r"""
        Test that a client that provides its current environment variables is
        connected to a forked process that has these environment variables
        restored.
        """
        env = context.SimpleQueue()

        class Server(forsake.server.PluginServer):
            r"""
            A server that reports its current environment variables.
            """
            def startup(self, plugins):
                super().startup(plugins)

                env.put(dict(os.environ))

        class Client(forsake.client.PluginClient):
            r"""
            A client that requests its environment variables to be restored in
            the forked process.
            """
            def start(self, plugins=None):
                plugins = plugins or {}
                super().start(plugins={**plugins, **self.collect_env()})

        with self.spawn_server(socket=socket, server=Server):
            key = "TEST_PLUGIN_CLIENT_SERVER"

            os.environ[key] = "1337"
            with self.spawn_client(socket=socket, client=Client):
                pass

            del os.environ[key]

            assert env.get()[key] == "1337"

    def test_stdio(self, socket, capfd):
        r"""
        Test that the client's stdin, stdout, stderr are connected to the
        forked process.
        """
        class Server(forsake.server.PluginServer):
            r"""
            A server that writes something to stdout.
            """
            def startup(self, plugins):
                super().startup(plugins)

                print("Hello World!", flush=True)

        class Client(forsake.client.PluginClient):
            r"""
            A client that requests its stdio streams to be connected to the
            forked process.
            """
            def start(self, plugins=None):
                plugins = plugins or {}
                super().start(plugins={**plugins, **self.collect_stdio()})

        with self.spawn_server(socket=socket, server=Server):
            with self.spawn_client(socket=socket, client=Client):
                pass

        captured = capfd.readouterr()
        assert captured.out == "Hello World!\n"
