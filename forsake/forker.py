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

import multiprocessing


context = multiprocessing.get_context("fork")


class Forker:
    def __init__(self, startup, on_exit):
        self._startup = startup
        self._on_exit = on_exit

    def start(self):
        # We have to set daemon=False so that the Forker can have the worker as a child process.
        pid = context.SimpleQueue()
        watcher = context.Process(target=self.spawn, args=(pid,), name="watcher", daemon=False)
        watcher.start()
        pid, worker = pid.get()
        return pid, worker

    def spawn(self, pid):
        # worker = context.Process(target=self.work, args=(), name="worker", daemon=True)
        import pty
        (worker, fd) = pty.fork()

        if worker == 0:
            self.work()

            import sys
            sys.exit(0)

        pid.put((worker, fd))
        import os
        os.waitpid(worker, 0)
        self._on_exit(worker)

    def work(self):
        self._startup()
