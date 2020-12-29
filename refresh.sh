/usr/bin/sudo pkill -F /home/llhost/Dev/metarmap/offpid.pid
/usr/bin/sudo pkill -F /home/llhost/Dev/metarmap/metarpid.pid
/usr/bin/sudo /usr/bin/python3 /home/llhost/Dev/metarmap/metar.py & echo $! > /home/llhost/Dev/metarmap/metarpid.pid
