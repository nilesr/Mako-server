import sys,os,re,ConfigParser
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
		global sets
		#**
		#* "sets" is a dictionary, which contains a dynamic amount of dictionaries, which contains two values: "conditions" and "change". Conditions is a list with a dynamic number of lists, each with two values: an environment variable and a regular expression. change contains a list of two values, both halves of a regular expression
		sets = dict()
		global log
		log = bool(int(kargs["config"].get("mod_rewrite","log")))
		for set in kargs["config"].get("mod_rewrite","sets").split(kargs["config"].get("general","listDelimiter")):
			try:
				sets[set] = dict()
				sets[set]['conditions'] = []
				sets[set]['change'] = kargs["config"].get("mod_rewrite",set+"-change").split(kargs["config"].get("general","listDelimiter"))
				i = 1
				while True:
					sets[set]['conditions'].append(kargs["config"].get("mod_rewrite",set+"-condition-"+str(i)).split(kargs["config"].get("general","listDelimiter")))
					i += 1
			except ConfigParser.NoOptionError:
				continue
		kargs['log']("mod_rewrite loaded")
		kargs['log']("Loaded rewrite rules: " + str(sets))
	except:
		kargs['log']("Your mod_rewrite settings are incorrect")
		sys.exit(1)
	kargs['log']("mod_rewrite module loaded")
#**
#* For each set, loop through each condition to see if that set applies. If it does, execute the regular expression on the PATH_INFO environment variable and log a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool false, dictionary environment
def onRequest(**kargs):
	for set in sets:
		apply = True
		for condition in sets[set]['conditions']:
			if condition[0] == "bypass":
				apply = True
				continue
			if not re.match(condition[1],kargs['environ'][condition[0]]):
				apply = False
				continue
		if apply:
			if log:
				logmessage = set + " is rewriting '" + kargs['environ']['PATH_INFO']
			kargs['environ']['PATH_INFO'] = re.sub(sets[set]['change'][0],sets[set]['change'][1],kargs['environ']['PATH_INFO'])
			if log:
				logmessage += "' to '" + kargs['environ']['PATH_INFO'] + "'"
				kargs['log'](logmessage)
	return False, kargs['environ']

