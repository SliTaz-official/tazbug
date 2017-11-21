#!/bin/sh
#
# TazBug Plugin - Buggy packages plugins
#

if [ "$(GET packages)" ] || [ "$(GET pkg)" ]; then
	d="Skel"
	header
	html_header
	user_box
	if [ "$(GET pkg)" ]; then
		pkg=$(GET pkg)
		echo "<h2>Bugs for: $pkg</h2>"
		echo "<pre>"
		for bug in $(fgrep -l "OPEN" $bugdir/open/*/bug.conf)
		do
			. ${bug}
			if echo "$PKGS" | fgrep -q "$pkg"; then
				dir=$(dirname $bug)
				id=$(basename $dir)
				cat << EOT
<img src='images/pkg.png' alt='' /> \
Bug $id: <a href='$script?id=$id'>$BUG</a> - <span class='date'>$DATE</span>
EOT
			fi
		done
		cat << EOT
</pre>
<div id="tools">
	<a href="$script?packages">Buggy packages</a>
</div>
EOT
	else
		# List all pkgs affected by a bug
		cat << EOT
<h2>Buggy packages</h2>
<div id="plugins">
<table>
	<thead>
		<td>$(gettext "Package name")</td>
		<td>$(gettext "Bug date")</td>
		<td>$(gettext "Action")</td>
	</thead>
EOT
		for bug in $(ls $bugdir/open)
		do
			. ${bugdir}/open/${bug}/bug.conf
			for pkg in ${PKGS}; do
				count=1
				if ! echo "$pkgs" | grep -q -w "$pkg"; then
					pkgs="$pkgs $PKGS"
				else
					count_${pkg}=$(($count + 1))
				fi
			unset PKGS
			done
		done
		for pkg in $pkgs; do
			cat << EOT
	<tr>
		<td><img src='images/pkg.png' alt='' /> <a href='?pkg=$pkg'>$pkg</a></td>
		<td>$count_pkg</td>
		<td>TODO</td>
	</tr>
EOT
		done
		echo "</table></div>"
	fi
	html_footer
	exit 0
fi
