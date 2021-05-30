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


# The charset to try, sorted by the likelihood of a character class
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_!?"


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
        return self.winB.GetScore() != 0


# Enables the typical GDB spam
def EnableLogging():
    gdb.execute("set logging off")


# Disables the typical GDB spam
def DisableLogging():
    gdb.execute("set logging file /dev/null")
    gdb.execute("set logging redirect on")
    gdb.execute("set logging on")


# Runs a given input through GDB
def TryInput(inp):
    gdb.execute(f"run 2>/dev/null 1>&2 <<< $(echo '{inp}')")


# Prints a small MOTD, hence the name of the function
def MOTD():
    print("+--------------------------------------------+")
    print("| 🥩 BARF - Breakpoint-Assisted Rough Fuzzer |")
    print("|      (c) 2021 Martin 'maride' Dessauer     |")
    print("|           github.com/maride/barf           |")
    print("+--------------------------------------------+")


# bruteforces a single character, sandwiched between the known parts.
# Returns the most promising string.
def BruteforceChar(bm, knownPrefix, knownSuffix):
    # keyFragment is the variable were we store our found-to-be-correct chars
    keyFragment = ""

    found = False

    ## detect best score
    # we want to get the score for "everything correct except last character".
    # we do this by combining knownPrefix + keyFragment with an "impossible" character.
    # the resulting score is the base for the next round of guessing, hopefully with a single solution better than the score of knownPrefix + keyFragment + impossibleChar.
    # please also note that this will massively fail if the "impossible" character is part of the flag, at the very position it was tested on ... have fun detecting that
    bm.ResetBreakpoints()
    TryInput(knownPrefix + keyFragment + "^" + knownSuffix)
    refScore = bm.PopScore()

    # iterate over every character in the charset
    for c in charset:
        # generate full input string
        inp = knownPrefix + keyFragment + c + knownSuffix

        # and try it
        bm.ResetBreakpoints()
        TryInput(inp)
        score = bm.PopScore()
        
        # yay, that's a hit
        if score > refScore:
            keyFragment += c
            found = True
            break
    
    # check if we found something this round
    return keyFragment if found else False


# Bruteforce calls BruteforceChar until:
# - BruteforceChar was unable to increase the score using any character in the charset, OR
# - the "win" breakpoint is hit :)
def Bruteforce(bm, knownPrefix, knownSuffix):
    while True:
        res = BruteforceChar(bm, knownPrefix, knownSuffix)
        if res is False:
            # no character from the given charset matched. :(
            EnableLogging()
            print("BARF is done with the charset and was unable to increase the score further. Issues may be:")
            print(" - Your charset is too small")
            print(" - Your chunk size is too small")
            print(" - Your breakpoints are off")
            print(" - The specified binary doesn't operate round-wise, so it's impossible to calculate a proper score")
            if len(knownPrefix) > 0:
                print(f"Anyway, I stopped with the key '{knownPrefix}[...mystery!...]{knownSuffix}'")
                print("Maybe that helps you. Have a good night!")
            DisableLogging()
            return knownPrefix + knownSuffix
        else:
            # good input, we stepped further
            knownPrefix += res
            EnableLogging()
            print(f"Found new scorer, we're now at '{knownPrefix}[...]{knownSuffix}'")
            DisableLogging()

            # let's examine it further - check if we hit the win breakpoint :)
            if bm.HitWin():
                EnableLogging()
                print("BARF found the flag - or at least managed to hit the 'win' breakpoint!")
                print(f"Winning guess for the flag is '{knownPrefix + knownSuffix}'")
                DisableLogging()
                return knownPrefix + knownSuffix


# getArguments grabs the arguments from pre-defined variables and returns it as a dict
def getArguments():
    a = dict()
    a["positiveAddr"] = barf_positive_addr
    a["negativeAddr"] = barf_negative_addr
    a["winAddr"] = barf_win_addr
    a["knownPrefix"] = barf_known_prefix
    a["knownSuffix"] = barf_known_suffix
    return a

# main func
def main():
    MOTD()
    gdb.execute("set pagination off")

    # check our args :)
    args = getArguments()

    # Create our breakpoints, managed by the BreakpointManager
    bm = BreakpointManager(args["positiveAddr"], args["negativeAddr"], args["winAddr"])

    # start the bruteforcing madness ;)
    DisableLogging()
    Bruteforce(bm, args["knownPrefix"], args["knownSuffix"])

    # g'night, gdb
    gdb.execute("quit")


# actually execute main function
main()

