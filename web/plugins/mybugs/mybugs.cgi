#!/bin/sh
#
# TinyCM/TazBug Plugin - List bugs and messages for a given user
#

if [ "$(GET mybugs)" ]; then
	d="My bugs"
	header
	html_header
	user_box
	if ! check_auth; then
		echo "You must be logged to view user bugs" 
		html_footer && exit 0
	fi
	if [ "$(GET user)" ]; then
		user="$(GET user)"
		. $PEOPLE/$user/account.conf
	fi
	echo "<h2><a href='?user=$USER'>$(get_gravatar "$MAIL" 48)</a> $NAME</h2>"
	
	if fgrep -q -l "CREATOR=\"$user\"" ${bugdir}/*/*/bug.conf; then
		echo "<h3>$(gettext 'My bugs')</h3>"
		echo "<pre>"
		for bug in $(fgrep -l "CREATOR=\"$user\"" ${bugdir}/*/*/bug.conf | \
			xargs ls -lt | awk '{print $9}' | head -n 4)
		do
			. ${bug}
			id=$(basename $(dirname $bug))
			cat << EOT
<img src='images/bug.png' alt='' /> \
Bug $id: <a href="?id=$id">$BUG</a> <span class="date">- $DATE</span>
EOT
		done
		echo "</pre>"
	fi
	
	if fgrep -q -l "USER=\"$user\"" ${bugdir}/*/*/msg.*; then
		echo "<h3>Debug messages</h3>"
		echo "<pre>"
		for msg in $(fgrep -l "USER=\"$user\"" ${bugdir}/*/*/msg.* | \
			xargs ls -lt | awk '{print $9}' | head -n 4)
		do
			. ${msg}
			id=$(basename $(dirname $msg))
			msgid=$(echo $msg | cut -d "." -f 2)
			cat << EOT
<img src='images/bug.png' alt='' /> \
<a href="?id=$id">Bug $id:</a> <span class="date">$DATE</span> \
<a href="?id=$id#msg${msgid}">$(echo "$MSG" | cut -c 1-40)...</a>
EOT
		done
		echo "</pre>"
	fi
	
	html_footer && exit 0
fi
