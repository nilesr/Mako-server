import sys, os, socket, threading,traceback
#**
#* Creates a daemon to return PING requests and join the channel
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			076
#* @since			2014-02-05
#* @params			none
#* @returns			bool true
def daemon():
	while True:
		text=ircSocket.recv(2040)
		if text.find("PING") != -1:
			ircSocket.send("PONG " + text.split()[1] + "\r\n")
		if text.find("001") != -1:
			ircSocket.send("JOIN #" + channel + "\r\n")

#**
#* Loads the relevant configuration options, connects to the server, and logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			076
#* @since			2014-02-05
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	try:
		global server, channel, nickname, order
		server = kargs["config"].get("mod_irc_logging","server")
		channel = kargs["config"].get("mod_irc_logging","channel")
		nickname = kargs["config"].get("mod_irc_logging","nickname")
		order = kargs["config"].get("mod_irc_logging","order").split(kargs['config'].get("general","listDelimiter"))
	except:
		kargs["log"]("There is a problem in your mod_irc_logging configuration")
		sys.exit(1)
	global ircSocket
	ircSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	kargs['log']("Connecting to: "+server)
	ircSocket.connect((server, 6667))
	ircSocket.send("USER "+ nickname +" "+ nickname +" "+ nickname +" :mod_irc_logging\r\n")
	ircSocket.send("NICK "+ nickname +"\r\n")
	t = threading.Thread(target=daemon)
	t.daemon = True
	t.start()
#**
#* For each request, log the relevant environment information to IRC
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			076
#* @since			2014-02-05
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool false, dictionary environment
def onRequest(**kargs):
	try:
		result = ""
		for x in order:
			if x in kargs['environ']:
				result += kargs['environ'][x] + " "
			else:
				result += x + " "
		ircSocket.send("PRIVMSG #" + channel + " :" + result[0:-1] + "\r\n")
	except:
		kargs['log']("There is a problem in the mod_irc_logging configuration")
		kargs['log'](traceback.format_exc())
	return False, kargs['environ']