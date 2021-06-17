// xor-o-rama.c
// -------------
//
// This is probably a more real-life (or CTF-like at least) example than single-char and double-trouble.
// The input gets XORed character-wise with a magic value.
//
// Compile with
//  gcc -o xor-o-rama xor-o-rama.c
//
// Let's start easy with the very basics required by BARF:
// - our positve-addr is at 0x0000555555555312 <+360>, where our counter variable is increased (`i++`)
// - our win-addr is at 0x000055555555532c <+386>, where `mov eax,0x0` is preparing the value for `return 0`.
//   Although it is not part of the code below, it is added by the compiler, because our main function needs
//   to return an integer.
// You may wonder why we didn't choose to use a negative address here, although we check for non-equality (!=).
// The relevant code is sitting at 0x0000555555555307 <+349> until 0x0000555555555310 <+358>, by the way.
// That's because the score of this breakpoint will always be -1, as we are only hitting it once, then return.
// Even if we have guessed the correct character (thus, didn't hit it), we will hit it the next round and again
// have a score of -1. So BARF cannot detect a right character until we give an address we only reach when a
// character was correct.
// So, the correct call would be:
//  ./barf.sh --positive-addr 0x555555555312 --win-addr 0x55555555532c ./xor-o-rama
//
// Persistent Mode
// To speed things up, we will dive into persistent mode.
// - our start-addr is at 0x00005555555552d9 <+303>, right after the `fgets(...)` call
// - our end-addr is at 0x0000555555555332 <+392>, the return instruction
// - our buffer sits at 0x7fffffffdf00 on the stack
// So let's get it groovin':
//  ./barf.sh --positive-addr 0x555555555312 --win-addr 0x55555555532c --start-addr 0x5555555552d9 --end-addr 0x555555555332 --buff-addr 0x7fffffffdf00 --persistent ./xor-o-rama
//

#include <stdio.h>

#define BUFSIZE 32

// Takes a string and crypts it in-situ
void crypt(char* b) {
	char magicVal[] = {0x23, 0x42, 0x13, 0x37, 0x0B, 0x0E, 0x0E, 0x0F};
	for(int i = 0; i < BUFSIZE; i++) {
		b[i] = (b[i] ^ magicVal[i % 8]) % 256;
	}
}

int main(int argc, char* argv[]) {
	char buf[BUFSIZE];
	int flag[BUFSIZE] = {0x60, 0x16, 0x55, 0x4c, 0x65, 0x3e, 0x51, 0x78, 0x17, 0x3b, 0x4c, 0x4e, 0x3b, 0x7b, 0x51, 0x2b, 0x13, 0x2e, 0x65, 0x4, 0x6f, 0x51, 0x7a, 0x67, 0x17, 0x36, 0x6e, 0x3d};
	// for debugging purposes, the flag is 'CTF{n0_w4y_y0u_$0lv3d_th4t}' ;)

	// read input
	fgets(buf, BUFSIZE, stdin);

	// crypt input
	crypt(buf);

	// walk input
	int i = 0;
	while(flag[i] != '\0' && i < BUFSIZE) {
		if(buf[i] != flag[i]) return 1; 
		i++;
	}
}

