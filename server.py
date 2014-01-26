#!/usr/bin/python
import cgi, re, os, posixpath, mimetypes, sys, ConfigParser, mimetypes, subprocess
from mako.lookup import TemplateLookup
from mako import exceptions
mimetypes.init()
config = ConfigParser.SafeConfigParser()
config.read("config.conf")

if __debug__:
	print "Restarting with -O"
	listofarguments = ["/usr/bin/env", "python", "-O"]
	for argument in sys.argv:
		if argument == __file__:
			continue
		listofarguments.append(argument)
	listofarguments.append(__file__)
	print "Calling " + " ".join(listofarguments)
	sys.exit(subprocess.call(listofarguments))
	
	# Alright, I have NO IDEA why, but if you don't start python with -O, it throws NoneType and "write() argument must be string" exceptions, then just closes the connection. 

root = config.get("server","root")
try:
	port = int(config.get("server","port"))
except ValueError:
	print "The port in config.conf must be an integer"
	sys.exit(1)
try:
	servestaticfiles = bool(int(config.get("server","servestaticfiles")))
except:
	print "The servestaticfiles value in config.conf should be a 1 or a 0"
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
	else:
		print "You dun fucked up"
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
	if re.match(r'.*\.pyhtml$', uri):
		try:
			template = lookup.get_template(uri)
			start_response("200 OK", [('Content-type','text/html')])
			return [template.render(**d)]
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
				start_response("200 OK", [('Content-type','text/html')])
				return TemplateLookup(directories=os.path.dirname(os.path.realpath(__file__)),filesystem_checks=True, module_directory='./modules').get_template("no.static.pyhtml").render(filename=filename,config=config)
		except error404:
			return serverError(start_response,404,uri)
		except:
			return serverError(start_response,500)
def getfield(f):
	"""convert values from cgi.Field objects to plain values."""
	if isinstance(f, list):
		return [getfield(x) for x in f]
	else:
		return f.value

if __name__ == '__main__':
	import wsgiref.simple_server
	server = wsgiref.simple_server.make_server('', port, serve)
	print "Server listening on port %d" % port
	server.serve_forever()


