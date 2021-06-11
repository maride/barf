#!/usr/bin/env python3

import gdb
import base64

from CheckpointBreakpoint import CheckpointBreakpoint
from PersistenceBreakpoint import PersistenceBreakpoint

# TargetManager is a wrapper around the target itself.
# Tasks include:
#  - Implementing the persistent mode using gdb checkpoints
#  - Feeding input into the binary
# The TargetManager aims to be the one-size-fits-all solution for execution handling.
# That means it is designed to have a unified interface, independent of e.g. persistent mode.
class TargetManager:
    usePersistent = False

    # vars used for persistent mode
    buffAddr = None
    startBreakpoint = None
    endBreakpoint = None
    checkpointIndex = 1
    isRunning = False

    # usePersistent is a boolean, determing if the experimental persistent mode should be used
    # startAddr is the address to start the persistent run
    # endAddr is the address to jump back to startAddr
    # buffAddr is the address of the target buffer to be written in persistent mode
    def __init__(self, usePersistent, startAddr, endAddr, buffAddr):
        self.usePersistent = usePersistent
        
        if usePersistent:
            # parse buffer address to int
            if buffAddr and isinstance(buffAddr, str):
                buffAddr = int(buffAddr, 16)
            self.buffAddr = buffAddr

            # set a breakpoint which will set a checkpoint at its address, the beginning
            self.startBreakpoint = CheckpointBreakpoint(startAddr)
            # breakpoint to reset to the checkpoint on
            self.endBreakpoint = PersistenceBreakpoint(self, endAddr)

    # Runs the binary.
    # If the persistent mode is used, your input will be written into memory directly.
    # If the persistent mode is not used, your input will just be thrown into the binary.
    def Run(self, inp):
        if not self.usePersistent:
            # not running in persistent mode, just feed the input into the binary
            if isinstance(inp, str):
                inp = inp.encode()
            # converting it to base64 is a cheap hack to avoid sanitizing the input ;)
            b = base64.b64encode(inp).decode() 
            gdb.execute("run > /dev/null <<< $(echo %s | base64 -d)" % b, to_string=True)
        else:
            # we're running in persistent mode, let's see if we need to kickstart the executable
            if not self.isRunning:
                # the executable doesn't yet run, so we gotta get it groovin ;)
                # we want to have a single, clean run, so startBreakpoint can set its checkpoint
                # and endBreakpoint can do the first round of resetting. After that, we can
                # start filling our buffer and check if we come near the flag (see block below).
                # That's why we feed /dev/null into the binary: fgets and other stdin read
                # operations should terminate cleanly, avoiding hangs in the executable
                gdb.execute("set confirm off")
                gdb.execute(f"run > /dev/null < /dev/null", to_string=True)
                self.isRunning = True
                # Due to the /dev/null magic above, we haven't yet fed inp into the binary. We
                # don't want to skip it, so we simply continue with the "isRunning==True" block.
                # Please note, as this may cast some confusion, that at this point the binary
                # had a full run-thru, is equipped with checkpoints and breakpoints and is
                # currently in break mode (not running, so to speak), and is at startAddr.
 
            # the executable is already running and reset
            # means we just need to feed input into the binary, then continue running it
            i = gdb.inferiors()[0]
            i.write_memory(self.buffAddr, inp + "\n\0")
            gdb.execute("continue", to_string=True)
            # Reset() will be called by endBreakpoint, we don't need to do that here

    # Resets the target back to the checkpoint set earlier, used for the persistent mode
    # Will be called by endBreakpoint
    def Reset(self):
        # Check if we reached endBreakpoint before hitting startBreakpoint
        if not self.startBreakpoint.isSet:
            print("[!] Reset() called without a startBreakpoint set.")
            print("    Check addresses of start and end!")
            return

        # gdb seems to have a problem with more than 41885 checkpoints.
        # the ID is rising even if checkpoints are deleted on the way.
        # to mitigate this, we start from the beginning and let Run() re-start the executable.
        if self.checkpointIndex > 40000:
            self.checkpointIndex = 1
            self.isRunning = False
            self.startBreakpoint.isSet = False
            return
        
        # jump back to the start
        gdb.execute("restart 1", to_string=True)

        # delete old checkpoint if we ran before
        if self.checkpointIndex > 1:
            gdb.execute(f"delete checkpoint {self.checkpointIndex}", to_string=True)

        # create a fresh copy of checkpoint 1
        gdb.execute("checkpoint", to_string=True)
        # ... and use it
        self.checkpointIndex += 1
        gdb.execute(f"restart {self.checkpointIndex}", to_string=True)

