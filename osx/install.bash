#!/usr/bin/env bash
if test $EUID -ne 0; then
	echo "Must be root"
	exit 1
fi
echo How do you run your program? Include full paths, and no quotes
echo "Example: '/usr/bin/env python -O /etc/mako-server/server.py' or '/etc/mako-server/server.py -P /var/run/mako-server.pid'"
read -p "> " arguments
echo What user should run this program?
echo "Example: '_www'"
read -p "> " user

echo '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>Disabled</key>
<false/>
<key>Label</key>
<string>com.niles.mako-server</string>
<key>OnDemand</key>
<false/>
<key>ProgramArguments</key>
<array>
' > temp.plist
for x in $arguments; do
	echo "<string>$x</string>" >> temp.plist
done
echo '</array>
<key>UserName</key>
<string>$user</string>
</dict>
</plist>' >> temp.plist
mv temp.plist /Library/LaunchDaemons/com.niles.mako-server.plist
launchctl load -w /Library/LaunchDaemons/com.niles.mako-server.plist
echo Installed and running.
echo "#!/usr/bin/env bash" > /usr/local/bin/mako-server-start
echo "launchctl load -w /Library/LaunchDaemons/com.niles.mako-server.plist" >> /usr/local/bin/mako-server-start
echo "#!/usr/bin/env bash" > /usr/local/bin/mako-server-stop
echo "launchctl unload /Library/LaunchDaemons/com.niles.mako-server.plist" >> /usr/local/bin/mako-server-stop
echo "#!/usr/bin/env bash" > /usr/local/bin/mako-server-restart
echo "launchctl unload /Library/LaunchDaemons/com.niles.mako-server.plist" >> /usr/local/bin/mako-server-stop
echo "launchctl load -w /Library/LaunchDaemons/com.niles.mako-server.plist" >> /usr/local/bin/mako-server-restart
chmod +x /usr/local/bin/mako-server-start /usr/local/bin/mako-server-stop /usr/local/bin/mako-server-restart
