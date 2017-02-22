#!/bin/sh
#
# TazBug Plugin - Textmode will output plain data to be used by remote client
#

if [ "$(GET textmode)" ]; then
	header "Content-type: text/plain; charset=UTF-8"
	
	separator() {
		echo "-------------------------------------------------------------------------------"
	}
	
	case " $(GET) " in
		
	*\ stats\ *)
		echo "Bugs count     : $(ls_bugs | wc -l)"
		echo "Messages count : $(find $bugdir -name msg.* | wc -l)"
		echo "Database size  : $(du -sh $bugdir | awk '{print $1}')" ;;
	
	*\ search\ *)
		for bug in $(ls_bugs)
		do
			set_bugdir "$bug"
			result=$(fgrep -i -h "$(GET search)" $bugdir/$bug/*)
			if [ "$result" ]; then
				found=$(($found + 1))
				. ${bugdir}/${bug}/bug.conf
				echo "Bug: $bug - $BUG"
			fi
			bugdir=$(dirname $bugdir)
		done
		if [ "$found" == "" ]; then
			echo "No result found for: $(GET search)"
		else
			separator && echo "$found result(s) found"
		fi ;;
	
	*\ id\ *)
		# Show bug information and description
		id=$(GET id)
		set_bugdir "$id"
		if [ -f "$bugdir/$id/bug.conf" ]; then
			. ${bugdir}/${id}/bug.conf
			cat << EOT
Bug      : $id - $STATUS - $PRIORITY
Title    : $BUG
Info     : $DATE - Creator: $CREATOR
$(separator)
$(cat $bugdir/$id/desc.txt)
EOT
		else
			echo "Can't find bug ID: $id" && exit 0
		fi ;;
	
	*)
		cat << EOT
Tazbug Textmode plugin
$(separator)
$(date)

Functions: 
  &stats      Display bug tracker stats
  &search=    Search for bugs by pattern
  &id=        Show bug info and description
EOT
		;;
	esac
	exit 0
fi
