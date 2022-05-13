#!/usr/bin/env python3
#
# (c) 2021 Martin "maride" Dessauer
#
# BARF, or the Breakpoint-Assisted Rough Fuzzer, is a tool to do intelligent bruteforcing.
# The "intelligent" part comes from watching breakpoints and counting how often they were hit.
# Input is fed into the target program, character-wise, and the character with the best score wins. ;)
# This is done as long as there is a better score to get, and/or until a "win breakpoint" is hit.
# If that's hard to understand on the first read, see some of the examples. ;)
#
# This script is not designed to be directly called. Instead, it gets imported by gdb, via the -x argument.
# Because passing arguments into gdb-python scripts is not trivial, the script _should_ be called by the barf.sh wrapper.
# If you have any reasons to avoid the wrapper script, ... uh well. Your choice. You can call the barf.py script via gdb like this:
# gdb -nx -ex "py barf_positive_addr=False;barf_negative_addr='0x5555555551c0';barf_win_addr='0x5555555551ec';barf_known_prefix='';barf_known_suffix=''" -x barf.py ./beispiel1
#  -nx avoids loading .gdbinit
#  -ex throws your arguments into gdb-python (must be specified _before_ handing in the script
#  -x specifies the location of the script
#  after that comes your executable (./beispiel1 in this case)
#
# In doubt, see https://github.com/maride/barf
# Have fun with the script! :)

# include project path as include path
sys.path.insert(1, barf_path)

from base64 import b64decode

# include project files
from BreakpointManager import BreakpointManager
from TargetManager import TargetManager
from Helper import *
from Bruteforce import *

# main func
def main():
    MOTD()
    gdb.execute("set pagination off")

    # check our args :)
    args = getArguments()

    # Create our breakpoints, managed by the BreakpointManager
    bm = BreakpointManager(args["positiveAddr"], args["negativeAddr"], args["winAddr"], args["loseAddr"])

    # Manage the target with the TargetManager
    tm = TargetManager(bm, args["persistent"], args["startAddr"], args["endAddr"], args["buffAddr"])

    # start the bruteforcing madness ;)
    Bruteforce(bm, tm, args["knownPrefix"], args["knownSuffix"], args["chunksize"], args["charset"])

    # g'night, gdb
    gdb.execute("set confirm off")
    gdb.execute("quit")


# getArguments grabs the arguments from pre-defined variables and returns it as a dict
def getArguments():
    a = dict()
    a["positiveAddr"] = barf_positive_addr
    a["negativeAddr"] = barf_negative_addr
    a["winAddr"] = barf_win_addr
    a["loseAddr"] = barf_lose_addr
    a["startAddr"] = barf_start_addr
    a["endAddr"] = barf_end_addr
    a["buffAddr"] = barf_buff_addr
    a["knownPrefix"] = barf_known_prefix
    a["knownSuffix"] = barf_known_suffix
    a["chunksize"] = barf_chunksize
    a["charset"] = b64decode(barf_charset_b64).decode()
    a["persistent"] = barf_persistent
    return a


# actually execute main function
main()

