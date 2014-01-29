import sys,os,re
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	kargs['log']("Logging module loaded")
def onRequest(**kargs):
	kargs['log'](kargs['environ']['REMOTE_ADDR'] + " " + kargs['environ']['REQUEST_METHOD'] + " " + kargs['environ']['PATH_INFO'] + " " + kargs['environ']['HTTP_USER_AGENT'])
	return False