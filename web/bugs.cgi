#!/bin/sh
#
# TazBug Web interface
#
# Copyright (C) 2012 SliTaz GNU/Linux - BSD License
#
. /usr/lib/slitaz/httphelper
[ -f "/etc/slitaz/tazbug.conf" ] && . /etc/slitaz/tazbug.conf
[ -f "../tazbug.conf" ] && . ../tazbug.conf

# Internal variable
bugdir="bug"
sessions="/tmp/tazbug/sessions"

# Content negotiation for Gettext
IFS=","
for lang in $HTTP_ACCEPT_LANGUAGE
do
	lang=${lang%;*} lang=${lang# } lang=${lang%-*}
	[ -d "$lang" ] &&  break
	case "$lang" in
		en) lang="C" ;;
		fr) lang="fr_FR" ;;
		ru) lang="ru_RU" ;;
	esac
done
unset IFS
export LANG=$lang LC_ALL=$lang

# Internationalization: $(gettext "")
. /usr/bin/gettext.sh
TEXTDOMAIN='tazbug'
export TEXTDOMAIN

#
# Functions
#

# HTML 5 header.
html_header() {
	cat lib/header.html
}

# HTML 5 footer.
html_footer() {
	cat << EOT
</div>

<div id="footer">
	<a href="./">SliTaz Bugs</a> -
	<a href="./?README">README</a>
</div>

</body>
</html>
EOT
}

# Crypt pass when login
crypt_pass() {
	echo -n "$1" | md5sum | awk '{print $1}'
}

# Check if user is auth
check_auth() {
	auth="$(COOKIE auth)"
	user="$(echo $auth | cut -d ":" -f 1)"
	md5cookie="$(echo $auth | cut -d ":" -f 2)"
	[ -f "$sessions/$user" ] && md5session="$(cat $sessions/$user)"
	if [ "$md5cookie" == "$md5session" ] && [ "$auth" ]; then
		return 0
	else
		return 1
	fi
}

# Authentified or not
user_box() {
	if check_auth; then
		. $PEOPLE/$user/slitaz.conf
		cat << EOT
<div id="user">
<a href="?user=$user">$(get_gravatar $MAIL 20)</a>
<a href="?logout">Logout</a>
</div>
EOT
	else
	cat << EOT
<div id="user">
	<img src="images/avatar.png" alt="[ User ]" />
	<a href="?login">Login</a>
</div>
EOT
	fi
	cat << EOT

<div id="search">
	<form method="get" action="./">
		<input type="text" name="search" placeholder="$(gettext "Search")" />
		<!-- <input type="submit" value="$(gettext "Search")" /> -->
	</form>
</div>

<!-- Content -->
<div id="content">

EOT
}

