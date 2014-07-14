import sys,cgi,re,os,mimetypes,traceback
from mako.lookup import TemplateLookup
from mako import exceptions
if __name__ == '__main__':
	print("Do not invoke this directly")#you dumb shit
	sys.exit(1)
#**
#* Loads the relevant configuration options, and logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	global listdirectories, servestaticfiles
	listdirectories = bool(int(kargs["config"].get("mod_default","listdirectories")))
	servestaticfiles = bool(int(kargs["config"].get("mod_default","servestaticfiles")))
	kargs['log']("Default case module loaded")
#**
#* Attempts to serve a rendered mako file, or a static file, or a directory listing, or a 404 error, or a 403, or a 500 error
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			string a rendered mako file or a static file or a directory listing or a 404 error or a 403 or a 500 error, dictionary environment
def onRequest(**kargs):
	#**
	#* I have no idea what this does
	fieldstorage = cgi.FieldStorage(
			fp = kargs["environ"]['wsgi.input'],
			environ = kargs['environ'],
			keep_blank_values = True
	)
	#**
	#* This sets d to the GET/POST headers, probably
	d = dict([(k, kargs["getfield"](fieldstorage[k])) for k in fieldstorage])
	if d:
		kargs['log']("Rendering page with cgi variables: " + str(d))
	#**
	#* This sets URI to something like "/" or "/index.pyhtml" or "/directory/specific_file.pyhtml"
	uri = kargs["environ"].get('PATH_INFO', '/')
	if not uri:
		uri = '/'
	u = re.sub(r'^\/+', '', uri)
	#**
	#* This sets filename to the local file where we are serving the file from
	filename = kargs["root"] + u
	#**
	#* If it's a directory, append /index.pyhtml to it
	#* Then, attempt to serve the file. If it doesn't exist, check the config file to see if we support directory listings. Depending on that value, either render and return a list of files and directories in said directory, or render and return a 403 error
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
					kargs['log'](traceback.format_exc())
					return kargs["serverError"](kargs["start_response"],500), kargs['environ']
			else:
				return kargs["serverError"](kargs["start_response"],403,uri), kargs['environ']
	#**
	#* If the uri ends with .pyhtml, attempt to serve the file using mako
	if re.match(r'.*\.pyhtml$', uri):
		try:
			rendered = TemplateLookup(directories=[kargs["root"]], filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template(uri).render(d=d,uri=uri,environ=kargs["environ"])
			kargs["start_response"]("200 OK", [('Content-type','text/html')])
			return rendered, kargs['environ']
		except exceptions.TopLevelLookupException as xxx_todo_changeme:
			exceptions.TemplateLookupException = xxx_todo_changeme
			return kargs["serverError"](kargs["start_response"],404,uri), kargs['environ']
		except:
			kargs['log'](traceback.format_exc())
			return kargs["serverError"](kargs["start_response"],500,error_string=traceback.format_exc()), kargs['environ']
	#**
	#* Otherwise, check our configuration to see if we will serve static files, and either send the file, send a file is empty warning, or send a message saying we do not serve static files
	else:
		try:
			if not os.path.exists(filename):
				return kargs["serverError"](kargs["start_response"],404,uri), kargs['environ']
			if servestaticfiles == True:
				mime = mimetypes.guess_type(filename)[0]
				if not mime:
					mime = "text/text"
				try:
					#**
					#* This is very slow, because we load the entire file, then pass it up. There is probably a way to speed this up, but until then it's going to take like 0.7 seconds to load a 4 kilobyte file
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
			kargs['log'](traceback.format_exc())
			return kargs["serverError"](kargs["start_response"],500,uri), kargs['environ']
