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
				echo "Bug $id: <a href='$script?id=$id'>$BUG</a> \
- <span class='date'>$DATE</span>"
			fi
		done
		echo "</pre>"
	else
		# List all pkgs affected by a bug
		echo "<h2>Buggy packages</h2>"
		echo "<pre>"
		for bug in $(ls $bugdir/open)
		do
			. $bugdir/open/${bug}/bug.conf
			for pkg in ${PKGS}; do
				if ! echo "$pkgs" | grep -q -w "$pkg"; then
					pkgs="$pkgs $PKGS"
				fi
			unset PKGS
			done
		done
		for pkg in $pkgs; do
			echo "Package: <a href='?pkg=$pkg'>$pkg</a>"
		done
		echo "</pre>"
	fi
	html_footer
	exit 0
fi
