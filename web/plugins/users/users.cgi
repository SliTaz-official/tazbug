#!/bin/sh
#
# TinyCM/TazBug Plugin - Users profile and admin
#

case " $(GET) " in
	*\ users\ *)
		d="Users"
		header
		html_header
		user_box
		if check_auth && ! admin_user; then
			gettext "You must be admin to manage users"
			exit 0
		fi
		users=$(ls -1 $PEOPLE | wc -l)
		cat << EOT
<h2>Users: $users</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href='?logged'>Logged users</a>
</div>
<pre>
EOT
		for u in $(ls $PEOPLE)
		do
			# Skip corrupted accounts
			if ! [ -f "${PEOPLE}/${u}/account.conf" ]; then
				echo "${u} : Missing account.conf"
				continue
			fi
			. "${PEOPLE}/${u}/account.conf"
			cat << EOT
$(get_gravatar $MAIL 24) <a href="?user=$USER">$USER</a> | $NAME | $MAIL
EOT
# deluser link
#: <a href="?users&amp;deluser=$USER">$(gettext "delete")</a>
			unset NAME USER 
		done
		echo "</pre>" 
		html_footer && exit 0 ;;
	
	*\ logged\ *)
		# Show online users based on sessions files.
		d="Logged users"
		header
		html_header
		user_box
		if ! check_auth; then
			gettext "You must be logged in to view online users"
			exit 0
		fi
		cat << EOT
<h2>Logged users</h2>
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
esac