# Login page
login_page() {
	cat << EOT
<!-- Content -->
<div id="content">

<h2>$(gettext "Login")</h2>

<div id="account-info">
$(gettext "No account yet? Please signup using the SliTaz Bugs reporter
on your SliTaz system. <p>Tip: to attach big files or images, you can use
SliTaz Paste services:") <a href="http://paste.slitaz.org/">paste.slitaz.org</a>
</p>
</div>

<div id="login">
	<form method="post" action="$SCRIPT_NAME">
		<input type="text" name="auth" placeholder="$(gettext "User name")" />
		<input type="password" name="pass" placeholder="$(gettext "Password")" />
		<div>
			<input type="submit" value="Login" />
			$error
		</div>
	</form>
</div>

<div style="clear: both;"></div>
EOT
}

# Display user public profile.
public_people() {
	cat << EOT
<pre>
Real name : $NAME
</pre>
EOT
}

# Display authentified user profile. TODO: change password
auth_people() {
	cat << EOT
<pre>
Real name  : $NAME
Email      : $MAIL
Secure key : $KEY
</pre>
EOT
}

# Usage: list_bugs STATUS
list_bugs() {
	echo "<h3>$1 Bugs</h3>"
	for pr in critical standard
	do
		for bug in $(fgrep -H "$1" $bugdir/*/bug.conf | cut -d ":" -f 1)
		do
			. $bug
			id=$(dirname $bug | cut -d "/" -f 2)
			if [ "$PRIORITY" == "$pr" ]; then
				cat << EOT
<pre>
Bug title  : <strong>$BUG</strong> <a href="?id=$id">Show</a>
ID - Date  : $id - $DATE
Creator    : <a href="?user=$CREATOR">$CREATOR</a>
</pre>
EOT
			fi
		done
	done
}

# Stripped down Wiki parser for bug desc and messages which are simply
# displayed in <pre>
wiki_parser() {
	sed \
		-e s"#http://\([^']*\).png#<img src='\0' alt='[ Image ]' />#"g \
		-e s"#http://\([^']*\).*# <a href='\0'>\1</a>#"g
}

# Bug page
bug_page() {
	if [ -f "$PEOPLE/$CREATOR/slitaz.conf" ]; then
		. $PEOPLE/$CREATOR/slitaz.conf
	else
		MAIL="default"
	fi
	cat << EOT
<h2>Bug $id</h2>
<form method="get" action="./">

<p>
	$(get_gravatar $MAIL 32) <strong>$STATUS</strong> $BUG - $DATE - Priority $PRIORITY
	- $msgs messages
</p>

<pre>
$(echo "$DESC" | wiki_parser)
</pre>

<div id="tools">
EOT
	if check_auth; then
		if [ "$STATUS" == "OPEN" ]; then
			cat << EOT 
<a href="?id=$id&amp;close">$(gettext "Close bug")</a>
<a href="?edit=$id">$(gettext "Edit bug")</a>
EOT
		else
			cat << EOT
<a href="?id=$id&amp;open">$(gettext "Re open bug")</a>
EOT
		fi
	fi
	cat << EOT
</div>

<h3>$(gettext "Messages")</h3>
EOT
	[ "$msgs" == "0" ] && gettext "No messages"
	for msg in $(ls -1tr $bugdir/$id/msg.*)
	do
		. $msg
		if [ "$MSG" ]; then
			msgid=$(echo $msg | cut -d "." -f 2)
			del=""
			# User can delete his post.
			[ "$user" == "$USER" ] && \
				del="<a href=\"?id=$id&amp;delmsg=$msgid\">delete</a>"
			cat << EOT
<p><strong>$USER</strong> $DATE $del</p>
<pre>
$(echo "$MSG" | wiki_parser)
</pre>
EOT
		fi
		unset NAME DATE MSG
	done
	if check_auth; then
		cat << EOT
<div>
	<h3>$(gettext "New message")</h3>
	
		<input type="hidden" name="id" value="$id" />
		<textarea name="msg" rows="8"></textarea>
		<p><input type="submit" value="$(gettext "Send message")" /></p>
	</form>
</div>
EOT
	fi
}

# Write a new message
new_msg() {
	date=$(date "+%Y-%m-%d %H:%M")
	msgs=$(ls -1 $bugdir/$id/msg.* | wc -l)
	count=$(($msgs + 1))
	if check_auth; then
		USER="$user"
	fi
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$id/msg.$count << EOT
USER="$USER"
DATE="$date"
MSG="$(GET msg)"
EOT
}

# Create a new Bug
new_bug() {
	count=$(ls -1 $bugdir | wc -l)
	date=$(date "+%Y-%m-%d %H:%M")
	# Sanity check, JS may be disabled.
	[ ! "$(GET bug)" ] && echo "Missing bug title" && exit 1
	[ ! "$(GET desc)" ] && echo "Missing bug description" && exit 1
	if check_auth; then
		USER="$user"
	fi
	mkdir -p $bugdir/$count
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$count/bug.conf << EOT
# SliTaz Bug configuration

BUG="$(GET bug)"
STATUS="OPEN"
PRIORITY="$(GET priority)"
CREATOR="$USER"
DATE="$date"
PKGS="$(GET pkgs)"

DESC="$(GET desc)"
EOT
}

# New bug page for the web interface
new_bug_page() {
	cat << EOT
<h2>$(gettext "New Bug")</h2>
<div id="newbug">

<form method="get" action="./" onsubmit="return checkNewBug();">
	<input type="hidden" name="addbug" />
	<table>
		<tbody>
			<tr>
				<td>$(gettext "Bug title")*</td>
				<td><input type="text" name="bug" /></td>
			</tr>
			<tr>
				<td>$(gettext "Description")*</td>
				<td><textarea name="desc"></textarea></td>
			</tr>
			<tr>
				<td>$(gettext "Packages")</td>
				<td><input type="text" name="pkgs" /></td>
			</tr>
			<tr>
				<td>$(gettext "Priority")</td>
				<td>
					<select name="priority">
						<option value="standard">$(gettext "Standard")</option>
						<option value="critical">$(gettext "Critical")</option>
					</select>
					<input type="submit" value="$(gettext "Create Bug")" />
				</td>
			</tr>
		</tbody>
	</table>
</form>

<p>
$(gettext "* field is obligatory. You can also specify affected packages.")
</p>

</div>
EOT
}

# Edit/Save a bug configuration file
edit_bug() {
	cat << EOT
<h2>$(gettext "Edit Bug $bug")</h2>
<div id="edit">

<form method="get" action="./">
	<textarea name="bugconf">$(cat $bugdir/$bug/bug.conf)</textarea>
	<input type="hidden" name="bug" value="$bug" />
	<input type="submit" value="$(gettext "Save configuration")" />
</form>

</div>
EOT
}

save_bug() {
	bug="$(GET bug)"
	content="$(GET bugconf)"
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$bug/bug.conf << EOT
$content
EOT
}

# Close a fixed bug
close_bug() {
	sed -i s'/OPEN/CLOSED/' $bugdir/$id/bug.conf
}

# Re open an old bug
open_bug() {
	sed -i s'/CLOSED/OPEN/' $bugdir/$id/bug.conf
}

# Get and display Gravatar image: get_gravatar email size
# Link to profile: <a href="http://www.gravatar.com/$md5">...</a>
get_gravatar() {
	email=$1
	size=$2
	[ "$size" ] || size=48
	url="http://www.gravatar.com/avatar"
	md5=$(echo -n $email | md5sum | cut -d " " -f 1)
	echo "<img src='$url/$md5?d=identicon&s=$size' alt='' />"
}

# Create a new user in AUTH_FILE and PEOPLE
new_user_config() {
	mail="$(GET mail)"
	pass="$(GET pass)"
	key=$(echo -n "$user:$mail:$pass" | md5sum | awk '{print $1}')
	echo "$user:$pass" >> $AUTH_FILE
	mkdir -p $PEOPLE/$user/
	cat > $PEOPLE/$user/slitaz.conf << EOT
# SliTaz user configuration
#

NAME="$(GET name)"
USER="$user"
MAIL="$mail"
KEY="$key"

COMMUNITY="$(GET scn)"
LOCATION="$(GET location)"
RELEASES="$(GET releases)"
PACKAGES="$(GET packages)"
EOT
	chmod 0600 $PEOPLE/$user/slitaz.conf
}

#
# POST actions
#

case " $(POST) " in
	*\ auth\ *)
		# Authenticate user. Create a session file in $sessions to be used
		# by check_auth. We have the user login name and a peer session
		# md5 string in the COOKIE.
		user="$(POST auth)"
		pass="$(crypt_pass "$(POST pass)")"
		valid=$(fgrep "${user}:" $AUTH_FILE | cut -d ":" -f 2)
		if [ "$pass" == "$valid" ] && [ "$pass" != "" ]; then
			md5session=$(echo -n "$$:$user:$pass:$$" | md5sum | awk '{print $1}')
			mkdir -p $sessions
			echo "$md5session" > $sessions/$user
			header "Location: $WEB_URL" \
				"Set-Cookie: auth=$user:$md5session; HttpOnly"
		else
			header "Location: $WEB_URL?login&error"
		fi ;;
esac

#
# GET actions
#

case " $(GET) " in
	*\ README\ *)
		header
		html_header
		user_box
		echo '<h2>README</h2>'
		echo '<pre>'
		cat /usr/share/doc/tazbug/README
		echo '</pre>' 
		html_footer ;;
	*\ closed\ *)
		# Show all closed bugs.
		header
		html_header
		user_box
		list_bugs CLOSED
		html_footer ;;
	*\ login\ *)
		# The login page
		[ "$(GET error)" ] && \
			error="<span class="error">$(gettext "Bad login or pass")</span>"
		header 
		html_header
		user_box
		login_page 
		html_footer ;;
	*\ logout\ *)
		# Set a Cookie in the past to logout.
		expires="Expires=Wed, 01-Jan-1980 00:00:00 GMT"
		if check_auth; then
			rm -f "$sessions/$user"
			header "Location: $WEB_URL" "Set-Cookie: auth=none; $expires; HttpOnly"
		fi ;;
	*\ user\ *)
		# User profile
		header
		html_header
		user_box
		. $PEOPLE/"$(GET user)"/slitaz.conf
		echo "<h2>$(get_gravatar $MAIL) $(GET user)</h2>"
		if check_auth && [ "$(GET user)" == "$user" ]; then
			auth_people
		else
			public_people
		fi
		html_footer ;;
	*\ newbug\ *)
		# Add a bug from web interface.
		header
		html_header
		user_box
		if check_auth; then
			new_bug_page
		else
			echo "<p>$(gettext "You must be logged in to post a new bug")</p>"
		fi
		html_footer ;;
	*\ addbug\ *)
		# Add a bug from web interface.
		if check_auth; then
			new_bug
			header "Location: $WEB_URL?id=$count"
		fi ;;
	*\ edit\ *)
		bug="$(GET edit)"
		header
		html_header
		user_box
		edit_bug
		html_footer ;;
	*\ bugconf\ *)
		if check_auth; then
			save_bug
			header "Location: $WEB_URL?id=$bug"
		fi ;;
	*\ id\ *)
		# Empty deleted messages to keep msg count working.
		id="$(GET id)"
		[ "$(GET close)" ] && close_bug
		[ "$(GET open)" ] && open_bug
		[ "$(GET msg)" ] && new_msg
		[ "$(GET delmsg)" ] && rm -f $bugdir/$id/msg.$(GET delmsg) && \
			touch $bugdir/$id/msg.$(GET delmsg)
		msgs=$(fgrep MSG= $bugdir/$id/msg.* | wc -l)
		header 
		html_header
		user_box 
		. $bugdir/$id/bug.conf
		bug_page
		html_footer ;;
	*\ signup\ *)
		# Signup
		header "Content-type: text/plain;"
		user="$(GET signup)"
		echo "Requested user login : $user"
		if fgrep -q "$user:" $AUTH_FILE; then
			echo "ERROR: User already exists" && exit 1
		else
			echo "Creating account for : $(GET name)"
			new_user_config 
		fi ;;
	*\ key\ *)
		# Let user post new bug or message with crypted key (no gettext)
		#
		# Testing only and is security acceptable ?
		#
		key="$(GET key)"
		id="$(GET bug)"
		header "Content-type: text/plain;"
		echo "Checking secure key..." 
		if fgrep -qH $key $PEOPLE/*/slitaz.conf; then
			conf=$(fgrep -H $key $PEOPLE/*/slitaz.conf | cut -d ":" -f 1)
			. $conf
			echo "Authentified: $NAME ($USER)"
			case " $(GET) " in
				*\ msg\ *)
					[ ! "$id" ] && echo "Missing bug ID" && exit 0
					echo "Posting new message to bug: $id"
					echo "Message: $(GET msg)"
					new_msg ;;
				*\ bug\ *)
					echo "Adding new bug: $(GET bug)" 
					echo "Description: $(GET desc)" 
					new_bug ;;
			esac 
		else
			echo "Not a valid SliTaz user key"
			exit 0
		fi ;;
	*\ search\ *)
		header
		html_header
		user_box
		cat << EOT
<h2>$(gettext "Search")</h2>
<form method="get" action="./">
	<input type="text" name="search" />
	<input type="submit" value="$(gettext "Search")" />
</form>
<div>
EOT
	
		#found=0 JS to notify or write results nb under the search box.
		for bug in $bugdir/*
		do
			result=$(fgrep -i "$(GET search)" $bug/*)
			if [ "$result" ]; then
				#found=$(($found + 1))
				id=${bug#bug/}
				echo "<p><strong>Bug $id</strong> <a href='?id=$id'>$(gettext "Show")</a></p>"
				echo '<pre>'
				fgrep -i "$(GET search)" $bugdir/$id/* | \
					sed s"/$(GET search)/<span class='ok'>$(GET search)<\/span>/"g
				echo '</pre>'
			else
				gettext "<p>No result found for:"; echo " $(GET search)</p>"
			fi
		done
		echo '</div>'
		html_footer ;;
	*)
		# Default page.
		bugs=$(ls -1 $bugdir | wc -l)
		close=$(fgrep "CLOSED" $bugdir/*/bug.conf | wc -l)
		fixme=$(fgrep "OPEN" $bugdir/*/bug.conf | wc -l)
		msgs=$(find $bugdir -name msg.* ! -size 0 | wc -l)
		pct=0
		[ $bugs -gt 0 ] && pct=$(( ($close * 100) / $bugs ))
		header
		html_header
		user_box
		cat << EOT

<h2>$(gettext "Summary")</h2>

<p>
	Bugs: $bugs in total - $close fixed - $fixme to fix - $msgs messages
</p>

<div class="pctbar">
	<div class="pct" style="width: ${pct}%;">${pct}%</div>
</div>

<p>
	Please read the <a href="?README">README</a> for help and more 
	information. You may also be interested by the SliTaz
	<a href="http://roadmap.slitaz.org/">Roadmap</a> and the packages 
	<a href="http://cook.slitaz.org/">Cooker</a>. To perform a search
	enter your term and press ENTER.
</p>

<div id="tools">
	<a href="?closed">View closed bugs</a>
EOT
		if check_auth; then
			echo "<a href='?newbug'>$(gettext "Create a new bug")</a>"
		fi
		cat << EOT
</div>
EOT
		list_bugs OPEN
		html_footer ;;
esac

exit 0
