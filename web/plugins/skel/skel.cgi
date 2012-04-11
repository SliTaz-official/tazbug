#!/bin/sh
#
# TinyCM/TazBug Plugin - Skeleton
#
. /usr/lib/slitaz/httphelper

if [ "$(GET skel)" ]; then
	d="Skel"
	header
	html_header
	user_box
	echo "<h2>Plugin Skel</h2>"
	echo $(date)
	
	# Say we use files in $DATA/skel, sort them by date and simply cat
	# the files, this will create a simple blog :-) We may add post via
	# uploads or an HTML form.
	
	html_footer
	exit 0
fi
