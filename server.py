#!/usr/bin/env python -O
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages/")
import cgi, re, os, mimetypes, ConfigParser, subprocess, glob, signal, time,traceback
#**
#* Logs a message, to both stdout and a logfile, if applicable
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			missive 
#* @returns			True
def log(missive):
	if logfile:
		try:
			logfileobject = open(logfile,'w')
			logfileobject.write(sys.argv[0] + " " + time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + missive + "\r\n")
			logfileobject.close()
		except OSError:
			print "Error opening logfile. Non-fatal"
	print sys.argv[0] + " " + time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + missive
#**
#* Sends an error message to the client
#* <p>
#* Uses the start_response to set headers. If the headers are already set, it just returns the rendered error file. Note that the "filename" parameter is refered to as "uri" in most of the rest of the program.
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function start_response, int status, optional str filename
#* @returns			A string equal to the rendered view of a mako template, which is then in theory sent to the client
def serverError(start_response,status,filename=""):
	if status == 500:
		try:
			start_response("500 Internal Server Error", [('Content-type','text/html')])
		except: # This hapends if the headers were already set by something else
			pass
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(__file__))+'/temporary_files').get_template("error-500.pyhtml").render(filename=filename,config=config)
	elif status == 404:
		try:
			start_response("404 Not found", [('Content-type','text/html')])
		except: # This hapends if the headers were already set by something else
			pass
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(__file__))+'/temporary_files').get_template("error-404.pyhtml").render(filename=filename,config=config)
	elif status == 403:
		try:
			start_response("403 Permission denied", [('Content-type','text/html')])
		except: # This hapends if the headers were already set by something else
			pass
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(__file__))+'/temporary_files').get_template("error-403.pyhtml").render(filename=filename,config=config)
	else:
		try:
			start_response("500 Internal Server Error", [('Content-type','text/html')])
		except: # This hapends if the headers were already set by something else
			pass
		return "The server attempted to send an error that I've never heard of before. The error code in question was " + str(status)
#**
#* Returns a value that is then sent to the connecting client
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			list environ (environment), function start_response (used to sent headers to the client)
#* @returns			A string equal to what is sent to the client by the wsgiref server.
def serve(environ, start_response):
	new_environ = environ
	for module in moduleObjects:
		try:
			returnvalue, new_environ = module.onRequest(start_response=start_response,environ=new_environ,log=log,logfile=logfile,root=root,serverError=serverError,config=config,file=__file__,getfield=getfield)
			if returnvalue:
				return returnvalue
		except:
			log(traceback.format_exc())
	try:
		start_response("500 Internal Server Error", [('Content-type','text/text')])
	except:
		pass
	return "No module was loaded to handle this case. The server owner has fucked some shit up really bad. Go yell at him. " + config.get('general','email')
#**
#* Gets the entry for a field from a POST or GET form request, probably
#* <p>
#* I'm not going to lie, I have no idea how or why this works
#* @author			No idea <nobody@>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			list f
#* @returns			A string equal to the value of the field specified (f)
def getfield(f):
	if isinstance(f, list):
		return [getfield(x) for x in f]
	else:
		return f.value

if __name__ == '__main__':
	#**
	#* Makes the directories for temporary files and modules, if they don't exist.
	if not os.path.isdir(os.path.dirname(os.path.realpath(__file__))+'/temporary_files'):
		try:
			os.makedirs(os.path.dirname(os.path.realpath(__file__))+'/temporary_files')
		except:
			log("Fatal error: Failed to create temporary_files directory")
			sys.exit(1)
	if not os.path.isdir(os.path.dirname(os.path.realpath(__file__))+'/modules'):
		try:
			os.makedirs(os.path.dirname(os.path.realpath(__file__))+'/modules')
		except:
			log("Fatal error: Failed to create modules directory")
			sys.exit(1)
	from mako.lookup import TemplateLookup
	from mako import exceptions
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	mimetypes.init()
	#**
	#* Reads the configuration file.
	config = ConfigParser.SafeConfigParser()
