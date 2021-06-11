#!/usr/bin/env python3

import gdb

# Enables the typical GDB spam
def EnableLogging():
    gdb.execute("set logging off")


# Disables the typical GDB spam
def DisableLogging():
    return
    gdb.execute("set logging file /dev/null")
    gdb.execute("set logging redirect on")
    gdb.execute("set logging on")


# Prints a small MOTD, hence the name of the function
def MOTD():
    print("+--------------------------------------------+")
    print("| 🥩 BARF - Breakpoint-Assisted Rough Fuzzer |")
    print("|      (c) 2021 Martin 'maride' Dessauer     |")
    print("|           github.com/maride/barf           |")
    print("+--------------------------------------------+")

