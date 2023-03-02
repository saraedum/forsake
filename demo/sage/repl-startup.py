import sage.all

from sage.misc.banner import banner
from sage.repl.interpreter import SageTerminalApp

banner()
app = SageTerminalApp.instance()
app.initialize()
app.start()
