import sys,os
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	try:
		orderString = config.get("mod_logging","order")
		order = config.get("mod_logging","order").split(config.get("general","listDelimiter"))
	except:
		kargs['log']("There is a problem in your mod_logging configuration")
	kargs['log']("Logging module loaded")
def onRequest(**kargs):
	try:
		result = ""
		for x in order:
			result += kargs['environ'][x] + " "
		kargs['log'](result[0:-1])
	except:
		kargs['log']("There is a problem in the mod_logging configuration")
	return False