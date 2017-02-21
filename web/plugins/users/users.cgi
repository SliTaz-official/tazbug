#!/bin/sh
#
# TinyCM/TazBug Plugin - Users profile and admin
#

# Display user public profile.
public_people() {
	echo "</pre>"
}

# Display authenticated user profile. TODO: change password
auth_people() {
	cat << EOT
Email      : $MAIL
</pre>

<div id="tools">
	$PLUGINS_TOOLS
	<a href="$script?modprofile">$(gettext "Modify profile")</a>
</div>
EOT
}

# List last active users. Usage: last_users NB
list_last_users() {
	count=${1}
	echo "<h3>Last $count active users</h3>"
	echo "<pre>"
	find ${PEOPLE} -name "last" | xargs ls -1t | head -n ${count} | while read last;
	do
		dir="$(dirname $last)"
		date="$(cat $last)"
		u=$(basename $dir)
		. "${PEOPLE}/${u}/account.conf"
	cat << EOT
$(get_gravatar $MAIL 24) $date  : <a href="?user=$u">$u</a> | $NAME
EOT
	done
	echo "</pre>"
}

case " $(GET) " in
	*\ users\ *)
		d="Users"
		header
		html_header
		user_box
		# Admin only
		if admin_user; then
			tools="<a href='$script?userslist'>Users list</a>"
		fi
		# Logged users
		if check_auth; then
			cat << EOT
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href='$script?lastusers'>Last users</a>
	$tools
</div>
<h2>${d}</h2>
<pre>
User accounts   : $(ls -1 $PEOPLE | wc -l)
Logged users    : $(ls $sessions | wc -l)
</pre>
EOT
			list_last_users 5
			
			# Admin only
			if admin_user; then
				cat << EOT
<h3>Config paths</h3>
<pre>
People DB       : $PEOPLE
Authfile        : $AUTH_FILE
Admin users     : $ADMIN_USERS
</pre>
EOT
				# Get the list of administrators
				echo "<h3>Admin users</h3>"
				echo "<pre>"
				for u in $(cat $ADMIN_USERS)
				do
					. ${PEOPLE}/${u}/account.conf
					echo "<a href='?user=$u'>$u</a> - $NAME"
				done
				echo "</pre>"
			fi
			
		else
			gettext "You must be logged in to check on admin users"
		fi
		html_footer && exit 0 ;;
		
	*\ userslist\ *)
		# List all users
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
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href="$script?users">Users</a>
	<a href='$script?lastusers'>Last users</a>
</div>
<h2>Users: $users</h2>
<div id="users">
<table>
	<thead>
		<td>$(gettext "Username")</td>
		<td>$(gettext "Action")</td>
	</thead>
EOT
		for u in $(ls $PEOPLE)
		do
			# Skip corrupted accounts
			if ! [ -f "${PEOPLE}/${u}/account.conf" ]; then
				echo "${u} : Missing account.conf"
				continue
			fi
			cat << EOT
	<tr>
		<td><a href="$script?user=$u">$u</a></td>
		<td>TODO</td>
	</tr>
EOT
# deluser link --> use 'tazu' on SliTaz
#: <a href="?users&amp;deluser=$USER">$(gettext "delete")</a>
			unset NAME USER 
		done
		echo "</table></div>"
		html_footer && exit 0 ;;
	
	*\ lastusers\ *)
		# Show online users based on sessions files.
		d="Last users"
		header
		html_header
		user_box
		if ! check_auth; then
			gettext "You must be logged in to view online users"
			exit 0
		fi
		cat << EOT
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href="$script?users">Users</a>
</div>
EOT
		list_last_users 15
		
		# Active cookies
		echo "<h3>Session cookies: $(ls $sessions | wc -l)</h3>"
		echo "<pre>"
		for u in $(ls $sessions)
		do
			. "${PEOPLE}/${u}/account.conf"
			cat << EOT
$(get_gravatar $MAIL 24) <a href="?user=$USER">$USER</a> | $NAME
EOT
		done
		echo "</pre>"
		html_footer && exit 0 ;;
		
	*\ user\ *)
		# User profile page
		d="$(GET user)"
		last="$(cat $PEOPLE/"$(GET user)"/last)"
		header
		html_header
		user_box
		account_config="$PEOPLE/$(GET user)/account.conf"
		profile_config="$PEOPLE/$(GET user)/profile.conf"
		if [ ! -f "$account_config" ]; then
			echo "No user profile for: $(GET user)"
			html_footer && exit 0
		else
			. ${account_config}
		fi
		[ -f "$profile_config" ] && . ${profile_config}
cat << EOT
<h2>$(get_gravatar $MAIL) $NAME</h2>

<pre>
$(gettext "User name  :") $USER
$(gettext "Last login :") $last
EOT
		if check_auth && [ "$(GET user)" == "$user" ]; then
			auth_people
		else
			# check_auth will set VARS to current logged user: re-source
			. $PEOPLE/"$(GET user)"/account.conf
			public_people
		fi
		
		# Messages plugin integration
		if [ -x "$plugins/messages/messages.cgi" ]; then
			if check_auth && [ "$(GET user)" != "$user" ]; then
				cat << EOT
<div id="tools">
<a href="$script?messages&amp;to=$(GET user)">$(gettext "Send message")</a>
</div>
EOT
			fi
		fi
		
		# Display personal user profile
		if [ -f "$PEOPLE/$USER/profile.txt" ]; then
			echo "<h2>$(gettext "About me")</h2>"
			cat $PEOPLE/$USER/profile.txt | wiki_parser
		fi
		html_footer && exit 0 ;;
		
	*\ modprofile\ *)
		# Let user edit their profile
		if ! check_auth; then
			echo "ERROR" && exit 0
		fi
		d="$user profile"
		path=${PEOPLE}/${user}
		header
		html_header
		user_box
		cat << EOT
<h2>$(gettext "User:") $user</h2>
<p>$(gettext "Modify your profile settings")
<div id="edit">

<form method="get" action="$script" name="editor">
	<input type="hidden" name="saveprofile" />
	<h3>Name</h3>
	<input type="text" name="name" value="$NAME" />
	<h3>Email</h3>
	<input type="text" name="mail" value="$MAIL" />
	<h3>About you</h3>
	<textarea name="profile">$(cat "$path/profile.txt")</textarea>
	<input type="submit" value="$(gettext "Save profile")" />
</form>

</div>
EOT
		html_footer && exit 0 ;;
	
	*\ saveprofile\ *)
		# Save a user profile
		if check_auth; then
			path="$PEOPLE/$user"
			sed -i s"/^NAME=.*/NAME=\"$(GET name)\"/" ${path}/account.conf
			sed -i s"/^MAIL=.*/MAIL=\"$(GET mail)\"/" ${path}/account.conf
			cp -f ${path}/profile.txt ${path}/profile.bak
			sed "s/$(echo -en '\r') /\n/g" > ${path}/profile.txt << EOT
$(GET profile)
EOT
			header "Location: $script?user=$user"
		fi && exit 0 ;;
	
esac
