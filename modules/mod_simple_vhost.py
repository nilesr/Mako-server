import sys,os,re,traceback
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	try:
		import mod_default
		global mod_default
		kargs['log']("The mod_default module will print a load message. mod_simple_vhost uses mod_default to serve up it's files")
		mod_default.onLoad(log=kargs['log'],config=kargs['config'])
		global sets
		sets = []
		for set in kargs["config"].get("mod_simple_vhost","sets").split(kargs["config"].get("general","listDelimiter")):
			sets.append([kargs["config"].get("mod_simple_vhost",set+"-host"),kargs["config"].get("mod_simple_vhost",set+"-root")])
		kargs['log']("mod_simple_vhost loaded")
	except:
		kargs['log']("Your vhost settings are incorrect")
		sys.exit(1)
	kargs['log']("Simple vhost module loaded")
def onRequest(**kargs):
	for set in sets:
		if re.match(set[0],kargs['environ']['HTTP_HOST']):
			return mod_default.onRequest(root=set[1],start_response=kargs['start_response'],environ=kargs['environ'],log=kargs['log'],logfile=kargs['logfile'],serverError=kargs['serverError'],config=kargs['config'],file=kargs['file'],getfield=kargs['getfield'])
	return False
