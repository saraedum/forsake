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

import click

from forsake.server import PluginServer
from forsake.client import PluginClient


@click.command()
@click.option("--socket", required=True, type=click.Path(exists=False))
@click.option("--warmup", required=True, type=click.File("r"))
def server(socket, warmup):
    server = ExecServer(socket, warmup.read())
    try:
        server.start()
    finally:
        import os

        os.unlink(socket)


@click.command()
@click.option("--socket", required=True, type=click.Path(exists=True))
@click.option("--startup", required=True, type=click.File("r"))
def client(socket, startup):
    client = PluginClient(socket)
    client.start(
        {
            "exec": (startup.read(),),
            **client.collect_cwd(),
            **client.collect_env(),
            **client.collect_stdio2(),
        }
    )


class ExecServer(PluginServer):
    def __init__(self, socket, warmup):
        super().__init__(socket)

        self._warmup = warmup

    def startup(self, parameters):
        super().startup(parameters)
        exec(self._code, globals(), globals())

    def startup_exec(self, code):
        self._code = code

    def warmup(self):
        exec(self._warmup, globals(), globals())
