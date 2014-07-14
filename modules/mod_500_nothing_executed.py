import sys,os
from mako.lookup import TemplateLookup
from mako import exceptions
if __name__ == '__main__':
	print "Do not invoke this directly"
	sys.exit(1)
#**
#* Logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	kargs['log']("Worst case scenario module loaded")
#**
#* Starts a 500 server error response, and sends the client a 500 server error
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/unreleased
#* @since			2014-01-29
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			string the rendered template for the 500 nothing executed file, dictionary environment
def onRequest(**kargs):
	kargs["start_response"]("500 Nothing executed", [('Content-type','text/html')])
	return TemplateLookup(directories=os.path.dirname(os.path.realpath(kargs["file"])),filesystem_checks=True, module_directory=os.path.dirname(os.path.realpath(kargs["file"]))+'/temporary_files').get_template("error-500-no-module.pyhtml").render(config=kargs["config"],uri=kargs['environ']['PATH_INFO']), kargs['environ']
