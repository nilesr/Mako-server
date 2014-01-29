import sys,os,re
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
def onLoad(**kargs):
	print "Worst case scenario module loaded"
def onRequest(**kargs):
	#set headers to 500
	return TemplateLookup(directories=os.path.dirname(os.path.realpath(kargs["file"])),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template("error-no-module.pyhtml").render(filename=filename,config=kargs["config"],d=d,uri=uri)
