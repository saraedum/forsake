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

import forsake.rpc


class Server:
    def __init__(self, socket):
        self._socket = socket

    def start(self):
        r"""
        Start the server and listen on the connected host and port.

        This method blocks forever to serve requests.
        """
        self.warmup()

        with forsake.rpc.Server(self._socket) as server:
            server.register_function(self.spawn, "spawn")

            server.serve_forever()

    def spawn(self, client, args):
        r"""
        Fork a process, run its :meth:`startup` with ``args`` and report the
        process ID of the forked process to the caller.
        """
        from forsake.forker import Forker
        forker = Forker(startup=lambda: self.startup(args), on_exit=lambda worker: self.exit(client, worker.exitcode))
        pid = forker.start()
        return pid

    def exit(self, socket, exitcode):
        with forsake.rpc.Client(socket) as proxy:
            proxy.exit(exitcode)

    def warmup(self):
        r"""
        Prepare this process so it is ready to :meth:`spawn` and run
        :meth:`startup` in any forks created.

        Subclasses can override this to perform custom initialization such as
        importing expensive modules.
        """
        pass

    def startup(self, parameters):
        raise NotImplementedError("server does not define a startup method, forked process will terminate immediately")


class PluginServer(Server):
    def startup(self, parameters):
        if parameters is not None:
            from pickle import loads
            parameters = loads(parameters)
            for section, args in parameters.items():
                getattr(self, f"startup_{section}")(*args)

    def startup_stdio(self, stdin, stdout, stderr):
        raise NotImplementedError

    def startup_cwd(self, cwd):
        import os
        os.chdir(cwd)

    def startup_env(self, env):
        raise NotImplementedError
