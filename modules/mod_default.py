import sys,cgi,re,os,mimetypes
from mako.lookup import TemplateLookup
from mako import exceptions
if __name__ == '__main__':
	print "Do not invoke this directly"#you dumb shit
	sys.exit(1)
def onLoad(**kargs):
	print "Default case module loaded"
	global listdirectories, servestaticfiles
	listdirectories = bool(int(kargs["config"].get("server","listdirectories")))
	servestaticfiles = bool(int(kargs["config"].get("server","servestaticfiles")))
def onRequest(**kargs):
	fieldstorage = cgi.FieldStorage(
			fp = kargs["environ"]['wsgi.input'],
			#environ = environ,
			keep_blank_values = True
	)
	d = dict([(k, getfield(fieldstorage[k])) for k in fieldstorage])

	uri = kargs["environ"].get('PATH_INFO', '/')
	if not uri:
		uri = '/index.pyhtml'
	else:
		uri = re.sub(r'^/$', '/index.pyhtml', uri)
	u = re.sub(r'^\/+', '', uri)
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
					# Note that all other templates get filename=uri and this gets filename=filename. This is because this file needs to check the date modified and other elements of the file in question, which requires an absolute path. It could be added as filename = config.get("server","root") + uri, but I already have this set up.
					kargs["start_response"]("200 OK", [('Content-type','text/html')])
					return rendered
				except OSError:
					return kargs["serverError"](kargs["start_response"],403,uri)
				except:
					return kargs["serverError"](kargs["start_response"],500)
			else:
				return kargs["serverError"](kargs["start_response"],403,uri)
	if re.match(r'.*\.pyhtml$', uri):
		try:
			rendered = TemplateLookup(directories=[kargs["root"]], filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template(uri).render(d=d,uri=uri)
			kargs["start_response"]("200 OK", [('Content-type','text/html')])
			return rendered
		except exceptions.TopLevelLookupException, exceptions.TemplateLookupException:
			return kargs["serverError"](kargs["start_response"],404,uri)
		except:
			print 2
			return kargs["serverError"](kargs["start_response"],500)
	else:
		try:
			if not os.path.exists(filename):
				return kargs["serverError"](kargs["start_response"],404,uri)
			if servestaticfiles == True:
				mime = mimetypes.guess_type(filename)[0]
				if not mime:
					mime = "text/text"
				try:
					rendered = file(filename).read()
				except:
					return kargs["serverError"](kargs["start_response"],403,uri)
				kargs["start_response"]("200 OK", [('Content-type',mime)])
				if not rendered:
					return "File is empty"
				else:
					return rendered
			else:
				rendered = TemplateLookup(directories=os.path.dirname(os.path.realpath(kargs["file"])),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template("no.static.pyhtml").render(filename=uri,config=config)
				kargs["start_response"]("200 OK", [('Content-type','text/html')])
				return rendered
		except:
			return kargs["serverError"](kargs["start_response"],500,uri)