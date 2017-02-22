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
		echo "You must be admin to debug" && exit 0
	fi
	cat << EOT
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href="$script?debug">Recheck</a>
</div>
<h2>Debug interface</h2>
<p>
	Check for corrupted config files and empty messages.
</p>
EOT
	# Handle ?debug&del request
	if [ "$(GET del)" ]; then
		id="$(GET del)"
		set_bugdir "$id"
		if [ -d "${bugdir}/${id}" ]; then
			echo -n "<pre>Removing bug ID: $id... "
			rm -rf ${bugdir}/${id}
			echo "Done</pre>"
		fi
	fi

	# Check for bug DB consistency
	echo "<h3>Checking for bug.conf consistency</h3>"
	for id in $(ls_bugs | sort -g)
	do
		set_bugdir "$id"
		if [ $(cat ${bugdir}/${id}/bug.conf | wc -l) != 8 ]; then
			echo "<pre>"
			echo -n "ERROR: bug ID $id"
			# Missing bug.conf
			if [ ! -f "${bugdir}/${id}/bug.conf" ]; then
				echo -n " - Missing: bug.conf"
			fi
			# Empty bug.conf
			if [ -s "${bugdir}/${id}/bug.conf" ]; then
				echo -n " - <a href='?editbug=$id'>Edit</a>"
			else
				echo -n " - Empty: bug.conf"
			fi
			echo " - <a href='?debug&amp;del=$id'>Delete</a>"
			cat ${bugdir}/${id}/bug.conf
			echo "</pre>"
		else
			# Empty values
			. ${bugdir}/${id}/bug.conf
			[ -n "$BUG" ] || miss="1"
			[ -n "$STATUS" ] || miss="1"
			[ -n "$PRIORITY" ] || miss="1"
			[ -n "$CREATOR" ] || miss="1"
			[ -n "$DATE" ] || miss="1"
			if [ "$miss" ]; then
				echo "<pre>"
				echo "ERROR: bug ID $id - Empty variable(s) - <a href='?debug&amp;del=$id'>Delete</a>"
				cat ${bugdir}/${id}/bug.conf
				echo "</pre>"
			fi
		fi
		bugdir=$(dirname $bugdir)
		unset miss
	done
	echo "$(ls_bugs | wc -l) bugs scanned"
	
	# Check for messages consistency
	echo "<h3>Checking for empty messages</h3>"
	msgs=$(find $bugdir -name msg.* | wc -l)
	empty=$(find $bugdir -name msg.* -size 0)
	if  [ "$empty" ]; then
		echo "<pre>"
		cd ${bugdir}
		for msg in */*/msg.*
		do
			if [ ! -s "$msg" ]; then
				# Delete msg ?
				if [ "$(GET delmsgs)" ]; then
					echo "Deleting empty message: $(basename $bugdir)/$msg"
					rm -f ${bugdir}/${msg}
				else
					echo "Found empty message: $(basename $bugdir)/$msg"
				fi
			fi
		done
		if [ ! "$(GET delmsgs)" ]; then
			echo "--&gt; <a href='?debug&amp;delmsgs'>Delete empty messages</a>"
		fi
		echo "</pre>"
	fi
	echo "$msgs messages scanned"
	
	html_footer & exit 0
fi
