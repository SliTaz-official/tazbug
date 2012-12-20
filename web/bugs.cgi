#!/bin/sh
#
# TazBug Web interface
#
# Copyright (C) 2012 SliTaz GNU/Linux - BSD License
#
. /usr/lib/slitaz/httphelper
[ -f "/etc/slitaz/bugs.conf" ] && . /etc/slitaz/bugs.conf

# Internal variable
bugdir="$TAZBUG/bug"
plugins="plugins"
sessions="/tmp/bugs/sessions"
po=""

# Content negotiation for Gettext
IFS=","
for lang in $HTTP_ACCEPT_LANGUAGE
do
	lang=${lang%;*} lang=${lang# } lang=${lang%-*}
	case "$lang" in
		en) LANG="C" ;;
		de) LANG="de_DE" ;;
		es) LANG="es_ES" ;;
		fr) LANG="fr_FR" ;;
		it) LANG="it_IT" ;;
		pt) LANG="pt_BR" ;;
		ru) LANG="ru_RU" ;;
		zh) LANG="zh_TW" ;;
	esac
	if echo "$po" | fgrep -q "$lang"; then
		break
	fi
done
unset IFS
export LANG LC_ALL=$LANG

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
	<a href="$WEB_URL">SliTaz Bugs</a> -
	<a href="$WEB_URL?README">README</a>
</div>

</body>
</html>
EOT
}

GETfiltered()
{
GET $1 | sed -e "s/'/\&#39;/g; s|\n|<br/>|g; s/\t/\&#09;/g;s/\%22/\"/g"
}

js_redirection_to()
{
	js_log "Redirecting to $1"
	echo "<script type=\"text/javascript\"> document.location = \"$1\"; </script>"
}


js_log()
{
	echo "<script type=\"text/javascript\">console.log('$1')</script>";
}


js_set_cookie()
{
	name=$1
	value=$2

	js_log 'Setting cookie.'
	echo "<script type=\"text/javascript\">"
		echo "document.cookie = \"$name=$value; expires=0; path=/\"";
	echo "</script>"
}


js_unset_cookie()
{
	name=$1

	js_log 'Unsetting cookie.'
	echo "<script type=\"text/javascript\">"
		echo "document.cookie = \"$1=\"\"; expires=-1; path=/";
	echo "</script>"
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

IDLOC=""
if [[ "$(GET id)" ]] ;then
	IDLOC="&id=$(GET id)"
fi

	if check_auth; then
		. $PEOPLE/$user/account.conf
		cat << EOT
<div id="user">
<a href="?user=$user">$(get_gravatar $MAIL 20)</a>
<a href="?logout">$(gettext 'Log out')</a>
</div>
EOT
	else
	cat << EOT
	<div id="user">
	<a href="?login$IDLOC"><img src="images/avatar.png" alt="[ User ]" /></a>
	<a href="?login$IDLOC">$(gettext 'Log in')</a>
	</div>
EOT
	fi
	cat << EOT

<div id="search">
	<form method="get" action="$WEB_URL">
		<input type="text" name="search" placeholder="$(gettext 'Search')" />
		<!-- <input type="submit" value="$(gettext 'Search')" /> -->
	</form>
</div>

<!-- Content -->
<div id="content">

EOT
}


# Login page
login_page() {
IDLOC=""
if [[ "$(GET id)" ]] ;then
	IDLOC="?id=$(GET id)"
fi

	cat << EOT
<h2>$(gettext 'Login')</h2>

<div id="account-info">
<p>$(gettext "No account yet? Please signup using the SliTaz Bugs reporter \
on your SliTaz system.")</p>
<p>$(gettext "Tip: to attach big files or images, you can use SliTaz Paste \
services:") <a href="http://paste.slitaz.org/">paste.slitaz.org</a></p>
</div>

<div id="login">
	<form method="post" action="$SCRIPT_NAME">
		<input type="text" name="auth" placeholder="$(gettext 'User name')" />
		<input type="password" name="pass" placeholder="$(gettext 'Password')" />
		<div>
			<input type="submit" value="$(gettext 'Log in')" />
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
$(eval_gettext 'Real name  : $NAME')
</pre>
EOT
}


# Display authentified user profile. TODO: change password
auth_people() {
	cat << EOT
<pre>
$(eval_gettext 'Real name  : $NAME')
$(eval_gettext 'Email      : $MAIL')
$(eval_gettext 'Secure key : $KEY')
</pre>
EOT
}


