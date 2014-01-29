import sys,os,re,ConfigParser
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	try:
		global sets
		sets = dict()
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
		print sets
	except:
		kargs['log']("Your vhost settings are incorrect")
		sys.exit(1)
	kargs['log']("Simple vhost module loaded")
def onRequest(**kargs):
	for set in sets:
		pass
	return False, kargs['environ']

