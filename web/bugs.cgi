#!/bin/sh
#
# TazBug Web interface
#
# Copyright (C) 2012-2017 SliTaz GNU/Linux - BSD License
#
. /usr/lib/slitaz/httphelper.sh

# Source config file
. ./config.cgi

# Internal variable
bugdir="$PWD/bug"
plugins="plugins"
sessions="/tmp/bugs/sessions"
script="$SCRIPT_NAME"
timestamp="$(date -u +%s)"

# Content negotiation for Gettext
IFS=","
for lang in $HTTP_ACCEPT_LANGUAGE
do
	lang=${lang%;*} lang=${lang# } lang=${lang%-*}
	case "$lang" in
		en) LANG="C" && break ;;
		de) LANG="de_DE" && break ;;
		es) LANG="es_ES" && break ;;
		fr) LANG="fr_FR" && break ;;
		it) LANG="it_IT" && break ;;
		pt) LANG="pt_BR" && break ;;
		ru) LANG="ru_RU" && break ;;
		zh) LANG="zh_TW" && break ;;
	esac
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
	gentime=$(( $(date -u +%s) - ${timestamp} ))
	cat << EOT
</div>

<div id="footer">
	<a href="$script">SliTaz Bugs</a> -
	<a href="$script?README">README</a>
	- Page generated in ${gentime}s
</div>

</body>
</html>
EOT
}

GETfiltered() {
	GET $1 | sed -e "s/'/\&#39;/g; s|\n|<br/>|g; s/\t/\&#09;/g;s/\%22/\\\"/g"
}

js_redirection_to() {
	js_log "Redirecting to $1"
	echo "<script type=\"text/javascript\"> document.location = \"$1\"; </script>"
}

js_log() {
	echo "<script type=\"text/javascript\">console.log('$1')</script>";
}

js_set_cookie() {
	name=$1
	value=$2
	js_log 'Setting cookie.'
	cat << EOT
<script type="text/javascript">
	document.cookie = '$name=$value; expires=0; path=/';
	</script>
EOT
}

js_unset_cookie() {
	name=$1
	js_log 'Unsetting cookie.'
	cat << EOT
<script type="text/javascript">
	document.cookie = '$1=""; expires=-1; path=/;'
</script>
EOT
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

# Check if user is admin
admin_user() {
	fgrep -w -q "$user" ${ADMIN_USERS}
}

# Authenticated or not
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
<a href="?logout">$(gettext 'Logout')</a>
</div>
EOT
	else
	cat << EOT
	<div id="user">
	<a href="?login$IDLOC"><img src="images/avatar.png" alt="[ User ]" /></a>
	<a href="?login$IDLOC">$(gettext 'Login')</a>
	</div>
EOT
	fi
	cat << EOT

<div id="search">
	<form method="get" action="$script">
		<input type="text" name="search" placeholder="$(gettext 'Search')" />
		<!-- <input type="submit" value="$(gettext 'Search')" /> -->
	</form>
</div>

<!-- Content -->
<div id="content">

EOT
}

# Signup page
signup_page() {
	cat << EOT

<div id="signup">
	<form method="post" name="signup" action="$SCRIPT_NAME" onsubmit="return checkSignup();">
		<input type="hidden" name="signup" value="new" />
		<input type="text" name="name" placeholder="$(gettext "Real name")" />
		<input type="text" name="user" placeholder="$(gettext "User name")" />
		<input type="text" name="mail" placeholder="$(gettext "Email")" />
		<input type="password" name="pass" placeholder="$(gettext "Password")" />
		<div>
			<input type="submit" value="$(gettext "Create new account")" />
		</div>
	</form>
</div>

EOT
}

# Link for online signup if enabled.
online_signup() {
	if [ "$ONLINE_SIGNUP" == "yes" ]; then
		echo -n "<a href='$script?signup&amp;online'>"
		gettext "Sign Up Online"
		echo '</a></p>'
	fi
}

