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
KNOWNPREFIX=""
KNOWNSUFFIX=""
BARFPATH="$(dirname $(realpath $0))/src"

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
if [ ! -e "$TARGETFILE" ]; then
	echo "The file $TARGETFILE does not exist."
	exit 1
fi

# see if the user needs our help
if [ "$SHOWHELP" == 1 ]; then
	echo "Usage: ./barf.sh"
	echo "		-p | --positive-addr 0x123456	a location to be counted as good hit"
	echo "		-n | --negative-addr 0x789ABC	a location to be counted as bad hit"
	echo "		-w | --win-addr      0xDEF042	a location reached if your input is correct"
	echo "		-< | --prefix        CTF{	a known prefix, e.g. the prefix of your flag"
	echo "		-> | --suffix        }		a known suffix, e.g. the suffix of your flag"
	echo "		-h | --help			a great and useful help message, you should try it!"
	echo "		./path/to/your/crackme		the path to the target to be fuzzed"
	echo "Note that you need to either specify --positive-addr or --negative-addr and your target of course."
	exit 1
fi

# ready for take-off
gdb --quiet -nx --eval-command "py barf_positive_addr='$POSITIVEADDR';barf_negative_addr='$NEGATIVEADDR';barf_win_addr='$WINADDR';barf_known_prefix='$KNOWNPREFIX';barf_known_suffix='$KNOWNSUFFIX';barf_path='$BARFPATH'" --command barf.py $TARGETFILE

