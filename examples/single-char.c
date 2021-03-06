// single-char.c
// -------------
//
// The binary reads some chars from stdin and checks it against a hard-coded flag.
// If the entered flag is correct, a corresponding message will be printed out.
//
// Compile with
//  gcc -o single-char single-char.c
//
// Quick binary analysis
//  - load into gdb
//  - start, so the binary is mapped to the final position
//  - execute "disas main"
// Look at 0x00005555555551c7 <+130>. It moves 0 to rbp-0x4, that's the foundFlag = 0 below.
// This is the perfect address for --negative-addr
// Finding the win function is even easier. We just need to search for the point where puts("yay, ...") is called.
// And that is at 0x00005555555551ec. It is not important if you choose the instruction moving the string into
// memory, or the instruction calling puts(), as long as it is inside the correct part of the if() block ;)
//
// With the addresses identified above, we call barf with:
//  ./barf.sh --negative-addr 0x5555555551c7 --win-addr 0x5555555551ec ./single-char
// 
// Persistence Mode
// It is fast, it is easy to use, so why not use it?
// We need to have another look on the binary to find a few more addresses.
// The point directly after fgets() seems like a good value for the start-addr, at 0x5555555551a6.
// end-addr is even easier, let's choose the return point of main(), at 0x555555555218.
// To find out where the buffer is located, start the binary, fill nonsense (32*'A') into it and use gdb's
// `searchmem` command. You will quickly find out that the buffer sits at 0x7fffffffdf00 (stack).
//
// Eqipped with those shiny new values, we can run barf with:
//  ./barf.sh --negative-addr 0x5555555551c7 --win-addr 0x5555555551ec --start-addr 0x5555555551a6 --end-addr 0x555555555218 --buff-addr 0x7fffffffdf00 --persistent ./single-char
//
// Can you notice any performance differences? ;)
//
//
// Please note that your addresses will likely differ, e.g. if you edit the source file below.

#include <stdio.h>
#include <string.h>

#define BUFSIZE 32

int main(int argc ,char* argv[]) {
	char buf[BUFSIZE];
	char flag[BUFSIZE] = "CTF{F00_b4R_B4z_fL4g!}\n";
	int foundFlag = 1;

	// read flag
	fgets(buf, BUFSIZE, stdin);

	// walk flag
	int i = 0;
	while(buf[i] != '\0' && i < BUFSIZE) {
		if(buf[i] != flag[i]) {
			foundFlag = 0;
		}
		i++;
	}

	// check flag
	if(foundFlag) {
		puts("yay, that's the flag! :)");
	} else {
		puts("nay, that's not the flag! :(");
	}
}

