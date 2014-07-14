import sys,os,re,configparser,traceback
if __name__ == '__main__':
	print("Do not invoke this directly")
	sys.exit(1)
#**
#* Logs a message
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/066
#* @since			2014-01-30
#* @params			function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool true
def onLoad(**kargs):
	kargs['log']("mod_simple_security module loaded")
#**
#* Checks the environment variable PATH_INFO
#* @author			Niles Rogoff <nilesrogoff@gmail.com>
#* @version			devel/066
#* @since			2014-01-30
#* @params			function start_response, dictionary environ, function log, string logfile, string root, function serverError, object config, string file, function getfield
#* @returns			bool false, dictionary environment
def onRequest(**kargs):
	new_environ = kargs['environ'].copy()
	if re.match(".*/\.{2}",new_environ['PATH_INFO']):
		new_environ['PATH_INFO'] = re.sub(".*/\.{2}",'',new_environ['PATH_INFO'])
		kargs['log']("Security match found! Rewriting")
		extravar, new_environ = onRequest(root=kargs['root'],start_response=kargs['start_response'],environ=new_environ,log=kargs['log'],logfile=kargs['logfile'],serverError=kargs['serverError'],config=kargs['config'],file=kargs['file'],getfield=kargs['getfield'])
		kargs['log']("New PATH_INFO: " + new_environ['PATH_INFO'])
	return False, new_environ

