#!/bin/sh
#
# TazBug Plugin - Dashboard
#

if [ "$(GET dashboard)" ]; then
	d="Dashboard"
	header
	html_header
	user_box
	if ! check_auth; then
		gettext "You must be logged in to view the dashboard"
		exit 0
	fi
	# Source all plugins.conf to get DASHBOARD_TOOLS and ADMIN_TOOLS
	ADMIN_TOOLS=""
	DASHBOARD_TOOLS=""
	for p in $(ls $plugins)
	do
		. $plugins/$p/$p.conf
	done
	if check_auth && ! admin_user; then
		ADMIN_TOOLS=""
	fi
	if check_auth; then
		cat << EOT
<h2>Dashboard</h2>
<pre>
Bugs count       : $(ls_bugs | wc -l)
Messages count   : $(find $bugdir -name msg.* | wc -l)
Database size    : $(du -sh $bugdir | awk '{print $1}')
</pre>
<div id="tools">
	$DASHBOARD_TOOLS $ADMIN_TOOLS
</div>
EOT
	
		# Only for admins
		if check_auth && admin_user; then
			# List all plugins
			cat << EOT
<h3>$(gettext "Plugins:") $(ls $plugins | wc -l)</h3>
<div id="plugins">
<table>
	<thead>
		<td>$(gettext "Name")</td>
		<td>$(gettext "Description")</td>
		<td>$(gettext "Action")</td>
	</thead>
EOT
			for p in $(ls -1 $plugins)
			do
				. $plugins/$p/$p.conf
				cat << EOT
	<tr>
		<td><a href='?$p'>$PLUGIN</a></td>
		<td>$SHORT_DESC</td>
		<td>TODO</td>
	</tr>
EOT
			done
			echo "</table></div>"
		fi
	else
		gettext "You must be logged in to view the dashboard"
	fi
	html_footer && exit 0
fi
