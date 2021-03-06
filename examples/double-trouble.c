// double-trouble.c
// ----------------
//
// The binary reads some chars from stdin and checks it against a hard-coded flag.
// It checks two chars at a time, this time with a positive counter :)
// If the entered flag is correct, a corresponding message will be printed out.
//
// Compile with
//  gcc -o double-trouble double-trouble.c
//
// Quick binary analysis
//  - load into gdb
//  - execute "start", so the binary is mapped to the final position
//  - execute "disas main"
// Look at 0x00005555555551f5 <+160>. It moves 2 to rbp-0x4, that's the correctChars += 2 below.
// Right after that, the i value is also increased with 2, so double-check to get the right address ;)
// Anyway, that's the right address for --positive-address
// Finding the win function is easy as always. We need to search for the point where puts("yay, ...") is called.
// And that is at 0x000055555555523d!
//
// With the addresses identified above, we call barf with:
//  ./barf.sh --positive-addr 0x5555555551f5 --win-addr 0x55555555523d --chunksize 2 ./double-trouble
//
// While it is possible to solve chunksizes of 2 or even more without persistent mode, it is not avisable.
// Keep in mind that the persistent mode can speed up things around factor 8 or even more.
// So, as a quick exercise, we calculate a few more addresses required for persistent mode.
// Let's pick 0x00005555555551af as start address (right after fgets) and 0x0000555555555248 (ret) as end address.
// You need to debug the binary with GDB to find your buffer address, here it is at 0x7fffffffdef0.
//
// With those additional addresses, we can kickstart barf in persistent mode:
// ./barf.sh --positive-addr 0x00005555555551f5 --win-addr 0x000055555555523d --start-addr 0x00005555555551af --end-addr 0x0000555555555248 --persistent --buff-addr 0x7fffffffdef0 --chunksize 2 ./double-trouble
//
// Enjoy!! ;)
//
// Please note that your addresses will likely differ, e.g. if you edit the source file below.

#include <stdio.h>
#include <string.h>

#define BUFSIZE 32

int main(int argc ,char* argv[]) {
	char buf[BUFSIZE];
	char flag[BUFSIZE] = "CTF{w3_h4ck_1n_du4l1ty!}";

	// read flag
	fgets(buf, BUFSIZE, stdin);

	// walk flag
	int correctChars = 0;
	int i = 0;
	while(buf[i] != '\0' && flag[i] != '\0' && i < BUFSIZE) {
		if(buf[i] == flag[i] && buf[i+1] == flag[i+1]) {
			correctChars += 2;
		}
		i += 2;
	}

	// check flag
	if(strlen(flag) == correctChars) {
		puts("yay, that's the flag! :)");
	}
}

