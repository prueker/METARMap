#!/bin/bash

if [[ $1 == "on" ]]; then
	( crontab -l | grep -v -F "/home/pi/lightsoff.sh --auto1" ) | crontab -
	( crontab -l | grep -v -F "/home/pi/refresh.sh --auto2" ) | crontab -
	( crontab -l | grep -v -F "/home/pi/lightsoff.sh --auto2" ) | crontab -

	croncmd="/home/pi/refresh.sh --auto1"
	cronjob="*/5 * * * * $croncmd"
	( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

	./refresh.sh | grep 'Done' &> /dev/null
	if [ $? == 0 ]; then
	   echo "METAR Map is on!"
	fi
elif [[ $1 == "off" ]]; then
	( crontab -l | grep -v -F "/home/pi/refresh.sh --auto1" ) | crontab -
	( crontab -l | grep -v -F "/home/pi/refresh.sh --auto2" ) | crontab -
	( crontab -l | grep -v -F "/home/pi/lightsoff.sh --auto2" ) | crontab -

	croncmd="/home/pi/lightsoff.sh --auto1"
	cronjob="*/10 * * * * $croncmd"
	( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

	./lightsoff.sh | grep 'LEDs off' &> /dev/null
	if [ $? == 0 ]; then
	   echo "METAR Map is off!"
	fi
elif [[ $1 == ??-?? ]] || [[ $1 == ?-?? ]] || [[ $1 == ??-? ]] || [[ $1 == ?-? ]]; then
	input="$1"
	arr=(${input//-/ })
	time1=${arr[0]}
	time2=${arr[1]}
	time1=`expr $time1 + 0`
	time2=`expr $time2 - 1`

	if [[ $time1 == 24 ]]; then time1=0; fi
	if [[ $time2 == 24 ]]; then time2=0; fi
	if [[ $time2 == -1 ]]; then time2=23; fi

	if [[ $time2 -lt $time1 ]]; then time2=23; fi

	if [[ $time1 -lt 24 ]] && [[ $time2 -lt 24 ]]; then
		( crontab -l | grep -v -F "/home/pi/refresh.sh --auto1" ) | crontab -
		( crontab -l | grep -v -F "/home/pi/lightsoff.sh --auto1" ) | crontab -
		( crontab -l | grep -v -F "/home/pi/refresh.sh --auto2" ) | crontab -
		( crontab -l | grep -v -F "/home/pi/lightsoff.sh --auto2" ) | crontab -

		dur="$time1-$time2"
		time3=`expr $time2 + 1`
		if [[ $time3 == 24 ]]; then time3=0; fi

		croncmd="/home/pi/refresh.sh --auto2"
		cronjob="*/5 $dur * * * $croncmd"
		( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab 
		croncmd="/home/pi/lightsoff.sh --auto2"
		cronjob="00 $time3 * * * $croncmd"
		( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab

		time_now=$( date +'%H' )
		if [[ $time_now -gt $time1 ]] && [[ $time_now -le $time2 ]]; then
			./refresh.sh | grep 'Done' &> /dev/null
			if [ $? == 0 ]; then
			   echo "METAR Map is on!"
			   echo "Hours: $time1-$time3"
			fi
		else
			./lightsoff.sh | grep 'LEDs off' &> /dev/null
			if [ $? == 0 ]; then
			   echo "METAR Map is off!"
			   echo "Hours: $time1-$time3"
			fi
		fi
	else
		echo "METAR Map status unknown!"
		echo "Hour range not valid!"
	fi
elif [[ $1 == "shutdown" ]]; then
	./lightsoff.sh | grep 'LEDs off' &> /dev/null
	if [ $? == 0 ]; then
	   echo "METAR Map is off!"
	   echo "Raspberry Pi is shutting down!"
	fi
	(sleep 5 && sudo shutdown now &> /dev/null) &
else
	echo "METAR Map status unknown!"
	echo "Input not valid!"
fi