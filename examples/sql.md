To make the sql example *really* work, you need to run something like this in your "test" database
It adds one user, username "admin", password "password"

<pre>
CREATE USER 'readonly'@'localhost';
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Username` char(11) CHARACTER SET utf8 DEFAULT NULL,
  `Password` char(32) CHARACTER SET utf8 DEFAULT NULL,
  `Messages` int(3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
LOCK TABLES `users` WRITE;
INSERT INTO `users` (`id`, `Username`, `Password`, `Messages`)
VALUES
	(1,'admin','5f4dcc3b5aa765d61d8327deb882cf99',3);
UNLOCK TABLES;
</pre>