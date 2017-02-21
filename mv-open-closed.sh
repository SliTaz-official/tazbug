#!/bin/sh
#
# From Tazbug 2.1 bugs are stored into $bugdir/open or $bugdir/closed
# This script will move all bugs to the correct directory
#
. /lib/libtaz.sh
check_root
path="$1"

if [ ! "${path}" ]; then
	echo "Usage: $0 path/to/bug" && exit 0
fi

cd ${path}
mkdir -p open closed

for bug in *
do
	if [ -f "${bug}/bug.conf" ]; then
		. ./${bug}/bug.conf
		echo  -n "Mouving bug: ${bug} $STATUS"
		if [ "$STATUS" == "OPEN" ]; then
			mv ${bug} open/ && status
		else
			mv ${bug} closed/ && status
		fi
		unset DESC BUG STATUS PRIORITY CREATOR DATE PKGS
		
	fi
	chown -R www.www *
done

exit 0