# Login page
login_page() {
	cat << EOT
<h2>$(gettext 'Login')</h2>

<div id="account-info">
<p>$(gettext "No account yet?")</p>
$(online_signup)
<p>$(gettext "Tip: to attach big files or images, you can use SliTaz Paste \
services:") <a href="http://paste.slitaz.org/">paste.slitaz.org</a></p>
</div>

<div id="login">
	<form method="post" action="$script">
	<div>
		<input type="text" name="auth" placeholder="$(gettext 'User name')" />
	</div>
		<input type="password" name="pass" placeholder="$(gettext 'Password')" />
		<div>
			<input type="hidden" name="id" value="$(GET id)" />
			<input type="submit" value="$(gettext 'Log in')" />
			$error
		</div>
	</form>
</div>

<div style="clear: both;"></div>
EOT
}

# Set open/closed bug path: set_bugpath ID
set_bugpath() {
	if [ -d "$bugdir/closed/$1" ]; then
		bugpath="$bugdir/closed/$1"
	else
		bugpath="$bugdir/open/$1"
	fi
}
set_bugdir() {
	if [ -d "$bugdir/closed/$1" ]; then
		bugdir="$bugdir/closed"
	else
		bugdir="$bugdir/open"
	fi
}

# Nice ls output for open and closed bugs
ls_bugs() {
	ls $bugdir/open
	ls $bugdir/closed
}

# Usage: list_bug ID
list_bug() {
	id="$1"
	set_bugpath ${id}
	. ${bugpath}/bug.conf
	[ -f "${PEOPLE}/${CREATOR}/account.conf" ] && \
	. ${PEOPLE}/${CREATOR}/account.conf
	cat << EOT
<a href="?user=$USER">$(get_gravatar "$MAIL" 24)</a> \
ID $id: <a href="?id=$id">$BUG</a> <span class="date">- $DATE</span>
EOT
	unset CREATOR USER MAIL bugpath
}

# Usage: list_bugs [open|closed]
list_bugs() {
	status="$1"
	echo "<h3>$(gettext 'Bugs:') $status</h3>"
	echo "<pre>"
	for pr in critical standard
	do
		for id in $(ls $bugdir/$status)
		do
			. $bugdir/$status/$id/bug.conf
			if [ "$PRIORITY" == "$pr" ]; then
				[ -f "${PEOPLE}/${CREATOR}/account.conf" ] && \
					. ${PEOPLE}/${CREATOR}/account.conf
				cat << EOT
<a href="?user=$USER">$(get_gravatar "$MAIL" 24)</a> \
ID $id: <a href="?id=$id">$BUG</a> <span class="date">- $DATE</span>
EOT
			fi
			unset CREATOR USER MAIL BUG
		done
	done
}

# Usage: list_msg path
list_msg() {
	msg="$1"
	dir=$(dirname $msg)
	id=$(basename $dir)
	. ${msg}
	[ -f "${PEOPLE}/${USER}/account.conf" ] && \
		. ${PEOPLE}/${USER}/account.conf
	cat << EOT
<a href="?user=$USER">$(get_gravatar "$MAIL" 24)</a> \
ID: <a href="?id=$id">Bug $id</a> by $USER <span class="date">- $DATE</span>
EOT
	unset CREATOR USER MAIL
}

# Stripped down Wiki parser for bug desc and messages which are simply
# displayed in <pre>
wiki_parser() {
	sed \
		-e s"#http://\([^']*\).png#<img src='\0' alt='[ Image ]' />#"g \
		-e s"#http://\([^']*\).*# <a href='\0'>\1</a>#"g \
		-e 's#\\\\n##g;s#%22#"#g;s#%21#!#g'
}

