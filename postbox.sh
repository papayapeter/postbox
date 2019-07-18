#!/bin/bash

python3 /home/pi/postbox/postbox.py &

HALT=4

while :
do
	# Check for halt button
	if [ $(gpio -g read $HALT) -eq 0 ]; then
		# Must be held for 2+ seconds before shutdown is run...
		starttime=$(date +%s)
		while [ $(gpio -g read $HALT) -eq 0 ]; do
			if [ $(($(date +%s)-starttime)) -ge 10 ]; then
				gpio -g write $LED 1
				shutdown -h now
			fi
		done
	fi
done
