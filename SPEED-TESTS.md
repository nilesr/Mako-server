### If you just want the tl;dr on this file, this web server is 10.53% slower than lighttpd running with php-cgi and I didn't test apache

### Seriously, it's still incredibly fast. Like 0.05ish seconds vs 0.045ish seconds fast.

To run a speed check, I used these scripts on my computer. This would use the loopback interface, so there would be almost no latency

<pre>
mkfifo temp
while true; do time curl localhost:4000/color.pyhtml; done &> temp & cat temp | grep real | tee -a full-optimization.log & sleep 30;rm temp; kill $(jobs -p)
while true; do time curl localhost:80/color.php; done &> temp & cat temp | grep real | tee -a lighttpd-php-cgi.log & sleep 30;rm temp; kill $(jobs -p)
</pre>

There was a dramatic difference, so on a remote host (roughly 60 mb/s down, 80mb/s up), I used these

<pre>
mkfifi temp
mkfifo temp; while true; do time curl niles.mooo.com:4000/color.pyhtml; done &> temp & cat temp | grep real | tee -a full-optimization-remote.log & sleep 30; kill $(jobs -p)
mkfifo temp; while true; do time curl niles.mooo.com:80/color.php; done &> temp & cat temp | grep real | tee -a lighttpd-php-cgi-remote.log & sleep 30; kill $(jobs -p)
</pre>

color.pyhtml is in the examples folder

color.php is as follows:

<pre>
&lt;?php
function newColor() {
	return str_pad( dechex( mt_rand( 0, 255 ) ), 2, '0', STR_PAD_LEFT);
}
function fullColor() {
	if (isset($_GET['color'])) {
		return $_GET['color'];
	} else {
		return "#" . newColor() . newColor() . newColor();
	}
}
?&gt;
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
&lt;title&gt;Hazel Alder&lt;/title&gt;
&lt;link rel="stylesheet" href="/style.css"&gt;
&lt;/head&gt;
&lt;body style="background-color:&lt;?php echo fullColor() ?&gt;"&gt;
&lt;h2&gt;Hazel Alder&lt;/h2&gt;
&lt;div id="content"&gt;
&lt;h1 style="color:&lt;?php echo fullColor() ?&gt;}"&gt;This is running on the mako engine. I'm sure I'll have a use for it sometime&lt;/h1&gt;
&lt;form name="input" action="" method="post"&gt;
New hex color: &lt;input type="text" name="color"&gt;&lt;br&gt;
&lt;input type="submit" value="Submit"&gt;
&lt;/form&gt;
&lt;hr /&gt;
&lt;a href="/ben.pyhtml"&gt;Ben is...&lt;/a&gt;
&lt;/div&gt;
&lt;div id="foot"&gt;Niles Rogoff 2013&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
</pre>

The results are below

<pre>
$ for x in *.log; do echo -n $x" - ";cat $x|sed -n '$='; done
lighttpd-php-cgi.log - 3438
full-optimization.log - 1437
lighttpd-php-cgi-remote.log - 606
full-optimization-remote.log - 517
</pre>

And the versions

<pre>
$ lighttpd -v
lighttpd/1.4.33 (ssl) - a light and fast webserver
Build-Date: Jan 26 2014 11:59:01
$ php-cgi -v
PHP 5.5.8 (cgi-fcgi) (built: Jan 26 2014 12:23:27)
Copyright (c) 1997-2013 The PHP Group
Zend Engine v2.5.0, Copyright (c) 1998-2013 Zend Technologies
$ python --version
Python 2.7.6
</pre>

As you can see, with the loopback interface, lighttpd with php-cgi is far superior. 

When actual networking has to be implemented, the difference in render times becomes negligible, a difference of 89 requests over 30 seconds.

I then ran this

<pre>
$ for x in *.log; do echo -n $x" - "; totalRequests=$(cat $x | sed -n '$='); echo $(($totalRequests/30)); done
</pre>

to determine the number of requests per second. It returned

<pre>
full-optimization-remote.log - 17
full-optimization.log - 47
lighttpd-php-cgi-remote.log - 19
lighttpd-php-cgi.log - 114
</pre>

As you can see, on the local host, there is a very dramatic difference, but from a remote host, it's only 10.53% slower.

Plus, who wants to use PHP anyways.