#	configfile = os.path.dirname(os.path.realpath(__file__)) + "/config.conf"
	logfile = False
	#**
	#* Gets called when the program recieves a 2, 3, 6 or 15 signal from the system
	#* <p>
	#* Attempts to log that the program is exiting, then delete the PID file.
	#* @author			Niles Rogoff <nilesrogoff@gmail.com>
	#* @version			devel/unreleased
	#* @since			2014-01-29
	#* @params			int signum, unknown stack
	#* @returns			True
	def signaled(sihipsterm, stack):
		log("Fatal info: Caught signal " + str(sihipsterm) + ", exiting.")
		try:
			os.remove(pidfile)
		except OSError:
			log("Fatal error: Failed to delete pid file. It might have vanished while we were running, or I didn't have permission to create it in the first place")
			sys.exit(1)
		sys.exit(0)
	#**
	#* Registers signal handlers for the singals 2, 3, 6 and 15
	#* @see				mako-server.server.signaled, signal
	for i in [2,3,6,15]:
		try:
			#sihipsterm = getattr(signal,i)
			signal.signal(i,signaled)
		except RuntimeError,m:
			pass
	#**
	#* I have NO IDEA why, but if you don't start python with -O, it throws NoneType and "write() argument must be string" exceptions, then just closes the connection. 
	#* -O runs optimizations, by the way
	if __debug__:	
		log("Nonfatal warning: Restarting with -O")
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
	#**
	#* Makes a random pid file.
	pidfile = subprocess.check_output(["/usr/bin/env","mktemp","/tmp/mako.XXXXXX"])[0:-1]
	#**
	#* Sets some defaults, before parsing arguments
	nextarg=""
	killkillKILL = True
	configfile=os.path.dirname(os.path.realpath(__file__)) + "/config.conf"
	#**
	#* Parses each argument. Daemonization support is planned, but not implemented.
	for argument in sys.argv[1:]:
		if argument == "-h" or argument.lower() == "--help":
			log("Usage: "+sys.argv[0]+" [-h|--help] [<--pidfile|-P> <pidfile>] [<--config-file|-c> <config.conf>] [--suppress-urge-to-kill]")
			sys.exit(0)
		if nextarg == "pidfile":
			#**
			#* Removes the old, randomly created PID file and uses the last one passed in an argument.
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
			continue
		log("Nonfatal warning. Argument: " +argument + " is not recoginized, ignoring.")
	#**
	#* Attempts to read the config file.
	try:
		config.readfp(open(configfile))
	except:
		log("Fatal error: Config file read failure")
		sys.exit(1)
	#**
	#* Attempts to kill all other mako servers, unless the "--suppress-urge-to-kill" argument was passed.
	if killkillKILL:
		for otherpidfile in glob.glob("/tmp/mako.*"):
			if otherpidfile == pidfile:
				continue
			try:
				otherpidfileobject = open(otherpidfile,'r')
			except IOError:
				#**
				#* We don't have permission to open the file
				continue
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
			try:
				os.remove(otherpidfile)
			except IOError:
				#**
				#* We don't have permission to delete the file
				pass
	#**
	#* Attempts to write the process ID to the pid file
	try:
		pidfileobject = open(pidfile,'w')
		pidfileobject.write(str(os.getpid()))
		pidfileobject.close()
	except:
		log("Nonfatal warning: could not write to PID file " + pidfile)
	#**
	#* Reads some global variables from the config file.
	root = config.get("server","root")
	try:
		port = int(config.get("server","port"))
	except ValueError:
		log("Fatal error: The port in config.conf must be an integer")
		sys.exit(1)
	logfile = config.get("server","logfile")
	#**
	#* Here, we actually start the server
	import wsgiref.simple_server
	server = wsgiref.simple_server.make_server('', port, serve)
	#**
	#* Imports every module in the config file.
	modules = config.get("server","modules").split(config.get("general","listDelimiter"))
	sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/modules')
	try:
		moduleObjects = map(__import__, modules)
	except:
		log("Fatal error: One or more modules failed to import. Please check your config file, and each module file")
		sys.exit(1)
	for module in moduleObjects:
		module.onLoad(log=log,logfile=logfile,root=root,serverError=serverError,config=config,file=__file__,getfield=getfield)
	log("Info: Server listening on port " + str(port))
	server.serve_forever()


