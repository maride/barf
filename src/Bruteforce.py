#!/usr/bin/env python3

from Helper import *

# The charset to try, sorted by the likelihood of a character class
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_!?'#%+/ ;[`@-\".<,*|&$(]=)^>\\:~"

# bruteforces a single character, sandwiched between the known parts.
# Returns the most promising string.
def BruteforceChar(bm, knownPrefix, knownSuffix, chunksize):
    # keyFragment is the variable were we store our found-to-be-correct chars
    keyFragment = ""

    found = False

    ## detect best score
    # we want to get the score for "everything correct except last character".
    # we do this by combining knownPrefix + keyFragment with an "impossible" character.
    # the resulting score is the base for the next round of guessing, hopefully with a single solution better than the score of knownPrefix + keyFragment + impossibleChar.
    # please also note that this will massively fail if the "impossible" character is part of the flag, at the very position it was tested on ... have fun detecting that
    bm.ResetBreakpoints()
    TryInput(knownPrefix + keyFragment + "^" * chunksize + knownSuffix)
    refScore = bm.PopScore()

    # iterate over every character in the charset
    for c in generateCharset(chunksize):
        # generate full input string
        inp = knownPrefix + keyFragment + c + knownSuffix

        # and try it
        bm.ResetBreakpoints()
        TryInput(inp)
        score = bm.PopScore()
        
        # yay, that's a hit
        if score > refScore or bm.HitWin():
            keyFragment += c
            found = True
            break
    
    # check if we found something this round
    return keyFragment if found else False


# Bruteforce calls BruteforceChar until:
# - BruteforceChar was unable to increase the score using any character in the charset, OR
# - the "win" breakpoint is hit :)
def Bruteforce(bm, knownPrefix, knownSuffix, chunksize):
    while True:
        res = BruteforceChar(bm, knownPrefix, knownSuffix, chunksize)
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


# generateCharset returns an iteratable object (string or set) to be used by the bruteforce function.
# the chunksize is the amount of characters to stuff into an entry
def generateCharset(chunksize):
    c = charset
    for i in range(chunksize - 1):
        c = [ a + b for a in c for b in charset ]
    return c

