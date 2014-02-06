import sys,os,re,ConfigParser,traceback
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
#**
#* Loads the relevant configuration options, and logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-30
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	try:
		global sets
		sets = {}
		global log
		log = bool(int(kargs["config"].get("mod_path_to_cgi","log")))
		for set in kargs["config"].get("mod_path_to_cgi","sets").split(kargs["config"].get("general","listDelimiter")):
			try:
				sets[set] = (kargs["config"].get("mod_path_to_cgi",set).split(kargs["config"].get("general","listDelimiter")))
			except ConfigParser.NoOptionError:
				kargs['log'](traceback.format_exc())
				continue
	except:
		kargs['log'](traceback.format_exc())
		kargs['log']("Your mod_path_to_cgi settings are incorrect")
		sys.exit(1)
	kargs['log']("mod_path_to_cgi loaded")
	kargs['log']("Loaded path to cgi rules: " + str(sets))

#**
#* For each set, apply the regular expression to change the path, and append the name of the set to the cgi variable, with the value of the url, minus the regular expression.
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-30
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool false, dictionary environment
def onRequest(**kargs):
	new_environ = kargs['environ'].copy()
	for set in sets:
		try:
			if re.match(sets[set][0],new_environ['PATH_INFO']):
				new_environ['QUERY_STRING'] = new_environ['QUERY_STRING'] + "&" + set + "=" + re.sub(sets[set][0],"",new_environ['PATH_INFO'])
				if new_environ['QUERY_STRING'][-1] == "/":
					new_environ['QUERY_STRING'] = new_environ['QUERY_STRING'][0:-1]
				newpath = re.sub(sets[set][0] + ".*",sets[set][1],new_environ['PATH_INFO'])
				if log:
					kargs['log']("New path: " + newpath)
				new_environ['PATH_INFO'] = newpath
		except:
			kargs['log'](traceback.format_exc())
	return False, new_environ

