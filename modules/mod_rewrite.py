import sys,os,re,ConfigParser
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	try:
		global sets
		sets = dict() # "sets" is a dictionary, which contains a dynamic amount of dictionaries, which contains two values: "conditions" and "change". Conditions contains a dynamic number of lists, each with two values, an environment variable and a regular expression. change contains a list of two values, both halves of a regular expression
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
	except:
		kargs['log']("Your vhost settings are incorrect")
		sys.exit(1)
	kargs['log']("Simple vhost module loaded")
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
			logmessage = set + " is rewriting '" + kargs['environ']['PATH_INFO']
			kargs['environ']['PATH_INFO'] = re.sub(sets[set]['change'][0],sets[set]['change'][1],kargs['environ']['PATH_INFO'])
			logmessage += "' to '" + kargs['environ']['PATH_INFO'] + "'"
			kargs['log'](logmessage)
	return False, kargs['environ']

