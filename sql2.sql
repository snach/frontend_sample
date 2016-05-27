DROP DATABASE IF EXISTS forum;
CREATE DATABASE forum;
USE forum;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id          INT AUTO_INCREMENT  NOT NULL,
  email       CHAR(50) UNIQUE     NOT NULL,
  username    CHAR(50),
  name        CHAR(50),
  about       TEXT,
  isAnonymous BOOL DEFAULT FALSE  NOT NULL,
  PRIMARY KEY (id),
  KEY name_email (name, email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS followers;
CREATE TABLE followers (
  follower CHAR(50) NOT NULL,
  followee CHAR(50) NOT NULL,
  PRIMARY KEY (follower, followee),
  KEY f_f (followee, follower)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS forums;
CREATE TABLE forums (
  id         INT AUTO_INCREMENT NOT NULL,
  name       CHAR(50)       NOT NULL UNIQUE,
  short_name CHAR(50)       NOT NULL UNIQUE,
  user       CHAR(50)       NOT NULL,
  PRIMARY KEY (id),
  KEY (short_name, user, id, name),
  CONSTRAINT `Forum_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS threads;
CREATE TABLE threads (
  id        INT AUTO_INCREMENT NOT NULL,
  title     CHAR(50)       NOT NULL,
  slug      CHAR(50)       NOT NULL,
  forum     CHAR(50)       NOT NULL,
  user      CHAR(50)       NOT NULL,
  posts     INT DEFAULT 0      NOT NULL,
  likes     INT DEFAULT 0      NOT NULL,
  dislikes  INT DEFAULT 0      NOT NULL,
  points    INT DEFAULT 0      NOT NULL,
  isDeleted BOOL DEFAULT FALSE NOT NULL,
  isClosed  BOOL DEFAULT FALSE NOT NULL,
  date      DATETIME           NOT NULL,
  message   TEXT               NOT NULL,
  PRIMARY KEY (id),
  KEY forum_date (forum, date),
  KEY user_date (user, date),
  CONSTRAINT `Thread_ibfk_1` FOREIGN KEY (`forum`) REFERENCES `forums` (`short_name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Thread_ibfk_2` FOREIGN KEY (`user`) REFERENCES `users` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
  id            INT AUTO_INCREMENT NOT NULL,
  message       TEXT               NOT NULL,
  forum         CHAR(50)           NOT NULL,
  user          CHAR(50)           NOT NULL,
  thread        INT                NOT NULL,
  likes         INT DEFAULT 0      NOT NULL,
  dislikes      INT DEFAULT 0      NOT NULL,
  parent        INT DEFAULT NULL,
  points        INT DEFAULT 0      NOT NULL,
  isDeleted     BOOL DEFAULT FALSE NOT NULL,
  isSpam        BOOL DEFAULT FALSE NOT NULL,
  isEdited      BOOL DEFAULT FALSE NOT NULL,
  isApproved    BOOL DEFAULT FALSE NOT NULL,
  isHighlighted BOOL DEFAULT FALSE NOT NULL,
  date          DATETIME           NOT NULL,
  path          VARCHAR(255),
  isRoot        BOOL DEFAULT TRUE  NOT NULL,
  PRIMARY KEY (id),
  KEY user_date (user, date),
  KEY user_forum (user, forum),
  KEY forum_date (forum, date),
  KEY thread_date (thread, date),
  CONSTRAINT `Post_ibfk_1` FOREIGN KEY (`forum`) REFERENCES `forums` (`short_name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Post_ibfk_2` FOREIGN KEY (`thread`) REFERENCES `threads` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Post_ibfk_3` FOREIGN KEY (`user`) REFERENCES `users` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS subscriptions;
CREATE TABLE subscriptions (
  user   CHAR(50) NOT NULL,
  thread INT          NOT NULL,
  PRIMARY KEY (user, thread)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
