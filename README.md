TODO: Write something smart here

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
