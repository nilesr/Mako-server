import sys,os
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	try:
		global order, orderString
		orderString = kargs['config'].get("mod_logging","order")
		order = kargs['config'].get("mod_logging","order").split(kargs['config'].get("general","listDelimiter"))
	except:
		kargs['log']("There is a problem in your mod_logging configuration")
		sys.exit(1)
	kargs['log']("Logging module loaded")
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
	return False