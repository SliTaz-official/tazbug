#!/bin/sh
#
# TinyCM/TazBug Plugin - Dashboard
#
. /usr/lib/slitaz/httphelper

case " $(GET) " in
	*\ users\ *)
		d="Users"
		header
		html_header
		user_box
		if check_auth && ! admin_user; then
			gettext "You must be admin to manage users."
			exit 0
		fi
		users=$(ls -1 $PEOPLE | wc -l)
		cat << EOT
<h2>Users: $users</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
</div>
<pre>
EOT
		for u in $(ls $PEOPLE)
		do
			. "${PEOPLE}/${u}/account.conf"
			cat << EOT
$(get_gravatar $MAIL 24) <a href="?user=$USER">$USER</a> | $NAME | $MAIL
EOT
# deluser link
#: <a href="?users&amp;deluser=$USER">$(gettext "delete")</a>
			unset NAME USER 
		done
		echo "</pre>" && exit 0 ;;
	
	*\ online\ *)
		# Show online users based on sessions files.
		d="Online users"
		header
		html_header
		user_box
		if ! check_auth; then
			gettext "You must be logged in to view online user"
			exit 0
		fi
		cat << EOT
<h2>Online users</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
</div>
<pre>
EOT
		for u in $(ls $sessions)
		do
			. "${PEOPLE}/${u}/account.conf"
			cat << EOT
$(get_gravatar $MAIL 24) <a href="?user=$USER">$USER</a> | $NAME
EOT
		done
		echo "</pre>"
		html_footer && exit 0 ;;
		
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
		if check_auth && admin_user; then
			admintools="<a href='?users'>List users</a>"
		fi
		cat << EOT
<h2>Dashboard</h2>
<pre>
Users     : $users
Bugs      : $bugs
Bugsize   : $bugsize
</pre>
<div id="tools">
	<a href='?online'>Online users</a>
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
