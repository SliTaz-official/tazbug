#!/bin/sh
#
# TinyCM/TazBug Plugin - Dashboard
#
. /usr/lib/slitaz/httphelper

case " $(GET) " in
	*\ users\ *)
		d="Dashboard"
		header
		html_header
		user_box
		if ! admin_user; then
			gettext "You must be admin in to manage users."
			exit 0
		fi
		users=$(ls -1 $PEOPLE | wc -l)
		cat << EOT
<h2>Users: $users</h2>
<pre>
EOT
		for u in $(ls $PEOPLE)
		do
			#. ${PEOPLE}/${u}/account.conf
			. "${PEOPLE}/${u}/account.conf"
			cat << EOT
<img src="images/avatar.png" /> <a href="?user=$USER">$USER</a> | $NAME
EOT
# deluser link
#: <a href="?users&amp;deluser=$USER">$(gettext "delete")</a>
			unset NAME USER 
		done
		echo "</pre>" && exit 0 ;;
		
	*\ dashboard\ *)
		d="Dashboard"
		header
		html_header
		user_box
		if ! check_auth; then
			gettext "You must be logged in to view the dashboard."
			exit 0
		fi
		if admin_user; then
			admintools="<a href='?users'>Users</a>"
		fi
		users=$(ls -1 $PEOPLE | wc -l)
		bugsize=$(du -sh $bugdir | awk '{print $1}')
		cat << EOT
<h2>Dashboard</h2>
<pre>
Users     : $users
Bugsize   : $bugsize
</pre>
<div id="tools">
$admintools
</div>
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
		for p in $(ls -1 $plugins)
		do
			. $plugins/$p/$p.conf
			echo "<a href='?$p'>$PLUGIN</a> - $SHORT_DESC"
		done
		echo '</pre>'
		html_footer
		exit 0 ;;
esac
