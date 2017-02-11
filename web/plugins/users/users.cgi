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
EOT
	# Each user can have personal profile page
	if [ -f "$PEOPLE/$USER/profile.txt" ]; then
		cat << EOT
<div id="tools">
	<a href="$script?modprofile">$(gettext "Modify profile")</a>
	<a href="$script?dashboard">Dashboard</a>
</div>
EOT
	else
		cat << EOT
<div id="tools">
	<a href="$script?modprofile">$(gettext "Create a profile page")</a>
	<a href="$script?dashboard">Dashboard</a>
</div>
EOT
	fi
}

case " $(GET) " in
	*\ users\ *)
		d="Users"
		header
		html_header
		user_box
		if check_auth && ! admin_user; then
			gettext "You must be admin to manage users" && exit 0
		fi
		cat << EOT
<h2>Users admin</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href='$script?loggedusers'>Logged users</a>
	<a href='$script?userslist'>Users list</a>
</div>
<pre>
User accounts   : $(ls -1 $PEOPLE | wc -l)
Logged users    : $(ls $sessions | wc -l)
People DB       : $PEOPLE
Auth file       : $AUTH_FILE
EOT
		
		echo "</pre>"
		html_footer && exit 0 ;;
		
	*\ userslist\ *)
		# List all users (slow if a llots a of accounts)
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
	<a href="$script?users">Users admin</a>
	<a href='$script?loggedusers'>Logged users</a>
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
# deluser link --> use 'tazu' on SliTaz
#: <a href="?users&amp;deluser=$USER">$(gettext "delete")</a>
			unset NAME USER 
		done
		echo "</pre>" 
		html_footer && exit 0 ;;
	
	*\ loggedusers\ *)
		# Show online users based on sessions files.
		d="Logged users"
		header
		html_header
		user_box
		if ! check_auth; then
			gettext "You must be logged in to view online users"
			exit 0
		fi
		logged="$(ls $sessions | wc -l)"
		cat << EOT
<h2>Logged users: $logged</h2>
<div id="tools">
	<a href="$script?dashboard">Dashboard</a>
	<a href="$script?users">Users admin</a>
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
		
	*\ user\ *)
		# User profile page
		d="$(GET user)"
		last="$(cat $PEOPLE/"$(GET user)"/last)"
		header
		html_header
		user_box
		. $PEOPLE/"$(GET user)"/account.conf
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
