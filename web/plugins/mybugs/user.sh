#!/bin/sh
#
# This script display bug for a given user. A copy is used on SCN to
# display user bugs on profile page with a custom config file to set
# $bugdir.
#
[ -f "$plugins/mybugs/user.conf" ] && . $plugins/mybugs/user.conf

echo "<h3>My bugs</h3>"
echo "<pre>"
for bug in $(fgrep -l $user ${bugdir}/*/*/bug.conf | xargs ls -lt | awk '{print $9}')
do
	. ${bug}
	id=$(basename $(dirname $bug))
	cat << EOT
<img src='images/bug.png' alt='' /> \
Bug $id: <a href="?id=$id">$BUG</a> <span class="date">- $DATE</span>
EOT
done
echo "</pre>"