# Usage: list_bugs STATUS
list_bugs() {
	bug="$1"
	echo "<h3>$(eval_gettext '$bug Bug')</h3>"
	for pr in critical standard
	do
		for bug in $(fgrep -H "$1" $bugdir/*/bug.conf | cut -d ":" -f 1)
		do
			. $bug
			id=$(basename $(dirname $bug))
			if [ "$PRIORITY" == "$pr" ]; then
				cat << EOT
<pre>
$(gettext 'Bug title  :') <strong>$BUG</strong> <a href="?id=$id">$(gettext 'Show')</a>
$(gettext 'ID - Date  :') $id - $DATE
$(gettext 'Creator    :') <a href="?user=$CREATOR">$CREATOR</a>
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
	if [ -f "$PEOPLE/$CREATOR/account.conf" ]; then
		. $PEOPLE/$CREATOR/account.conf
	else
		MAIL="default"
	fi
	cat << EOT
<h2>$(eval_gettext 'Bug $id')</h2>
<form method="get" action="$WEB_URL">

<p>
	$(get_gravatar $MAIL 32)
	<strong>$STATUS</strong>
	$BUG - $DATE -
	$(eval_gettext 'Priority $PRIORITY') -
	$(eval_ngettext '$msgs message' '$msgs messages' $msgs)
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
		<p><input type="submit" value="$(gettext 'Send message')" /></p>
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
	js_log "Will write message in $bugdir/$id/msg.$count "
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$id/msg.$count << EOT
USER="$USER"
DATE="$date"
MSG="$(GETfiltered msg)"
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

BUG="$(GETfiltered bug)"
STATUS="OPEN"
PRIORITY="$(GET priority)"
CREATOR="$USER"
DATE="$date"
PKGS="$(GETfiltered pkgs)"

DESC="$(GETfiltered desc)"
EOT
}


# New bug page for the web interface
new_bug_page() {
	cat << EOT
<h2>$(gettext "New Bug")</h2>
<div id="newbug">

<form method="get" action="$WEB_URL" onsubmit="return checkNewBug();">
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
<h2>$(eval_gettext 'Edit Bug $bug')</h2>
<div id="edit">

<form method="get" action="$WEB_URL">
	<textarea name="bugconf">$(cat $bugdir/$bug/bug.conf)</textarea>
	<input type="hidden" name="bug" value="$bug" />
	<input type="submit" value="$(gettext 'Save configuration')" />
</form>

</div>
EOT
}


save_bug() {
	bug="$(GET bug)"
	content="$(GET bugconf)"
	sed "s|\"|'|" | sed "s/$(echo -en '\r') /\n/g" > $bugdir/$bug/bug.conf << EOT
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
	md5=$(md5crypt $email)
	echo "<img src=\"$url/$md5?d=identicon&amp;s=$size\" alt=\"\" />"
}


# Create a new user in AUTH_FILE and PEOPLE
new_user_config() {
	mail="$(GET mail)"
	pass="$(GET pass)"
	key=$(echo -n "$user:$mail:$pass" | md5sum | awk '{print $1}')
	echo "Server Key generated"
	echo "$user:$pass" >> $AUTH_FILE
	mkdir -pm0700 $PEOPLE/$user/
	cat > $PEOPLE/$user/account.conf << EOT
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
	chmod 0600 $PEOPLE/$user/account.conf
	if [ ! -f $PEOPLE/$user/account.conf ]; then
		echo "ERROR: User creation failed!"
		fi;
	}




###################################################
# POST actions
###################################################

case " $(POST) " in
	*\ auth\ *)
		header
		html_header
		# Authenticate user. Create a session file in $sessions to be used
		# by check_auth. We have the user login name and a peer session
		# md5 string in the COOKIE.
		user="$(POST auth)"
		pass="$(echo -n "$(POST pass)" | md5sum | awk '{print $1}')"

		IDLOC=""
			if [[ "$(GET id)" ]] ;then
				IDLOC="&id=$(GET id)"
			fi

		if [  ! -f $AUTH_FILE ] ; then
			js_log "$AUTH_FILE (defined in \$AUTH_FILE) have not been found."
			js_redirection_to "$WEB_URL?login$IDLOC"
		fi;

		valid=$(fgrep "${user}:" $AUTH_FILE | cut -d ":" -f 2)
		if [ "$pass" == "$valid" ] && [ "$pass" != "" ]; then
			if [[ "$(GET id)" ]] ;then
				IDLOC="?id=$(GET id)"
			fi
			md5session=$(echo -n "$$:$user:$pass:$$" | md5sum | awk '{print $1}')
			mkdir -p $sessions
			echo "$md5session" > $sessions/$user
			js_set_cookie 'auth' "$user:$md5session"
			js_log "Login authentification have been executed & accepted :)"
			js_redirection_to "$WEB_URL$IDLOC"
		else
			js_log "Login authentification have been executed & refused"
			js_redirection_to "$WEB_URL?login&error$IDLOC"
		fi

		html_footer
		;;
esac

#
# Plugins
#
for p in $(ls -1 $plugins)
do
	[ -f "$plugins/$p/$p.conf" ] && . $plugins/$p/$p.conf
	[ -x "$plugins/$p/$p.cgi" ] && . $plugins/$p/$p.cgi
done




###################################################
# GET actions
###################################################

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
			error="<span class='error'>$(gettext 'Bad login or pass')</span>"
		header
		html_header
		user_box
		login_page
		html_footer ;;
	*\ logout\ *)
		header
		html_header
		if check_auth; then
			rm -f "$sessions/$user"
			js_unset_cookie 'auth'
			js_redirection_to "$WEB_URL"

		fi ;;
	*\ user\ *)
		# User profile
		header
		html_header
		user_box
		. $PEOPLE/"$(GET user)"/account.conf
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
			echo "<p>$(gettext 'You must be logged in to post a new bug')</p>"
		fi
		html_footer ;;
	*\ addbug\ *)
		# Add a bug from web interface.
		header
		html_header
		if check_auth; then
			new_bug
			js_redirection_to "$WEB_URL?id=$count"
		fi ;;
	*\ edit\ *)
		bug="$(GET edit)"
		header
		html_header
		user_box
		edit_bug
		html_footer ;;
	*\ bugconf\ *)
		header
		html_header
		if check_auth; then
			save_bug
			js_redirection_to "$WEB_URL?id=$bug"
		fi ;;
	*\ id\ *)
		# Empty deleted messages to keep msg count working.
		header
		html_header
		id="$(GET id)"
		[ "$(GET close)" ] && close_bug
		[ "$(GET open)" ] && open_bug
		[ "$(GET msg)" ] && new_msg
		[ "$(GET delmsg)" ] && rm -f $bugdir/$id/msg.$(GET delmsg) && \
			touch $bugdir/$id/msg.$(GET delmsg)
		msgs=$(fgrep MSG= $bugdir/$id/msg.* | wc -l)
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
		if fgrep -qH $key $PEOPLE/*/account.conf; then
			conf=$(fgrep -H $key $PEOPLE/*/account.conf | cut -d ":" -f 1)
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
<form method="get" action="$WEB_URL">
	<input type="text" name="search" />
	<input type="submit" value="$(gettext 'Search')" />
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
				echo "<p><strong>Bug $id</strong> <a href=\"?id=$id\">"$(gettext 'Show')"</a></p>"
				echo '<pre>'
				fgrep -i "$(GET search)" $bugdir/$id/* | \
					sed s"/$(GET search)/<span class='ok'>$(GET search)<\/span>/"g
				echo '</pre>'
			else
				get_search=$(GET search)
				echo "<p>$(eval_gettext 'No result found for: $get_search')</p>"
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
	$(eval_ngettext 'Bug: $bugs in total -' 'Bugs: $bugs in total -' $bugs)
	$(eval_ngettext '$close fixed -' '$close fixed -' $close)
	$(eval_ngettext '$fixme to fix -' '$fixme to fix -' $fixme)
	$(eval_ngettext '$msgs message' '$msgs messages' $msgs)
</p>

<div class="pctbar">
	<div class="pct" style="width: ${pct}%;">${pct}%</div>
</div>

<p>$(gettext "Please read the <a href=\"?README\">README</a> for help and more \
information. You may also be interested by the SliTaz \
<a href=\"http://roadmap.slitaz.org/\">Roadmap</a> and the packages \
<a href=\"http://cook.slitaz.org/\">Cooker</a>. To perform a search \
enter your term and press ENTER.")
</p>

<div id="tools">
	<a href="?closed">$(gettext 'View closed bugs')</a>
EOT
		if check_auth; then
			echo "<a href='?newbug'>$(gettext 'Create a new bug')</a>"
		fi
		cat << EOT
</div>
EOT
		list_bugs OPEN
		html_footer ;;
esac

exit 0
