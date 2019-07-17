#!/bin/bash

HALT=4

# Initialize GPIO states
gpio -g mode  $HALT    up

python3 /home/pi/postbox/secret.py

while :
do
	# Check for halt button
	if [ $(gpio -g read $HALT) -eq 0 ]; then
		# Must be held for 2+ seconds before shutdown is run...
		starttime=$(date +%s)
		while [ $(gpio -g read $HALT) -eq 0 ]; do
			if [ $(($(date +%s)-starttime)) -ge 5 ]; then
				shutdown -h now
			fi
		done
	fi
done
