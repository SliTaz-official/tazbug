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
		for bug in $(fgrep -l "OPEN" $bugdir/*/bug.conf)
		do
			. ${bug}
			if echo "$PKGS" | fgrep -q "$pkg"; then
				dir=$(dirname $bug)
				id=$(basename $dir)
				echo "ID: $id <a href='$script?id=$id'>$BUG</a> \
<span class='date'>$DATE</span>"
			fi
		done
		echo "</pre>"
	else
		# List all pkgs affected by a bug
		echo "<h2>Buggy packages</h2>"
		echo "<pre>"
		for bug in $(fgrep -l "OPEN" $bugdir/*/bug.conf)
		do
			. ${bug}
			pkgs="$pkgs $PKGS"
			unset PKGS
		done
		for pkg in $pkgs; do
			echo "<a href='?pkg=$pkg'>$pkg</a> "
		done
		echo "</pre>"
	fi
	html_footer
	exit 0
fi
