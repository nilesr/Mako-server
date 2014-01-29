import sys,os,re
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	try:
		
	except:
		kargs['log']("Your vhost settings are incorrect")
		sys.exit(1)
	kargs['log']("Simple vhost module loaded")
def onRequest(**kargs):
	