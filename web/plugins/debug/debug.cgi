#!/bin/sh
#
# TazBug Plugin - Debug Tazbug :-)
#

if [ "$(GET debug)" ]; then
	d="Debug"
	header
	html_header
	user_box
	if check_auth && ! admin_user; then
		gettext "You must be admin to debug"
		exit 0
	fi
	cat << EOT
<h2>Debug interface</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
</div>
EOT
	# Handle ?debug&del request
	if [ "$(GET del)" ]; then
		id="$(GET del)"
		if [ -d "${bugdir}/${id}" ]; then
			echo -n "<pre>Removing bug ID: $id... "
			rm -rf ${bugdir}/${id}
			echo "Done</pre>"
		fi
	fi

	# Check for bug DB consistency
	echo "<h3>Checking for bug.conf consistency</h3>"
	for id in $(ls $bugdir | sort -g)
	do
		if [ $(cat ${bugdir}/${id}/bug.conf | wc -l) != 8 ]; then
			echo "<pre>"
			echo -e "ERROR: bug ID $id - <a href='?edit=$id'>Edit</a>\
 - <a href='?debug&amp;del=$id'>Delete</a>\n"
			cat ${bugdir}/${id}/bug.conf
			echo "</pre>"
		fi
	done
	echo "$(ls -1 $bugdir | wc -l) bugs scanned"
	
	html_footer & exit 0
fi
