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
        self._fds = {}

    def start(self):
        r"""
        Start the server and listen on the connected host and port.

        This method blocks forever to serve requests.
        """
        self.warmup()

        with forsake.rpc.Server(self._socket) as server:
            server.register_function(self.spawn, "spawn")
            server.register_function(self.interrupt, "interrupt")

            server.serve_forever()

    def spawn(self, client, args):
        r"""
        Fork a process, run its :meth:`startup` with ``args`` and report the
        process ID of the forked process to the caller.
        """
        from forsake.forker import Forker

        self._client = client

        forker = Forker(
            startup=lambda: self.startup(args),
            on_exit=lambda worker: self.exit(client, -1),
        )
        pid, fd = forker.start()
        self._fds[pid] = fd

        from sys import stderr

        print(f"Forked worker with PID {pid}", file=stderr, flush=True)

        return pid

    def interrupt(self, pid):
        fd = self._fds[pid]

        import os
        # This does not work :( inapporpriate ioctl for device
        # pid = os.tcgetpgrp(fd)

        import signal
        os.kill(pid, signal.SIGINT)


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
        raise NotImplementedError(
            "server does not define a startup method, forked process will terminate immediately"
        )


class PluginServer(Server):
    def startup(self, plugins):
        if plugins is not None:
            from pickle import loads

            plugins = loads(plugins)
            for section, args in plugins.items():
                getattr(self, f"startup_{section}")(*args)

    def startup_stdio(self, stdin, stdout, stderr):
        import sys

        socket = self._client

        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        sys.stdin = open(stdin, "r")
        sys.stdout = open(stdout, "w")
        sys.__stdout__ = sys.stdout
        sys.stderr = open(stderr, "w")

        import fcntl

        ioctl_ = fcntl.ioctl
        def ioctl(fd, *args, **kwargs):
            print("ioctl", fd)
            return ioctl_(fd, *args, **kwargs)

        fcntl.ioctl = ioctl

        fcntl_ = fcntl.fcntl
        def fcntl__(fd, *args, **kwargs):
            print("fcntl", fd)
            return fcntl_(fd, *args, **kwargs)

        fcntl.fcntl = fcntl__

        sys.stdin.isatty = lambda: True
        sys.stdout.isatty = lambda: True
        sys.stderr.isatty = lambda: True

        import IPython.terminal.interactiveshell
        IPython.terminal.interactiveshell._is_tty = True
        IPython.terminal.interactiveshell._use_simple_prompt = False

        import termios
        def tcgetattr_(fileno):
            with forsake.rpc.Client(socket) as proxy:
                return proxy.tcgetattr()
        termios.tcgetattr = tcgetattr_

        def tcsetattr_(fileno, *args, **kwargs):
            with forsake.rpc.Client(socket) as proxy:
                return proxy.tcsetattr(*args, **kwargs)
        termios.tcsetattr = tcsetattr_

        import os
        # os.setpgrp()

        os.tcsetpgrp(0, os.getpid())

    def startup_cwd(self, cwd):
        import os

        os.chdir(cwd)

    def startup_env(self, env):
        import os

        for key in os.environ:
            del os.environ[key]
        for key, value in env.items():
            os.environ[key] = value

    def startup_stdio2(self, stdin, stdout, stderr):
        self.startup_stdio(stdin, stdout, stderr)
