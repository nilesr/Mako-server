import sys,os
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
#**
#* Loads the relevant configuration options, and logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	try:
		global order
		order = kargs['config'].get("mod_logging","order").split(kargs['config'].get("general","listDelimiter"))
	except:
		kargs['log']("There is a problem in your mod_logging configuration")
		sys.exit(1)
	kargs['log']("Logging module loaded")
#**
#* For each request, log the relevant environment information
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
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
		kargs['log'](result[0:-1])
	except:
		kargs['log']("There is a problem in the mod_logging configuration")
	return False, kargs['environ']