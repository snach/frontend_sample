DROP DATABASE IF EXISTS `forum`;
CREATE DATABASE  IF NOT EXISTS `forum` ;
USE `forum`;

SET  FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `Forum`;

CREATE TABLE `Forum` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `short_name` varchar(255) NOT NULL,
  `user` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `short_name` (`short_name`),
  KEY `user` (`user`),
  CONSTRAINT `Forum_ibfk_1` FOREIGN KEY (`user`) REFERENCES `User` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=cp1251;


DROP TABLE IF EXISTS `Post`;

CREATE TABLE `Post` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `thread` int(11) NOT NULL,
  `message` text NOT NULL,
  `user` varchar(255) NOT NULL,
  `forum` varchar(255) NOT NULL,
  `parent` int(11) DEFAULT NULL,
  `isApproved` tinyint(1) NOT NULL DEFAULT '0',
  `isHighlighted` tinyint(1) NOT NULL DEFAULT '0',
  `isEdited` tinyint(1) NOT NULL DEFAULT '0',
  `isSpam` tinyint(1) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(1) NOT NULL DEFAULT '0',
  `likes` int(11) NOT NULL DEFAULT '0',
  `dislikes` int(11) NOT NULL DEFAULT '0',
  `path` varchar(255) NOT NULL DEFAULT '0',
  `childs_count` int(11) NOT NULL DEFAULT '0',
  `points` int(11) NOT NULL DEFAULT '0',
  `isRoot` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `forum` (`forum`),
  KEY `thread` (`thread`),
  KEY `user` (`user`),
  CONSTRAINT `Post_ibfk_1` FOREIGN KEY (`forum`) REFERENCES `Forum` (`short_name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Post_ibfk_2` FOREIGN KEY (`thread`) REFERENCES `Thread` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Post_ibfk_3` FOREIGN KEY (`user`) REFERENCES `User` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=cp1251;



DROP TABLE IF EXISTS `Thread`;

CREATE TABLE `Thread` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `forum` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `isClosed` tinyint(1) NOT NULL DEFAULT '0',
  `user` varchar(255) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `message` text NOT NULL,
  `slug` varchar(255) NOT NULL,
  `isDeleted` tinyint(1) NOT NULL DEFAULT '0',
  `likes` int(11) NOT NULL DEFAULT '0',
  `dislikes` int(11) NOT NULL DEFAULT '0',
  `posts` int(11) NOT NULL DEFAULT '0',
  `points` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `forum` (`forum`),
  KEY `user` (`user`),
  CONSTRAINT `Thread_ibfk_1` FOREIGN KEY (`forum`) REFERENCES `Forum` (`short_name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Thread_ibfk_2` FOREIGN KEY (`user`) REFERENCES `User` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=cp1251;



DROP TABLE IF EXISTS `Thread_followers`;

CREATE TABLE `Thread_followers` (
  `thread_id` int(11) NOT NULL,
  `follower_email` varchar(50) NOT NULL,
  PRIMARY KEY (`thread_id`,`follower_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



DROP TABLE IF EXISTS `User`;

CREATE TABLE `User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `about` text,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `isAnonymous` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=cp1251;



DROP TABLE IF EXISTS `User_followers`;

CREATE TABLE `User_followers` (
  `User` varchar(50) NOT NULL,
  `Followers` varchar(50) NOT NULL,
  PRIMARY KEY (`User`,`Followers`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

