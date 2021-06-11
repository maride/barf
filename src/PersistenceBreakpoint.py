#!/usr/bin/env python3

import gdb

# A breakpoint class with reset-to-checkpoint-magic
# "You hit it? We reset it."
class PersistenceBreakpoint(gdb.Breakpoint):
    targetManager = None

    # tm is apointer to TargetManager so we can Reset() the executable
    # endAddr is the address on which we want to jump back
    def __init__(self, tm, endAddr):
        self.targetManager = tm

        # gdb requires address literals to start with a star
        if endAddr[0] != "*":
            endAddr = "*" + endAddr

        # actually create breakpoint
        super().__init__(endAddr)

        # avoid spamming "Breakpoint X, ..." when hit
        self.silent = True

    def stop(self):
        # do the checkpoint thing
        self.targetManager.Reset()
        # we return true so we still break - we will 'continue' later, after we wrote memory.
        return True

