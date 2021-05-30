#!/usr/bin/env python3

import gdb

# Breakpoint wrapper class
# A breakpoint class with patented, award-winning score functionality.
class CounterBreakpoint(gdb.Breakpoint):
    # addr is the address of the breakpoint
    # isGood is a boolean, determing if the breakpoint is good-to-hit or bad-to-hit
    # (means a negative breakpoint has isGood = false, and vice versa)
    def __init__(self, addr, isGood):
        self.isGood = isGood
        self.currentScore = 0

        # gdb requires address literals to start with a star
        if addr[0] != "*":
            addr = "*" + addr

        super().__init__(addr)

    # returns the score of this breakpoint
    def GetScore(self):
        return self.currentScore

    # resets the score to 0
    def ResetScore(self):
        self.currentScore = 0

    # returns the score and resets it to 0 afterwards
    def PopScore(self):
        i = self.GetScore()
        self.ResetScore()
        return i

    # the function called by GDB if the breakpoint is hit
    def stop(self):
        if self.isGood:
            self.currentScore += 1
        else:
            self.currentScore -= 1

        # don't break into gdb GUI
        return False

