import sys,cgi,re,os,mimetypes
from mako.lookup import TemplateLookup
from mako import exceptions
if __name__ == '__main__':
	print "Do not invoke this directly"#you dumb shit
	sys.exit(1)
def onLoad(**kargs):
	global listdirectories, servestaticfiles
	listdirectories = bool(int(kargs["config"].get("mod_default","listdirectories")))
	servestaticfiles = bool(int(kargs["config"].get("mod_default","servestaticfiles")))
	kargs['log']("Default case module loaded")
def onRequest(**kargs):
	fieldstorage = cgi.FieldStorage(
			fp = kargs["environ"]['wsgi.input'],
			environ = kargs['environ'],
			keep_blank_values = True
	)
	d = dict([(k, kargs["getfield"](fieldstorage[k])) for k in fieldstorage])
	uri = kargs["environ"].get('PATH_INFO', '/')
	if not uri:
		uri = '/'
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