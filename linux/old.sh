#!/bin/bash
if ! test $EUID -eq 0; then
	echo got root?
	exit 1
fi
echo How do you run your program? Include full paths, and no quotes
echo "Example: '/etc/mako-server/server.py' or '/etc/mako-server/server.py -P /var/run/mako-server.pid'"
read -p "> " arguments
echo What user should run this program?
echo "Example: '_www', 'www-data'"
echo "IMPORTANT! Make sure this user can modify the directory the server is in (or at least temporary_files), as well as the logfile"
read -p "> " user
echo script > /etc/init/mako-server.conf
echo sudo -u $user $arguments >> /etc/init/mako-server.conf
echo end script >> /etc/init/mako-server.conf
echo start on startup >> /etc/init/mako-server.conf
echo Installed. Start server now?
echo -n "[y]> "
read yn
if test "$yn" == "" || test "$yn" == "y" || test "$yn" == "Y"; then
	echo Starting
	service mako-server start	
else
	echo Aborting.
fi
echo This installer uses upstart. To control your server, use:
echo
echo sudo service mako-server '<'start'|'stop'|'restart'|'status'>'
echo
echo Installer exiting. mako-server configured to start on boot.
echo The mako-server upstart process will not restart if it fails.
