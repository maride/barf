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
	int isCorrect = 1;

	fgets(buff, 16, stdin);
	for(int i = 0; flag[i] != 0; i++) {
		if(buff[i] != flag[i]) {
			puts("no!");
			isCorrect = 0;
		}
	}

	if(isCorrect) {
		puts("you're good at guessing!");
	}

	return 0;
}
```

The application asks for some input and checks it against a hard-coded flag, characterwise.
If the input is not correct, the application informs the user about that. If it is correct, a short message is printed.

In a real-life scenario, it would be easy to obtain the hard-coded flag using `strings`.
Let's just acknowledge that this is for the simplicity of the example, and it could be swapped with some strange XOR magic going on.

Let's start right off with the very basic concepts of BARF:

### Positive and Negative Address

While both can be set (`--positive-addr` and `--negative-addr`, respectively), in most cases just one is necessary.
You should search for instructions in your objective application which are only reached if a character is correct (positive address) or if a character is wrong (negative address).

Based on the hit count of those addressess, BARF is able to calculate a score. Comparing scores of different inputs, BARF is able to detect the correct input, stepwise.

In the example above, it would be clever to set the `puts("no!");` command as a negative address - because it will only be hit if `buff[i] != flag[i]`, and we want to avoid that.

### Win and Lose Address

While it would be fine to assume that BARF found the flag when the hit counter for the negative address is zero, especially in the example above, it might not be that easy to detect in other scenarios.

To give BARF the possibility to identify a successful input, the `--win-addr` can be set. It is a instruction region which is only executed when the correct input is found.
The same goes for `--lose-addr`; it marks an instruction region which is only executed when the input is wrong.

Don't get yourself confused: `--win-addr` and `--lose-addr` will most likely reside after your compare logic, e.g. the loop. They are just hit once during execution and are not part of the score.
That marks the difference to positive and negative addresses, which may be visited multiple times and are part of the score.
In the above example, the `puts("you're good at guessing!")` call would be the correct choice for the win address, and there is no usable location for a lose address.

Let's modify the example above so we can set either a lose or win address:

```
if(isCorrect) {
	puts("you're good at guessing!");
	// win-addr here!
} else {
	puts("your flag is bad and you should feel bad.");
	// lose-addr here!
}
```

### Persistent mode

Persistent mode is a huge performance booster, as it avoids loading the executable and libraries from disk, linking it, and doing some function calls.
You should use it whenever you can. The performance of guessing may be increased by the factor of 8, more or less.
While this is not a big deal if you have a chunk size of 1, running BARF with a chunk size of 2 or even more will keep you entertained for hours or days.

Persistent mode basically creates a snapshot of your executable at a given location (`--start-addr`) and rolls the memory and registers back to that if you hit another given location (`--end-addr`).
If those values are chosen wisely, you skip:

- loading the executable from disk
- linking the exeuctable and load shared libraries (at least libc) from disk
- init code of your executable
- other overhead, dependent on what your exeuctable does

In the above example you'd typically choose the instruction after the `fgets` call as `--start-addr` and the `return` instruction as `--end-addr`. That will properly cover the logic we want to fuzz.
But, as we are kicking in *after* `fgets`, we need to overwrite the buffer with our generated input. Therefore you need to specifiy the `--buff-addr`: it's the location BARF writes its input to before the executable is run.
Usually it is a stack address, in the example above the address of `buff`. You can easily find it out using gdb: `break fgets`, `continue`, then `print $rdi`.

## Usage & Examples

For a brief overview over the available arguments and some explanation for them, run

`./barf.sh --help`

For examples, see the `examples` directory. It contains some simple C programs which showcase different capabilities of BARF. Make sure to read the source code, as it contains a lot of explanation on the programs, how to analyze different aspects relevant for BARF, and finally run BARF against them.

