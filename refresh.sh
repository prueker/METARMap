/usr/bin/sudo pkill -F /home/kody/offpid.pid
/usr/bin/sudo pkill -F /home/kody/metarpid.pid
/usr/bin/sudo /usr/bin/python3 /home/kody/metar.py & echo $! > /home/kody/metarpid.pid
