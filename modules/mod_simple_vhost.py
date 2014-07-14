import sys,os,re
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
#**
#* Loads the relevant configuration options, imports mod_default, and logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	try:
		import mod_default
		global mod_default
		kargs['log']("Info: The mod_default module will now print a load message. Please note that this does not mean that mod_default is in this position in the module order. mod_simple_vhost uses mod_default to serve up it's files")
		mod_default.onLoad(log=kargs['log'],config=kargs['config'])
		global sets
		sets = []
		#**
		#* sets is a list of lists, each containing two strings, a regular expression and a document root to be applied if the host matches that regular expression
		for set in kargs["config"].get("mod_simple_vhost","sets").split(kargs["config"].get("general","listDelimiter")):
			sets.append([kargs["config"].get("mod_simple_vhost",set+"-host"),kargs["config"].get("mod_simple_vhost",set+"-root")])
		kargs['log']("mod_simple_vhost loaded")
	except:
		kargs['log']("Your vhost settings are incorrect")
		sys.exit(1)
	kargs['log']("Simple vhost module loaded")
#**
#* For each set, check if the set applied and if it did, serve the request with the document root specified in the config file. If no set applies, continue to the next module in the execution order
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			(string a response rendered by mod_default, dictionary environment) or (bool false, dictionary environment)
#* @see				mako-server.modules.mod_default.onRequest
def onRequest(**kargs):
	for set in sets:
		if re.match(set[0],kargs['environ']['HTTP_HOST']):
			return mod_default.onRequest(root=set[1],start_response=kargs['start_response'],environ=kargs['environ'],log=kargs['log'],logfile=kargs['logfile'],serverError=kargs['serverError'],config=kargs['config'],file=kargs['file'],getfield=kargs['getfield'])
	return False, kargs['environ']