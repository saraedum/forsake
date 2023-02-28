<p align="center">
    <img alt="logo" src="https://github.com/saraedum/forsake/raw/main/doc/logo.svg?sanitize=true">
</p>
<h1><p align="center">forsake</p></h1>

forsake is a Python library to quickly spawn copies of Python processes that
otherwise take a long time to load.

This library was originally developed for SageMath which typically takes 2s to
start. With this library the startup time can be cut down to about 100ms.

TODO: Write something smart here

## Installation

```
pip install forsake
```

## Performance

With this approach, the startup time of a process can be cut down to the
startup time of Python + the time needed to import some basic networking
modules. Typically, to about 100ms.

Things could be sped up much further by implementing the client process in [C
or C++](https://github.com/saraedum/forsake/issues/5).

## Examples

### Spawn IPython with Preloaded Modules

TODO

### Spawn SageMath

```sh
$ cat warmup.py
import sage.all
$ cat startup.py
from sage.misc.banner import banner
banner()

from sage.repl.interpreter import SageTerminalApp

app = SageTerminalApp.instance()
app.initialize()
app.start()
$ forsake-server --socket /tmp/forsake.socket --warmup warmup.py
$ forsake-client --socket /tmp/forsake.socket --startup startup.py
```
