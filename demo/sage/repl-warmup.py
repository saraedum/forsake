import sage.all

import sys
sys.argv = ["sage"]

from sage.misc.banner import banner
from sage.repl.interpreter import SageTerminalApp
app = SageTerminalApp.instance()