# Bug page
bug_page() {
	. $bugdir/$id/bug.conf
	if [ -f "$PEOPLE/$CREATOR/account.conf" ]; then
		. $PEOPLE/$CREATOR/account.conf
	else
		MAIL="default"
	fi
	cat << EOT
<h2>$(eval_gettext 'Bug $id: $STATUS')</h2>

<p>
	$(get_gravatar $MAIL 32) <strong>$BUG</strong>
</p>
<p>
	$(gettext "Date:") $DATE -
	$(gettext "Creator:") <a href="?user=$CREATOR">$CREATOR</a> -
	$(eval_gettext 'Priority $PRIORITY') -
	$(eval_ngettext '$msgs message' '$msgs messages' $msgs)
</p>

<pre>
$(cat $bugdir/$id/desc.txt | wiki_parser)
</pre>

<div id="tools">
EOT
	if check_auth; then
		if [ "$STATUS" == "OPEN" ]; then
			cat << EOT
<a href="?id=$id&amp;close">$(gettext "Close bug")</a>
EOT
		# Only original user and admin can edit a bug
		if [ "$user" == "$CREATOR" ] || admin_user; then
			cat << EOT
<a href="?editbug=$id">$(gettext "Edit bug")</a>
EOT
		fi
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
			# User can delete his post as well as admin.
			if [ "$user" == "$USER" ] || admin_user; then
				del="<a href=\"?id=$id&amp;delmsg=$msgid\">delete</a>"
			fi
			cat << EOT
<p><strong>$USER</strong> $DATE $del</p>
<pre>
$(echo "$MSG" | wiki_parser)
</pre>
EOT
		fi
		unset USER DATE MSG
	done
	if check_auth; then
		cat << EOT
<div>
	<h3>$(gettext "New message")</h3>
	<form method="get" action="$script">
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
	msgs=$(ls -1 $bugdir/$id/msg.* | cut -d "." -f 2 | sort -n | tail -n 1)
	count=$(($msgs + 1))
	if check_auth; then
		USER="$user"
	fi
	js_log "Will write message in $bugdir/$id/msg.$count "
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$id/msg.$count.tmp << EOT
USER="$USER"
DATE="$date"
MSG="$(GETfiltered msg)"
EOT
	fold -s -w 80 $bugdir/$id/msg.$count.tmp > $bugdir/$id/msg.$count
	rm -f $bugdir/$id/msg.$count.tmp
}

