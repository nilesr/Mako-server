# Mako-server
This is a multithreaded webserver that can serve files using the python-based [mako template engine](http://www.makotemplates.org/)

For speed comparisons, see SPEED-TESTS.md

## Portability

This is 100% portable, and can be run from anywhere on the system. I recommend /etc/mako-server, but really it doesn't matter

I recommend starting it like ./server.py or /etc/mako-server/server.py, but you can also start it with python server.py

There is currently an installer for Mac OS X, but all it does is make the "mako-server-start" "mako-server-stop" and "mako-server-restart", then install launchd job to daemonize the server, you still have to put these files somewhere on your system, like /etc or /Library

## Planned features

* daemonization
* an installer for various distros of linux

## Installation

This does not need to be installed. See the "Portability" clause of the "Mako-server" heading.

The default config file is called config.conf. A sample.conf is provided

## Command line options

-h/--help: prints help

--suppress-urge-to-kill: will not kill other mako web server processes

-c/--config-file: specifies an alternative configuration file

-P/--pidfile: specifies an alternative process identifier file

## The module system

Mako-server is split into several modules. It is easy to write your own module, but the ones that come pre-installed should more than suit your needs. They are organized in the config file in order of execution. Each module has an opportunity to modify environment variables, and to load a page to send to a client.

It is incredibly easy to make your own module. You could rewrite mod_default to use nemo instead of mako by adding "from nemo.parser import nemo" and pasting "preprocessor=nemo," into it six or seven times. Or you could make a module that logs all queries to an IRC channel. Or you could turn this into a HTTP proxy. Really the possibilities are endless.

The built in modules are below

### mod_logging

All this does is log some information about each request. If mod_rewrite or something similar is loaded before it, it will log the new path.

Mod_logging is highly configurable. An example configuration is
<pre>
order: IP address:,REMOTE_ADDR,REQUEST_METHOD,File requested:,PATH_INFO,User-agent string:,HTTP_USER_AGENT
</pre>
A request with this configuration would look like this:
<pre>./server.py 29/01/2014 21:21:32	IP address: 108.48.xx.xxx GET File requested: /favicon.ico User-agent string: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.46 Safari/537.36</pre>

This uses the main server's built in log function, which uses a log file specified in the general section of the configuration file.

### mod_rewrite

This takes some getting used to, and definitely isn't required, but can be incredibly powerful.

Note that this logs each rewrite, in order, if log is set to 1 

Some example configuration, then what it does.
<pre>
log: 1
sets: set-1,set-2
set-1-condition-1: bypass
set-1-change: index,new
set-2-condition-1: REMOTE_ADDR,^(?!127\.0\.).+
set-2-condition-2: PATH_INFO,.*admin\.pyhtml*
set-2-change:admin\.pyhtml,index.pyhtml
</pre>

And as promised, how it works. Each set is loaded in order, by name.
First we load set-1. We look at the first condition, which is the string "bypass". Because we are bypassing condition checking, we apply the set set-1 to every incoming request. The two parts of set-1-change are the two halves of a regular expression. This regular expression will change every instance of "index" to "new" in the URL. 

Now we load set-2. For each condition (there are two conditions) we check them in order. First, we check to see if the IP address that is connecting does not start with "127.0.". If it starts with "127.0." we do not apply this rule. Then we go to set-2-condition-2. We check to see that "admin.pyhtml" is in the client's request string. If it is not, we do not apply this rule. Finally, if the IP does not start with "127.0." AND the file they are requesting contains "admin.pyhtml", then we apply the regular expression in set-2-change. That expression changes admin.pyhtml to index.pyhtml.

I do not recommend this as a legitimate security function.

You can specify as many conditions as you want in a set, but only one "change".

If you need to specify a comma in a regular expression, do not attempt to escape it with a backslash. Change the listdelimiter option under the general section of the configuration file.

### mod_simple_vhost

This is somewhat easier than mod_rewrite, but the configuration is based on a similar principle (without looping this time)

Here's an example configuration
<pre>
sets: mysite1,mysite2,local
mysite1-host: site.one.com*
mysite1-root: /var/www/site_one_htdocs/
mysite2-host: site.two.com*
mysite2-root: /var/www/site_two_htdocs/
local-host: *localhost*
local-root: /var/www/admin/
</pre>

So first the sets option. This is a list of every vhost configuration you load

Each -host option is a regular expression to be checked against the Host header sent by the client

Each -root option is a file path to the document root for that vhost configuration

First, we load mysite1. If the regular expression in mysite1-host applies, we employ mod_default to serve that file using the document root in the configuration at mysite1-root, which is /var/www/site_one_htdocs/

The same thing happens for mysite2

If we are connecting and giving the Host header something that has localhost in it, it will serve out queries from /var/www/admin/

If a vhost regular expression applies, this module will always stop the execution chain. If nothing applies, it returns, and server.py continues down the list of modules.

### mod_default

This is pretty easy. It serves a file out of the root that it is passed, either from the global configuration or a plugin that calls it, such as mod_simple_vhost

This module will always return something and stop the chain of execution

There are only two configuration options
<pre>
servestaticfiles: 1
listdirectories: 1
</pre>

First, if the request is a directory, it will check to see if there is an index.pyhtml file in it

If there is not, and listdirectores is set to 1, it will return 404 error with a list of all files in the directory

The file list is incredibly similar to the directory list for lighttpd

The directory list is in the file list.pyhtml

I expect you to edit this file for your purposes, but it will work just fine with no edits

If listdirectories is set to 0, it returns a 403 permission denied error, and sends the file error-403.pyhtml

Again, I expect you to change this file to suit your needs, but will work just fine with no changes

If index.pyhtml does exist in that directory, it renders it

If the file is not a directory, it checks to see if the file requested ends with .pyhtml, and if it does, it attempts to render and send the file

If an error occurs rendering that file, it prints a stack trace to the console and log file, then sends a 500 error page to the client, using the file error-500.pyhtml. Again, you probably don't need to edit this file, but it can't hurt to open it up and see what's inside before putting it in your web server

If the file does not exist, it returns a 404 error using the file error-404.pyhtml. You can guess what I have to say about that

If the file requested does not end in .pyhtml, and it exists, it checks the config file option servestaticfiles

If it is set to 1, it guesses the mimetype from the extension and sends the static file

On the other hand, if it is set to 0, it sends a 200 response code and renders the file no.static.pyhtml, which contains a warning about how the server owner has disallowed static files, then redirects the user to [this video](https://www.youtube.com/watch?v=gvdf5n-zI14)

# If there's anything you should change before using this web server in any non-testing situation, it's that

If you serve other things such as php files out of this directory, remember that they will be sent with the internal code unparsed, so you might want to disallow sending static files or write a rule using mod_rewrite

### mod_500_nothing_executed

The simplest of all the modules.

Returns a 500 error code and renders the file error-500-no-module.pyhtml

If you include mod_default before this, this will never get called

It's really only for if you are using mod_simple_vhost but you don't want mod_default to serve any files, so you just take it out of the module order. Then, if no host applies in mod_simple_vhost, it will ideally eventually execute this module

### mod_path_to_cgi

This provides something that should probably be possible with mod_rewrite, but isn't.

This allows you to change paths to files, but keep the path saved somewhere

Here's an example configuration
<pre>
log: 1
sets: api-key
api-key: ^(/api/),/d.pyhtml
</pre>

Here's <pre>d.pyhtml</pre>
<pre>
% if d:
${str(d)}
% else:
<p>No cgi variables :(</p>
% endif
</pre>

An example request, <pre>/api/68b329da9893e34099c7d8ad5cb9c940/</pre> would be redirected to <pre>/d.pyhtml</pre>

d.pyhtml would render <pre>{'api-key': '68b329da9893e34099c7d8ad5cb9c940/'}</pre>

You could extend this to look something like this

<pre>/api/message/unread</pre>

to <pre>/d.pyhtml</pre> which would render

<pre>{'api-key': 'message/unread'}</pre>

If you renamed api-key to something else in the config file, this would make more sense

It is evaluated just like all the other cgi variables, including GET and POST requests.

This module does not return a response

### mod_simple_security

Pretty simple security.

Prevents a client from sending a string like "/directory/../../../.." or ".." and breaking out of the document root.

Note that if you have a web page that gets files from the filesystem, this will offer no protection whatsoever

This module does not return a response.

Introduced version 066

### What if no module returns anything?

The server will send a 500 response, mime type text/text and the string "No module was loaded to handle this case. The server owner has fucked some shit up really bad. Go yell at him. ", plus the email specified in the config file

