#!/bin/bash
#
# wrapper script around barf.py
#
# In doubt, see https://github.com/maride/barf
# Have fun with the script! :)

# setting defaults for the arguments
POSITIVEADDR=""
NEGATIVEADDR=""
WINADDR=""
LOSEADDR=""
STARTADDR=""
ENDADDR=""
BUFFADDR=""
KNOWNPREFIX=""
KNOWNSUFFIX=""
BARFPATH="$(dirname $(realpath $0))/src"
CHUNKSIZE=1
PERSISTENT="False"

# getopt is kind-of unstable across distributions and versions, so we implement it on our own
# hat-tip to https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
while [[ $# -gt 0 ]]; do
	key="$1"

	case $key in
		-p|--positive-addr)
		POSITIVEADDR="$2"
		shift; shift
		;;
		-n|--negative-addr)
		NEGATIVEADDR="$2"
		shift; shift
		;;
		-w|--win-addr)
		WINADDR="$2"
		shift; shift
		;;
		-l|--lose-addr)
		LOSEADDR="$2"
		shift; shift
		;;
		-s|--start-addr)
		STARTADDR="$2"
		shift; shift
		;;
		-e|--end-addr)
		ENDADDR="$2"
		shift; shift
		;;
		--buff-addr)
		BUFFADDR="$2"
		shift; shift
		;;
		-h|--help)
		SHOWHELP=1
		shift
		;;
		-b|--prefix)
		KNOWNPREFIX="$2"
		shift; shift
		;;
		-a|--suffix)
		KNOWNSUFFIX="$2"
		shift; shift
		;;
		-c|--chunksize)
		CHUNKSIZE="$2"
		shift; shift
		;;
		-x|--persistent)
		PERSISTENT="1"
		shift
		;;
		*) # unknown option - we assume it is the target literal
		TARGETFILE="$key"
		shift
		;;
	esac
done

# check if we have all arguments we need
if [ "$POSITIVEADDR" == "" ] && [ "$NEGATIVEADDR" == "" ] || [ "$TARGETFILE" == "" ] ; then
	# nope, missing some args
	SHOWHELP=1
fi

# check if the arguments are valid
if [ ! "$TARGETFILE" == "" ] && [ ! -e "$TARGETFILE" ]; then
	echo "The file $TARGETFILE does not exist."
	SHOWHELP=1
fi

# check if the persistent mode can be used
if [[ "$PERSISTENT" == "1" && ("$STARTADDR" == "" || "$ENDADDR" == "" || "$BUFFADDR" == "" ) ]]; then
	# missing the end address for persistent mode
	echo "You need to specify --start-addr, --end-addr and --buff-addr if you want to use persistent mode."
	echo "Set --start-addr to an address before your input reaches the program (e.g. before fgets())"
	echo "Set --end-addr to an address after the program has checked if the input is good or not (e.g. somewhere after gets('Yay!') and gets('Nay!'))"
	echo "Set --buffer-addr to the address where user input is stored (e.g. the address of b in case of fgets(b, 16, stdin)"
	SHOWHELP=1
fi


# see if the user needs our help
if [ "$SHOWHELP" == 1 ]; then
	echo "Usage: ./barf.sh <options ...> ./path/to/your/binary"
	echo ""
	echo "    BASIC OPTIONS"
	echo "		-p | --positive-addr 0x123456	a location to be counted as good hit"
	echo "		-n | --negative-addr 0x234567	a location to be counted as bad hit"
	echo "		-w | --win-addr      0x345678	a location reached if your input is correct"
	echo "		-l | --lose-addr     0x456789	a location reached if your input is incorrect"
	echo ""
	echo "    PERSISTENT MODE OPTIONS"
	echo "		-x | --persistent		enable the experimental (!) persistent mode"
	echo "		-s | --start-addr    0x56789A	a location directly after your input is fed into the target"
	echo "		-e | --end-addr	     0x6789AB	a location where the to-be-fuzzed logic is done"
	echo "		--buff-addr          0x789ABC	the location where user input is stored"
	echo ""
	echo "    MISC OPTIONS"
	echo "		-b | --prefix        CTF{	a known prefix, e.g. the prefix of your flag"
	echo "		-a | --suffix        }		a known suffix, e.g. the suffix of your flag"
	echo "		-c | --chunksize     2		amount of characters to try at once (default: 1)"
	echo "		-h | --help			a great and useful help message, you should try it!"
	echo ""
	echo "See https://github.com/maride/barf for more information and examples!"
	exit 1
fi

# ready for take-off
gdb --quiet -nx --eval-command "py barf_positive_addr='$POSITIVEADDR';barf_negative_addr='$NEGATIVEADDR';barf_win_addr='$WINADDR';barf_lose_addr='$LOSEADDR';barf_start_addr='$STARTADDR';barf_end_addr='$ENDADDR';barf_buff_addr='$BUFFADDR';barf_known_prefix='$KNOWNPREFIX';barf_known_suffix='$KNOWNSUFFIX';barf_path='$BARFPATH';barf_chunksize=$CHUNKSIZE;barf_persistent=$PERSISTENT" --command barf.py $TARGETFILE

