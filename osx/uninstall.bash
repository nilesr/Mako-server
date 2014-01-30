#!/usr/bin/env bash
if test $EUID -ne 0; then
	echo "Must be root"
	exit 1
fi
launchctl unload /Library/LaunchDaemons/com.niles.mako-server.plist
launchctl remove com.niles.mako-server
rm -rf /Library/LaunchDaemons/com.niles.mako-server.plist /usr/local/bin/mako-server-start /usr/local/bin/mako-server-stop /usr/local/bin/mako-server-restart

echo "Uninstall script completed"