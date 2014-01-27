#!/usr/bin/env python -O
import cgi, re, os, posixpath, mimetypes, sys, ConfigParser, mimetypes, subprocess, glob, signal, time
from mako.lookup import TemplateLookup
from mako import exceptions
mimetypes.init()
config = ConfigParser.SafeConfigParser()
configfile = os.path.dirname(os.path.realpath(__file__)) + "/config.conf"
logfileobject = False
def log(missive):
	if logfileobject:
		logfileobject.write(sys.argv[0] + " " + time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + missive + "\r\n")
	print sys.argv[0] + " " + time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + missive
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
				log("Either the other process has ended, or I don't have permission to kill it.")
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
logfileobject = open(logfile,'w')
class error404:
	def __init__(self):
		pass
	def __str__(self):
		pass
lookup = TemplateLookup(directories=[root], filesystem_checks=True, module_directory='./modules')
def serverError(start_response,status,filename=""):
	if status == 500:
		start_response("500 Internal Server Error", [('Content-type','text/html')])
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory='./modules').get_template("error-500.pyhtml").render(filename=filename,config=config)
	elif status == 404:
		start_response("404 Not found", [('Content-type','text/html')])
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory='./modules').get_template("error-404.pyhtml").render(filename=filename,config=config)
	elif status == 403:
		start_response("403 Permission denied", [('Content-type','text/html')])
		return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory='./modules').get_template("error-403.pyhtml").render(filename=filename,config=config)
	else:
		log("You dun fucked up")
		sys.exit(1)
def serve(environ, start_response):
	# serves requests using the WSGI callable interface.
	fieldstorage = cgi.FieldStorage(
			fp = environ['wsgi.input'],
			environ = environ,
			keep_blank_values = True
	)
	d = dict([(k, getfield(fieldstorage[k])) for k in fieldstorage])

	uri = environ.get('PATH_INFO', '/')
	if not uri:
		uri = '/index.pyhtml'
	else:
		uri = re.sub(r'^/$', '/index.pyhtml', uri)
	u = re.sub(r'^\/+', '', uri)
	filename = root + u
	if os.path.isdir(filename):
		if not filename[-1] == '/':
			filename = filename + "/"
		filename = filename + "index.pyhtml"
		if not uri[-1] == '/':
			uri = uri + "/"
		uri = uri + "index.pyhtml"
		if not os.path.exists(filename):
			if listdirectories:
				try:
					rendered = TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory='./modules').get_template("list.pyhtml").render(filename=filename,config=config)
					# Note that all other templates get filename=uri and this gets filename=filename. This is because this file needs to check the date modified and other elements of the file in question, which requires an absolute path. It could be added as filename = config.get("server","root") + uri, but I already have this set up.
					start_response("200 OK", [('Content-type','text/html')])
					return rendered
				except OSError:
					return serverError(start_response,403,uri)
				except:
					return serverError(start_response,500)
			else:
				return serverError(start_response,403,uri)
	if re.match(r'.*\.pyhtml$', uri):
		try:
			template = lookup.get_template(uri)
			rendered = [template.render(**d)]
			start_response("200 OK", [('Content-type','text/html')])
			return rendered
		except exceptions.TopLevelLookupException, exceptions.TemplateLookupException:
			return serverError(start_response,404,uri)
		except:
			return serverError(start_response,500)
	else:
		try:
			if not os.path.exists(filename):
				raise error404()
			if servestaticfiles == True:
				mime = mimetypes.guess_type(filename)[0]
				if not mime:
					mime = "text/text"
				start_response("200 OK", [('Content-type',mime)])
				return [file(filename).read()]			
			else:
				rendered = TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory='./modules').get_template("no.static.pyhtml").render(filename=uri,config=config)
				start_response("200 OK", [('Content-type','text/html')])
				return rendered
		except error404:
			return serverError(start_response,404,uri)
		except:
			return serverError(start_response,500,uri)
def getfield(f):
	"""convert values from cgi.Field objects to plain values."""
	if isinstance(f, list):
		return [getfield(x) for x in f]
	else:
		return f.value

if __name__ == '__main__':
	import wsgiref.simple_server
	server = wsgiref.simple_server.make_server('', port, serve)
	log("Server listening on port %d" % port)
	server.serve_forever()


