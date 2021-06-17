# BARF: Breakpoint-Assisted Rough Fuzzer

BARF is a fuzzer utilizing a score calculated from breakpoint hit counts.

## What is it?

BARF feeds input into a target binary and creates a score out of the hits of pre-defined breakpoints.
It is an intelligent input fuzzer for binaries without source code available.

BARFs "intelligent" part comes from watching breakpoints and counting how often they were hit.
Breakpoints have a score, being either positive or negative if it is hit.
Automatically created input is fed into the target program, character-wise, and the character with the best score wins.
This is done as long as there is a better score to get, and/or until a "win breakpoint" is hit.
If that's hard to understand on the first read, see some of the examples. ;)

## Basics

Let's have a look at an example application:

```
#include <stdio.h>
#include <string.h>

int main(int argc, char* argv[]) {
	char buff[16];
	char flag[16] = "BARF{R34DM3.md}";
	fgets(buff, 16, stdin);
	for(int i = 0; i < strlen(buff) - 1; i++) {
		if(buff[i] != flag[i]) {
			return 1;
		}
	}
	puts("you're good at guessing!");
}
```

The application asks for some input and checks it against a hard-coded flag, characterwise.
If the input is not equal to the flag, the application exists silently. If it is correct, a short message is printed.

In a real-life scenario, it would be easy to obtain the hard-coded flag using `strings`.
Let's just acknowledge that this is for the simplicity of the example, and it could be swapped with some strange XOR magic going on - `strings` won't help you anymore then.

Let's start right off with the very basic concepts for barf

### Positive and Negative Address

While both can be set (`--positive-addr` and `--negative-addr`, respectively), in most cases just one is necessary.
You should search for instructions in your objective application which are only reached if a character is correct (positive address) or if a character is wrong (negative address).

Based on the hit count of those addressess, barf is able to calculate a score. Comparing scores of different inputs, barf is able to detect the correct input, stepwise.

In the example above, it would be clever to set the `return 1` command as a negative address - because it will only be hit if `buff[i] != flag[i]`, and we want to avoid that.

### Win Address

While it would be fine to assume that barf found the flag when the hit counter for the negative address is zero, especially in the example above, it might not be that easy to detect in other scenarios.

To give barf the possibility to identify a successful input, the `--win-addr` can be set. It is a instruction region which is only executed when the correct input is found.
In the above example, the `puts(...)` call would be the correct choice for the win address.

## Usage & Examples

For a brief overview over the available arguments and some explanation for them, run

`./barf.sh --help`

For examples, see the `examples` directory. It contains some simple C programs which showcase different capabilities of barf. Make sure to read the source code, as it contains a lot of explanation on the programs, how to analyze different aspects relevant for barf, and finally run barf against them.

