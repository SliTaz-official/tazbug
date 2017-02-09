#!/bin/sh
#
# Extract bug description from a bug.conf file to create a desc.txt file
#
. /lib/libtaz.sh
check_root
path="$1"

if [ ! "${path}" ]; then
	echo "Usage: $0 path/to/bug" && exit 0
fi

cd ${path}

for bug in *
do
	 . ./${bug}/bug.conf
	 echo  -n "Converting bug: ${bug} "
	 echo "${DESC}" > ${bug}/desc.txt
	 chown www.www ${bug}/desc.txt
	 status
done

exit 0
