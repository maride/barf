#!/usr/bin/env python3

from CounterBreakpoint import CounterBreakpoint
import gdb

# Abstracts the breakpoints into a single class:
#  - returns the score of the positive and negative breakpoint
#  - checks if the win function was hit
#  - takes care of resetting all breakpoints with a single call
class BreakpointManager:
    posB = None
    negB = None
    winB = None

    def __init__(self, pAddr, nAddr, wAddr):
        if pAddr:
            self.posB = CounterBreakpoint(pAddr, True)
        if nAddr:
            self.negB = CounterBreakpoint(nAddr, False)
        if wAddr:
            self.winB = CounterBreakpoint(wAddr, True)

    def GetScore(self):
        score = 0
        if self.posB:
            score += self.posB.GetScore()
        if self.negB:
            score += self.negB.GetScore()
        return score

    def ResetBreakpoints(self):
        if self.posB:
            self.posB.ResetScore()
        if self.negB:
            self.negB.ResetScore()
        if self.winB:
            self.winB.ResetScore()

    def PopScore(self):
        score = 0
        if self.posB:
            score += self.posB.PopScore()
        if self.negB:
            score += self.negB.PopScore()
        return score

    def HitWin(self):
        if self.winB:
            return self.winB.GetScore() != 0

