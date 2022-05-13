#!/usr/bin/env python3

from itertools import permutations

from Helper import *
from TargetManager import TargetManager

# The charset to try, sorted by the likelihood of a character class
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_!?'#%+/ ;[`@-\".<,*|&$(]=)^>\\:~"

# bruteforces a single character, sandwiched between the known parts.
# Returns the most promising string.
def BruteforceChar(bm, tm, knownPrefix, knownSuffix, chunksize):
    # keyFragment is the variable were we store our found-to-be-correct chars
    keyFragment = ""

    # detect best score
    refScore = Calibrate(bm, tm, knownPrefix + keyFragment, knownSuffix, chunksize)
    if refScore is False:
        return False

    # iterate over every character in the charset
    for c in permutations(charset, chunksize):
        # construct a string out of the charset bit
        c = "".join(c)

        # generate full input string
        inp = knownPrefix + keyFragment + c + knownSuffix

        # and try it
        score = RunAndScore(bm, tm, inp)
        
        # yay, that's a hit
        if score > refScore or bm.HitWin():
            keyFragment += c
            break
    
    # check if we found something this round
    return keyFragment or False


# Bruteforce calls BruteforceChar until:
# - BruteforceChar was unable to increase the score using any character in the charset, OR
# - the "win" breakpoint is hit :)
def Bruteforce(bm, tm, knownPrefix, knownSuffix, chunksize):
    while True:
        res = BruteforceChar(bm, tm, knownPrefix, knownSuffix, chunksize)
        if res is False:
            # no character from the given charset matched. :(
            EnableLogging()
            print("BARF is done with the charset and was unable to increase the score further. Issues may be:")
            print(" - Your charset is too small")
            print(" - Your chunk size is too small")
            print(" - Your breakpoints are off")
            print(" - Your prefix and/or suffix is wrong")
            print(" - The specified binary doesn't operate round-wise, so it's impossible to calculate a proper score")
            if len(knownPrefix) > 0:
                print(f"Anyway, I stopped with the key '{knownPrefix}[...mystery!...]{knownSuffix}'")
                print("Maybe that helps you. Have a good night!")
            DisableLogging()
            return knownPrefix + knownSuffix
        else:
            # good input, we stepped further
            # let's examine it - check if we hit the win breakpoint :)
            if bm.HitWin() or not bm.HitLose():
                EnableLogging()
                print("BARF found the flag - or at least managed to hit the 'win' breakpoint!")
                print(f"Winning guess for the flag is '{knownPrefix + knownSuffix}'")
                DisableLogging()
                return knownPrefix + knownSuffix

            # No win breakpoint hit, but still a good step forward - proceed
            knownPrefix += res
            EnableLogging()
            print(f"Found new scorer, we're now at '{knownPrefix}[...]{knownSuffix}'")
            DisableLogging()


# Finds out the base score when filling the binary with partly correct chars (e.g. the already found-to-be-correct prefix)
# It does this by combining knownPrefix + keyFragment and knownSuffix with an "impossible" character.
# We're only able to proceed if every character (except one) returns the same score - the "except one" score is the winner ;)
# Note that this function will massively fail if the "impossible" character is part of the flag, at the very position it was tested on ... have fun detecting that
def Calibrate(bm, tm, prefix, suffix, chunksize):
    score1 = RunAndScore(bm, tm, prefix + '^' * chunksize + suffix)
    score2 = RunAndScore(bm, tm, prefix + '`' * chunksize + suffix)

    if score1 == score2:
        # we found a stable score, return it
        return score1
    else:
        # There is some kind of inconsistency in the executable, stop here.
        EnableLogging()
        print(score1)
        print(score2)
        print("BARF was unable to calibrate.")
        print("While this may have multiple reasons, the most realistic are:")
        print(" - The specified binary is not solvable on a round-based approach")
        print("   -> reverse the binary further - is there some shuffeling mechanism in place?")
        print(" - The 'no way that character is part of the flag' charset is actually part of the flag")
        DisableLogging()
        return False


# Runs the given input and returns its breakpoint score
def RunAndScore(bm, tm, inp):
    bm.ResetBreakpoints()
    tm.Run(inp)
    return bm.PopScore()


# generateCharset returns an iteratable object (string or set) to be used by the bruteforce function.
# the chunksize is the amount of characters to stuff into an entry
def generateCharset(chunksize):
    if chunksize == 1:
        yield "".join(c)
    else:
        for c in charset:
            yield c + generateCharset(chunksize - 1)
