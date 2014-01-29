#!/usr/bin/env python -O
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages/")
import cgi, re, os, mimetypes, ConfigParser, subprocess, glob, signal, time
def log(missive):
	if logfile:
		logfileobject = open(logfile,'w')
		logfileobject.write(sys.argv[0] + " " + time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + missive + "\r\n")
		logfileobject.close()
	print sys.argv[0] + " " + time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + missive
def serverError(start_response,status,filename=""):
	if status == 500:
		start_response("500 Internal Server Error", [('Content-type','text/html')])
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(__file__))+'/temporary_files').get_template("error-500.pyhtml").render(filename=filename,config=config)
	elif status == 404:
		start_response("404 Not found", [('Content-type','text/html')])
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(__file__))+'/temporary_files').get_template("error-404.pyhtml").render(filename=filename,config=config)
	elif status == 403:
		start_response("403 Permission denied", [('Content-type','text/html')])
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(__file__))+'/temporary_files').get_template("error-403.pyhtml").render(filename=filename,config=config)
	else:
		log("You dun fucked up")
		sys.exit(1)
def serve(environ, start_response):
	for module in moduleObjects:
		returnvalue = module.onRequest(start_response=start_response,environ=environ,log=log,logfile=logfile,root=root,serverError=serverError,config=config,file=__file__)
		if returnvalue:
			return returnvalue
		
def getfield(f):
	# convert values from cgi.Field objects to plain values.
	if isinstance(f, list):
		return [getfield(x) for x in f]
	else:
		return f.value

if __name__ == '__main__':
	if not os.path.isdir(os.path.dirname(os.path.realpath(__file__))+'/temporary_files'):
		try:
			os.makedirs(os.path.dirname(os.path.realpath(__file__))+'/temporary_files')
		except:
			log("Failed to create temporary_files directory")
			sys.exit(1)
	if not os.path.isdir(os.path.dirname(os.path.realpath(__file__))+'/modules'):
		try:
			os.makedirs(os.path.dirname(os.path.realpath(__file__))+'/modules')
		except:
			log("Failed to create modules directory")
			sys.exit(1)
	from mako.lookup import TemplateLookup
	from mako import exceptions
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	mimetypes.init()
	config = ConfigParser.SafeConfigParser()
	configfile = os.path.dirname(os.path.realpath(__file__)) + "/config.conf"
	logfile = False
	def signaled(sihipsterm, stack):
		log("Caught signal " + str(sihipsterm) + ", exiting.")
		try:
			os.remove(pidfile)
		except OSError:
			log("Failed to delete pid file. It might have vanished while we were running, or I didn't have permission to create it in the first place")
		sys.exit(0)
	for i in [2,3,6,15]:
		try:
			#sihipsterm = getattr(signal,i)
			signal.signal(i,signaled)
		except RuntimeError,m:
			pass

	if __debug__:	# Alright, I have NO IDEA why, but if you don't start python with -O, it throws NoneType and "write() argument must be string" exceptions, then just closes the connection. 
		log("Restarting with -O")
		listofarguments = ["/usr/bin/env", "python", "-O"]
		for argument in sys.argv:
			if argument == __file__:
				continue
			listofarguments.append(argument)
		listofarguments.append(__file__)
		log("Calling " + " ".join(listofarguments))
		try:
			sys.exit(subprocess.call(listofarguments))
		except:
			sys.exit(1)
	pidfile = subprocess.check_output(["/usr/bin/env","mktemp","/tmp/mako.XXXXXX"])[0:-1]
	nextarg=""
	killkillKILL = True
	for argument in sys.argv:
		if argument == "-h" or argument.lower() == "--help":
			log("Usage: ./server.py [-h|--help] [<--pidfile|-P> <pidfile>] [<--config-file|-c> <config.conf>] [--suppress-urge-to-kill]")
			sys.exit(0)
		if nextarg == "pidfile":
			os.remove(pidfile)
			pidfile = argument
			nextarg=""
			continue
		if nextarg == "config":
			configfile = argument
			nextarg=""
			continue
	#	if argument == "-d" or argument.lower() == "--daemon":
	#		daemonize = True
	#		continue
		if argument == "-P" or argument.lower() == "--pidfile":
			nextarg = "pidfile"
			continue
		if argument == "-c" or argument.lower() == "--config-file":
			nextarg = "config"
			continue
		if argument.lower() == "--suppress-urge-to-kill":
			killkillKILL = False
	try:
		config.readfp(open(configfile))
	except:
		log("Config file read failure")
		sys.exit(1)
	if killkillKILL:
		for otherpidfile in glob.glob("/tmp/mako.*"):
			if otherpidfile == pidfile:
				continue
			otherpidfileobject = open(otherpidfile,'r')
			try:
				otherpid = int(otherpidfileobject.read())
			except:
				pass
			try:
				os.kill(otherpid,3)
			except OSError:
				try:
					os.kill(otherpid,9)
				except OSError:
					#log("Either the other process has ended, or I don't have permission to kill it.")
					pass
			except:
				pass
			otherpidfileobject.close()
			os.remove(otherpidfile)
	pidfileobject = open(pidfile,'w')
	pidfileobject.write(str(os.getpid()))
	pidfileobject.close()
	root = config.get("server","root")
	try:
		port = int(config.get("server","port"))
	except ValueError:
		log("The port in config.conf must be an integer")
		sys.exit(1)
	try:
		servestaticfiles = bool(int(config.get("server","servestaticfiles")))
	except:
		log("The servestaticfiles value in config.conf should be a 1 or a 0")
	try:
		listdirectories = bool(int(config.get("server","listdirectories")))
	except:
		log("The listdirectories value in config.conf should be a 1 or a 0")
	logfile = config.get("server","logfile")
	import wsgiref.simple_server
	server = wsgiref.simple_server.make_server('', port, serve)
	for file in glob.glob(os.path.dirname(os.path.realpath(__file__))+'/modules/*.pyo'):
		os.remove(file)
	modules = config.get("server","modules").split(config.get("general","listDelimiter"))
	sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/modules')
	moduleObjects = map(__import__, modules)
	for module in moduleObjects:
		module.onLoad(config=config)
	log("Server listening on port " + str(port))
	server.serve_forever()


