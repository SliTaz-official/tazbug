#!/bin/sh
#
# TinyCM/TazBug Plugin - List bugs for a user
#

if [ "$(GET mybugs)" ]; then
	d="My bugs"
	header
	html_header
	user_box
	if ! check_auth; then
		echo "You must logged to view user bugs" 
		html_footer && exit 0
	fi
	echo "<h2><a href='?user=$USER'>$(get_gravatar "$MAIL" 48)</a> $USER</h2>"
	. $plugins/mybugs/user.sh
	html_footer && exit 0
fi
