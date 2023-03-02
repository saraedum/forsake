<p align="center">
    <img alt="logo" src="https://github.com/saraedum/forsake/raw/main/doc/logo.svg?sanitize=true">
</p>
<h1><p align="center">forsake</p></h1>

forsake is a Python library to quickly spawn copies of Python processes that
otherwise take a long time to load.

This library was originally developed for SageMath which typically takes 2s to
start. With this library the startup time can be cut down to about 100ms.

The idea is to start the expensive process once and then use the
[fork](https://docs.python.org/3/library/os.html#os.fork) system call to spawn
more copies quickly. Since copies then have their stdin, stdout, stderr
attached to the calling terminal, it appears is if the process were a child of
the calling shell.

Not all operating systems do implement `fork`. In particular, we cannot use
this approach to quickly clone a process on Windows. It should work fine on all
Unixes such as Linux and macOS. (But it does not actually work on macOS, see [#6](https://github.com/saraedum/forsake/issues/6).)

## Installation

```
pip install forsake
```

## Performance

With the approach here the startup time of a process can be cut down to the
startup time of Python + the time needed to import some basic networking
modules. Typically, to about 100ms.

Things could be sped up much further by implementing the client process in [C
or C++](https://github.com/saraedum/forsake/issues/5).

## Security

The forking server is listening on a Unix socket which is created securely. To
our knowledge there are no security problems with this approach.

## Examples

forsake comes with a command line interface `forsake-server` and
`forsake-client`. These were written as demo applications. For production use,
you probably want to write a specialized command line interface that suits your
use case.

Note that all the example files used below can be found in the
[`demo/`](./demo) directory.

### Spawn a SageMath Executor

On modern systems, the SageMath startup takes about 2 seconds. The time is
mostly spent importing lots of Python libraries that get pulled in by
`sage.all` even if only a very small fraction of these libraries is used.

Here, we create a forking server that preloads `sage.all` and then execute a
computation in a fresh fork of this server when a client requests it:

```sh
$ cat demo/sage/computation.py
from sage.all import ZZ
print(ZZ(1337).factor())
$ forsake-server --socket /tmp/forsake.socket --warmup demo/sage/executor.py  # this command hangs while it is waiting for connections
$ time sage demo/sage/computation.py
7 * 191  # takes about 2s
$ forsake-client --socket /tmp/forsake.socket --startup demo/sage/computation.py
7 * 191  # takes about 100ms
```

### Spawn a SageMath REPL

```sh
$ forsake-server --socket /tmp/forsake.socket --warmup demo/sage/repl-warmup.py  # this command hangs whil it is waiting for connections
$ forsake-client --socket /tmp/forsake.socket --startup demo/sage/repl-startup.py
sage: 1337.factor()
7 * 191
```

## Development

Any recent version of Python should work to develop forsake. The few required
dependencies can be conveniently installed with mamba:

```
mamba env create -f environment.yml
mamba activate forsake-dev
```

To install a development version of forsake, run `pip install -e .` in this
directory.

To run the test suite, run `pytest` in this directy.
