#!/bin/sh
#
# This script displays bugs for a given user. A copy is used on SCN to
# display user bugs on profile page with a custom config file to set
# $bugdir.
#
[ -f "$plugins/mybugs/bugdir.conf" ] && . $plugins/mybugs/bugdir.conf
[ "$(GET user)" ] && user="$(GET user)"
url="http://bugs.slitaz.org/"

if fgrep -q -l "CREATOR=\"$user\"" ${bugdir}/*/*/bug.conf; then
	show_more="0"
	echo "<h3>Latest bugs</h3>"
	echo "<pre>"
	for bug in $(fgrep -l "CREATOR=\"$user\"" ${bugdir}/*/*/bug.conf | \
		xargs ls -lt | awk '{print $9}' | head -n 3)
	do
		. ${bug}
		id=$(basename $(dirname $bug))
		cat << EOT
<img src='images/bug.png' alt='' /> \
Bug $id: <a href="${url}?id=$id">$BUG</a> <span class="date">- $DATE</span>
EOT
	done
	echo "</pre>"
fi

#if fgrep -q -l "USER=\"$user\"" ${bugdir}/*/*/msg.*; then
	#show_more="0"
	#echo "<h3>Latest debug messages</h3>"
	#echo "<pre>"
	
	#for msg in $(fgrep -l "USER=\"$user\"" ${bugdir}/*/*/msg.* | \
		#xargs ls -lt | awk '{print $9}' | head -n 4)
	#do
		#. ${msg}
		#id=$(basename $(dirname $msg))
		#msgid=$(echo $msg | cut -d "." -f 2)
		#message="$(fgrep MSG= $msg | cut -d \" -f 2 | cut -c 1-40)"
		#cat << EOT
#<img src='images/bug.png' alt='' /> \
#<a href="${url}?id=$id">Bug $id:</a> <span class="date">$DATE</span> \
#<a href="${url}?id=$id#msg${msgid}">${message}...</a>
#EOT
	#done
	#echo "</pre>"
#fi

if [ "$show_more" ]; then
	echo "<p>"
	if [ "$HTTP_HOST" == "bugs.slitaz.org" ]; then
		echo "<a href='?mybugs&user=$user'>$(gettext 'View all my bugs and messages')</a>"
	else
		echo "$(gettext 'View all my bugs and debug messages on:') "
		echo "<a href='${url}?mybugs&user=$user'>bugs.slitaz.org</a>"
	fi
	echo "</p>"
fi
