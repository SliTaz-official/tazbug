#!/bin/sh
#
# TazBug Plugin - Dashboard
#
. /usr/lib/slitaz/httphelper

case " $(GET) " in
	*\ dashboard\ *)
		d="Dashboard"
		users=$(ls -1 $PEOPLE | wc -l)
		bugs=$(ls -1 $bugdir | wc -l)
		bugsize=$(du -sh $bugdir | awk '{print $1}')
		header
		html_header
		user_box
		if ! check_auth; then
			gettext "You must be logged in to view the dashboard"
			exit 0
		fi
		# Source all plugins configs to get DASHBOARD_TOOLS and ADMIN_TOOLS
		for p in $(ls $plugins)
		do
			. $plugins/$p/$p.conf
		done
		if check_auth && ! admin_user; then
			ADMIN_TOOLS=""
		fi
		cat << EOT
<h2>Dashboard</h2>

<div id="tools">
	$DASHBOARD_TOOLS $ADMIN_TOOLS
</div>

<pre>
Users     : $users
Bugs      : $bugs
Bugsize   : $bugsize
</pre>

<h3>Admin users</h3>
EOT
		# Get the list of administrators
		for u in $(ls $PEOPLE)
		do
			user=${u}
			if admin_user; then
				echo "<a href='?user=$u'>$u</a>"
			fi
		done
		cat << EOT
<h3>$(gettext "Plugins")</h3>
<pre>
EOT
		# List all plugins
		for p in $(ls -1 $plugins)
		do
			. $plugins/$p/$p.conf
			echo "<a href='?$p'>$PLUGIN</a> - $SHORT_DESC"
		done
		echo '</pre>'
		html_footer && exit 0 ;;
esac
