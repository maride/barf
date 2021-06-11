#!/usr/bin/env python3

import gdb

# A simple breakpoint to set a checkpoint at the given address
# After that, it doesn't do a thing anymore
class CheckpointBreakpoint(gdb.Breakpoint):
    # The address to break on
    isSet = False

    def __init__(self, startAddr):
        # gdb requires address literals to start with a star
        if startAddr[0] != "*":
            startAddr = "*" + startAddr
        
        super().__init__(startAddr)

    def stop(self):
        if not self.isSet:
            gdb.execute("checkpoint")
            self.isSet = True
        return False

