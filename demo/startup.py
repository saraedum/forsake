import sys
sys.argv = ["sage"]

from sage.misc.banner import banner
banner()

from sage.repl.interpreter import SageTerminalApp

app = SageTerminalApp.instance()
app.initialize()
app.start()