# Create a new Bug. ID is set by counting dirs in bug/ + 1
new_bug() {
	count=$(ls_bugs | sort -g | tail -n 1)
	id=$(($count +1))
	date=$(date "+%Y-%m-%d %H:%M")
	# Sanity check, JS may be disabled.
	[ ! "$(GET bug)" ] && echo "Missing bug title" && exit 1
	[ ! "$(GET desc)" ] && echo "Missing bug description" && exit 1
	if check_auth; then
		USER="$user"
	fi
	mkdir -p $bugdir/open/$id
	# bug.conf
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/open/$id/bug.conf << EOT
# SliTaz Bug configuration

BUG="$(GETfiltered bug)"
STATUS="OPEN"
PRIORITY="$(GET priority)"
CREATOR="$USER"
DATE="$date"
PKGS="$(GETfiltered pkgs)"
EOT
	# desc.txt
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/open/$id/desc.tmp << EOT
$(GETfiltered desc)
EOT
	fold -s -w 80 $bugdir/open/$id/desc.tmp > $bugdir/open/$id/desc.txt
	rm -f $bugdir/open/$id/*.tmp
}

# New bug page for the web interface
new_bug_page() {
	cat << EOT
<h2>$(gettext "New Bug")</h2>
<div id="newbug">

<form method="get" action="$script" onsubmit="return checkNewBug();">
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

# Edit/Save a bug
edit_bug() {
	. $bugdir/$id/bug.conf
	if admin_user || [ "$user" == "$CREATOR" ]; then
		continue
	else
		gettext "You can't edit someone else's bug!" && exit 0
	fi
	cat << EOT
<h2>$(eval_gettext 'Edit Bug $bug')</h2>
<div id="editbug">

<form method="get" action="$script">
	<input type="hidden" name="savebug" />
	<input type="hidden" name="id" value="$id" />
	<input type="hidden" name="creator" value="$CREATOR" />
	<input type="hidden" name="date" value="$DATE" />
	<table>
		<tbody>
			<tr>
				<td>$(gettext "Bug title")</td>
				<td><input type="text" name="bug" value="$BUG" /></td>
			</tr>
			<tr>
				<td>$(gettext "Description")</td>
				<td><textarea name="desc">$(cat $bugdir/$id/desc.txt)</textarea></td>
			</tr>
			<tr>
				<td>$(gettext "Packages")</td>
				<td><input type="text" name="pkgs" value="$PKGS" /></td>
			</tr>
			<tr>
				<td>$(gettext "Priority")</td>
				<td>
					<select name="priority">
						<option value="$PRIORITY">$PRIORITY</option>
						<option value="standard">$(gettext "Standard")</option>
						<option value="critical">$(gettext "Critical")</option>
					</select>
					<input type="submit" value="$(gettext 'Save configuration')" />
				</td>
			</tr>
		</tbody>
	</table>
</form>

</div>
EOT
}

save_bug() {
	id="$(GET id)"
	set_bugdir ${id}
	# bug.conf
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$id/bug.conf << EOT
# SliTaz Bug configuration

BUG="$(GETfiltered bug)"
STATUS="OPEN"
PRIORITY="$(GET priority)"
CREATOR="$(GET creator)"
DATE="$(GET date)"
PKGS="$(GETfiltered pkgs)"
EOT
	# desc.txt
	sed "s/$(echo -en '\r') /\n/g" > $bugdir/$id/desc.tmp << EOT
$(GETfiltered desc)
EOT
	fold -s -w 80 $bugdir/$id/desc.tmp > $bugdir/$id/desc.txt
	rm -f $bugdir/$id/*.tmp
}

# Close a fixed bug
close_bug() {
	sed -i s'/OPEN/CLOSED/' $bugdir/open/$id/bug.conf
	mv $bugdir/open/$id $bugdir/closed/$id
}

# Re open an old bug
open_bug() {
	sed -i s'/CLOSED/OPEN/' $bugdir/closed/$id/bug.conf
	mv $bugdir/closed/$id $bugdir/open/$id
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
	if [ ! -f "$AUTH_FILE" ]; then
		touch $AUTH_FILE && chmod 0600 $AUTH_FILE
	fi
	echo "$user:$pass" >> $AUTH_FILE
	mkdir -pm0700 $PEOPLE/${user}
	cat > $PEOPLE/$user/account.conf << EOT
# User configuration
NAME="$name"
USER="$user"
MAIL="$mail"
EOT
	chmod 0600 $PEOPLE/$user/account.conf
	# First created user is admin
	if [ $(ls ${PEOPLE} | wc -l) == "1" ]; then
		echo "$user" > ${ADMIN_USERS}
	fi
}

########################################################################
# POST actions                                                         #
########################################################################

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
		if [[ "$(POST id)" ]] ;then
			IDLOC="&id=$(POST id)"
		fi

		if [  ! -f $AUTH_FILE ] ; then
			js_log "$AUTH_FILE (defined in \$AUTH_FILE) has not been found."
			js_redirection_to "$script?login$IDLOC"
		fi;

		valid=$(fgrep "${user}:" $AUTH_FILE | cut -d ":" -f 2)
		if [ "$pass" == "$valid" ] && [ "$pass" != "" ]; then
			if [[ "$(POST id)" ]] ;then
				IDLOC="?id=$(POST id)"
			fi
			md5session=$(echo -n "$$:$user:$pass:$$" | md5sum | awk '{print $1}')
			mkdir -p $sessions
			# Log last login
			date '+%Y-%m-%d' > ${PEOPLE}/${user}/last
			echo "$md5session" > $sessions/$user
			js_set_cookie 'auth' "$user:$md5session"
			js_log "Login authentication has been executed & accepted :)"
			js_redirection_to "$script$IDLOC"
		else
			js_log "Login authentication has been executed & refused"
			js_redirection_to "$script?login&error$IDLOC"
		fi
		html_footer ;;
	*\ signup\ *)
		# POST action for online signup
		name="$(POST name)"
		user="$(POST user)"
		mail="$(POST mail)"
		pass="$(md5crypt "$(POST pass)")"
		if ! grep "^${user}:" $AUTH_FILE; then
			online="yes"
			new_user_config
			header "Location: $SCRIPT_NAME?login"
		else
			header
			html_header
			user_box
			echo "<h2>$(gettext "User already exists:") $user</h2>"
			html_footer && exit 0
		fi ;;
esac

#
# Plugins Now!
#

for p in $(ls -1 $plugins)
do
	[ -f "$plugins/$p/$p.conf" ] && . $plugins/$p/$p.conf
	[ -x "$plugins/$p/$p.cgi" ] && . $plugins/$p/$p.cgi
done

########################################################################
# GET actions                                                          #
########################################################################

case " $(GET) " in
	*\ README\ *)
		header
		html_header
		user_box
		echo '<h2>README</h2>'
		echo '<pre>'
		if [ -f "README" ]; then
			cat README
		else
			cat /usr/share/doc/tazbug/README
		fi
		echo '</pre>'
		html_footer ;;
	*\ closed\ *)
		# Show all closed bugs.
		header
		html_header
		user_box
		list_bugs "closed"
		echo "</pre>"
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
			js_redirection_to "$script"
		fi ;;
	*\ user\ *)
		# User profile. Use the users plugin for more functions
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
</pre>
EOT
		html_footer ;;
	*\ newbug\ *)
		# Create a bug from web interface.
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
		# Save a new bug
		header
		html_header
		if check_auth; then
			new_bug
			js_redirection_to "$script?id=$id"
		fi ;;
	*\ editbug\ *)
		# Edit existing bug
		header
		html_header
		id="$(GET editbug)"
		set_bugdir ${id}
		user_box
		edit_bug
		html_footer ;;
	*\ savebug\ *)
		header
		html_header
		if check_auth; then
			save_bug
			js_redirection_to "$script?id=$id"
		fi ;;
	*\ id\ *)
		header
		html_header
		id="$(GET id)"
		[ "$(GET close)" ] && close_bug
		[ "$(GET open)" ] && open_bug
		set_bugdir ${id}
		[ "$(GET msg)" ] && new_msg
		[ "$(GET delmsg)" ] && rm -f $bugdir/$id/msg.$(GET delmsg)
		msgs=$(fgrep MSG= $bugdir/$id/msg.* | wc -l)
		user_box
		bug_page
		html_footer ;;
	*\ signup\ *)
		# Signup
		header
		html_header
		user_box
		echo "<h2>$(gettext "Sign Up")</h2>"
		if [ "$ONLINE_SIGNUP" == "yes" ]; then
			signup_page
		else
			gettext "Online registration is disabled"
		fi
		html_footer ;;

	*\ search\ *)
		found=0
		header
		html_header
		user_box
		cat << EOT
<h2>$(gettext "Search")</h2>
<form method="get" action="$script">
	<input type="text" name="search" />
	<input type="submit" value="$(gettext 'Search')" />
</form>
<div>
EOT
		cd $bugdir
		for bug in *
		do
			result=$(fgrep -i -h "$(GET search)" $bug/*)
			if [ "$result" ]; then
				found=$(($found + 1))
				id=${bug}
				echo "<p><strong>Bug $id</strong> <a href=\"?id=$id\">"$(gettext 'Show')"</a></p>"
				echo '<pre>'
				fgrep -i -h "$(GET search)" $bugdir/$id/* | \
					sed s"/$(GET search)/<span class='ok'>$(GET search)<\/span>/"g
				echo '</pre>'
			fi
		done
		if [ "$found" == "0" ]; then
			echo "<p>$(gettext 'No result found for') : $(GET search)</p>"
		else
			echo "<p> $found $(gettext 'results found')</p>"
		fi
		echo '</div>'
		html_footer ;;
	*)
		# Default page.
		bugs=$(ls_bugs | wc -l)
		close=$(ls $bugdir/closed | wc -l)
		fixme=$(ls $bugdir/open  | wc -l)
		msgs=$(find $bugdir -name msg.* | wc -l)
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

<p>$(gettext "Please read the <a href=\"?README\">README</a> for help and \
more information. You may also be interested by the SliTaz \
<a href=\"http://roadmap.slitaz.org/\">Roadmap</a> and the packages \
<a href=\"http://cook.slitaz.org/\">Cooker</a>. To perform a search \
enter your term and press ENTER.")
</p>

<div id="tools">
	$BUGS_TOOLS
	<a href="?closed">$(gettext 'Closed bugs')</a>
EOT
		if check_auth; then
			echo "<a href='?newbug'>$(gettext 'Create bug')</a>"
			echo "$PLUGINS_TOOLS"
		fi
		cat << EOT
</div>

<h3>$(gettext "Latest Bugs")</h3>
EOT
		# List last 4 bugs
		echo "<pre>"
		for lb in $(ls_bugs | sort -n -r | head -n 4)
		do
			list_bug ${lb}
		done
		echo "</pre>"
		
		# List last 4 messages
		echo "<h3>$(gettext "Latest Messages")</h3>"
		echo "<pre>"
		
		for msg in $(ls -r $bugdir/*/*/msg.* | head -n 4)
		do
			list_msg ${msg}
		done
		echo "</pre>"
		list_bugs open
		echo "</pre>"
		html_footer ;;
esac

exit 0
