#!/bin/sh
#
# TinyCM/TazBug Plugin - Skeleton
#

if [ "$(GET skel)" ]; then
	d="Skel"
	header
	html_header
	user_box
	cat << EOT
<h2>Plugin Skel</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
</div>
EOT
	echo "<p>$(date)</p>"
	
	# Say we use files in $DATA/skel, sort them by date and simply cat
	# the files, this will create a simple blog :-) We may add posts via
	# uploads or a HTML form.
	
	html_footer
	exit 0
fi
