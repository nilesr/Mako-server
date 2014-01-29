import sys,cgi,re,os,mimetypes
from mako.lookup import TemplateLookup
from mako import exceptions
if __name__ == '__main__':
	print "Do not invoke this directly"#you dumb shit
	sys.exit(1)
#**
#* Loads the relevant configuration options, and logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2013-01-29
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			True
def onLoad(**kargs):
	global listdirectories, servestaticfiles
	listdirectories = bool(int(kargs["config"].get("mod_default","listdirectories")))
	servestaticfiles = bool(int(kargs["config"].get("mod_default","servestaticfiles")))
	kargs['log']("Default case module loaded")
#**
#* Attempts to serve a rendered mako file, or a static file, or a directory listing, or a 404 error, or a 403, or a 500 error
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2013-01-29
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			A rendered mako file, or a static file, or a directory listing, or a 404 error, or a 403, or a 500 error
def onRequest(**kargs):
	#**
	#* I have no idea what this does
	fieldstorage = cgi.FieldStorage(
			fp = kargs["environ"]['wsgi.input'],
			environ = kargs['environ'],
			keep_blank_values = True
	)
	#**
	#* This sets d to the GET/POST headers
	d = dict([(k, kargs["getfield"](fieldstorage[k])) for k in fieldstorage])
	#**
	#* This sets URI to something like "/" or "/index.pyhtml" or "/directory/specific_file.pyhtml"
	uri = kargs["environ"].get('PATH_INFO', '/')
	if not uri:
		uri = '/'
	u = re.sub(r'^\/+', '', uri)
	#**
	#* This sets filename to the local file where we are serving the file from
	filename = kargs["root"] + u
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
					rendered = TemplateLookup(directories=os.path.dirname(os.path.realpath(kargs["file"])),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template("list.pyhtml").render(filename=filename,config=kargs["config"],d=d,uri=uri)
					kargs["start_response"]("200 OK", [('Content-type','text/html')])
					return rendered, kargs['environ']
				except OSError:
					return kargs["serverError"](kargs["start_response"],403,uri), kargs['environ']
				except:
					return kargs["serverError"](kargs["start_response"],500), kargs['environ']
			else:
				return kargs["serverError"](kargs["start_response"],403,uri), kargs['environ']
	if re.match(r'.*\.pyhtml$', uri):
		try:
			rendered = TemplateLookup(directories=[kargs["root"]], filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template(uri).render(d=d,uri=uri)
			kargs["start_response"]("200 OK", [('Content-type','text/html')])
			return rendered, kargs['environ']
		except exceptions.TopLevelLookupException, exceptions.TemplateLookupException:
			return kargs["serverError"](kargs["start_response"],404,uri), kargs['environ']
		except:
			return kargs["serverError"](kargs["start_response"],500), kargs['environ']
	else:
		try:
			if not os.path.exists(filename):
				return kargs["serverError"](kargs["start_response"],404,uri), kargs['environ']
			if servestaticfiles == True:
				mime = mimetypes.guess_type(filename)[0]
				if not mime:
					mime = "text/text"
				try:
					rendered = file(filename).read()
				except:
					return kargs["serverError"](kargs["start_response"],403,uri), kargs['environ']
				kargs["start_response"]("200 OK", [('Content-type',mime)])
				if not rendered:
					return "File is empty", kargs['environ']
				else:
					return rendered, kargs['environ']
			else:
				rendered = TemplateLookup(directories=os.path.dirname(os.path.realpath(kargs["file"])),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template("no.static.pyhtml").render(filename=uri,config=config)
				kargs["start_response"]("200 OK", [('Content-type','text/html')])
				return rendered, kargs['environ']
		except:
			return kargs["serverError"](kargs["start_response"],500,uri), kargs['environ']