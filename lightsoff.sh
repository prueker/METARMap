/usr/bin/sudo pkill -F /home/pi/offpid.pid
/usr/bin/sudo pkill -F /home/pi/metarpid.pid
/usr/bin/sudo /usr/bin/python3 /home/pi/pixelsoff.py & echo $! > /home/pi/offpid.pid
