/usr/bin/sudo pkill -F /home/pi/blinkpid.pid
/usr/bin/sudo pkill -F /home/pi/offpid.pid
/usr/bin/sudo pkill -F /home/pi/metarpid.pid
/usr/bin/sudo /usr/bin/python3 /home/pi/blink.py & echo $! > /home/pi/blinkpid.pid
