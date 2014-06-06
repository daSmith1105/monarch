-- MySQL dump 10.9
--
-- Host: localhost    Database: monarch
-- ------------------------------------------------------
-- Server version	4.1.20

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP DATABASE IF EXISTS monarch;
CREATE DATABASE monarch;

USE monarch;

/*GRANT ALL ON monarch.* TO 'monarch' IDENTIFIED BY 'monarch';*/
/*GRANT ALL ON monarch.* TO 'monarch'@'localhost' IDENTIFIED BY 'monarch';*/

--
-- Table structure for table `ACL`
--

DROP TABLE IF EXISTS `ACL`;
CREATE TABLE `ACL` (
  `bUserID` BIGINT UNSIGNED NOT NULL default '0',
  `bRight` SMALLINT UNSIGNED NOT NULL default '0',
	UNIQUE `bUser` (`bUserID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `ACL`
--

/*!40000 ALTER TABLE `ACL` DISABLE KEYS */;
LOCK TABLES `ACL` WRITE;
INSERT INTO `ACL` VALUES (2,31);
UNLOCK TABLES;
/*!40000 ALTER TABLE `ACL` ENABLE KEYS */;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
CREATE TABLE `User` (
  `bID` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
  `sName` VARCHAR(64) NOT NULL default '',
  `sPassword` VARCHAR(16) default NULL,
  `sDescription` VARCHAR(64) NOT NULL default '',
  `bType` TINYINT UNSIGNED NOT NULL default '0',
  PRIMARY KEY  (`bID`),
	UNIQUE `sName` (`sName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `User`
--

/*!40000 ALTER TABLE `User` DISABLE KEYS */;
LOCK TABLES `User` WRITE;
INSERT INTO `User` VALUES (1,'dividia',PASSWORD('saf8734'),'Dividia',0);
INSERT INTO `User` VALUES (2,'rayers',PASSWORD('lynn1012'),'Ryan Ayers',20);
UNLOCK TABLES;
/*!40000 ALTER TABLE `User` ENABLE KEYS */;

--
-- Table structure for table `Session`
--

DROP TABLE IF EXISTS `Session`;
CREATE TABLE `Session` (
  `bUserID` BIGINT UNSIGNED NOT NULL UNIQUE,
  `dLastAccess` DATETIME NOT NULL,
  `sSessID` VARCHAR(255) NOT NULL default '',
  PRIMARY KEY  (`bUserID`),
	UNIQUE `sSessid` (`sSessID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `Rights`
--

DROP TABLE IF EXISTS `Rights`;
CREATE TABLE `Rights` (
  `bID` SMALLINT UNSIGNED NOT NULL UNIQUE,
  `sName` VARCHAR(32) NOT NULL default '',
  `sDescription` VARCHAR(32) NOT NULL default '',
  PRIMARY KEY  (`bID`),
	UNIQUE `sName` (`sName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Rights`
--

/*!40000 ALTER TABLE `Rights` DISABLE KEYS */;
LOCK TABLES `Rights` WRITE;
INSERT INTO `Rights` VALUES (1,'access','Access');
INSERT INTO `Rights` VALUES (2,'user','User Manager');
UNLOCK TABLES;
/*!40000 ALTER TABLE `Rights` ENABLE KEYS */;

--
-- Table structure for table `Server`
--

DROP TABLE IF EXISTS `Server`;
CREATE TABLE `Server` (
  `bSerial` SMALLINT UNSIGNED NOT NULL UNIQUE,
  `sCompany` VARCHAR(64) NOT NULL default 'Test',
  `sName` VARCHAR(64) NOT NULL default 'Test',
  `sCategories` VARCHAR(64) NOT NULL default 'test',
  `sPreferred` VARCHAR(64) NOT NULL default 'test',
  `sIP` VARCHAR(15) NOT NULL default '127.0.0.1',
  `sRemoteIP` VARCHAR(15) NOT NULL default '127.0.0.1',
  `sLocalIP` VARCHAR(15) NOT NULL default '127.0.0.1',
  `bPort` SMALLINT UNSIGNED NOT NULL default 80,
  `bSshPort` SMALLINT UNSIGNED NOT NULL default 22,
  `dTimestamp` DATETIME,
  `dInstall` DATE,
  `sMaintenance` VARCHAR(16) NOT NULL default 'install',
	`dMaintenanceOnsite` DATE,
  `fSkip` BOOLEAN NOT NULL default '0',
  `fSick` BOOLEAN NOT NULL default '0',
  `sOS` VARCHAR(3) NOT NULL default '',
  `sVersionInstalled` VARCHAR(8) NOT NULL default '',
  `sVersion` VARCHAR(3) NOT NULL default '3.1',
  `bNumcam` SMALLINT UNSIGNED NOT NULL default 0,
  `sMac` VARCHAR(2) NOT NULL default '',
  `sKey` VARCHAR(24) NOT NULL default '',
  `sKeyPos` VARCHAR(24) NOT NULL default '',
  `bPos` TINYINT(1) NOT NULL default '0',
  `sKill` VARCHAR(8) NOT NULL default '',
  `fEnterprise` BOOLEAN NOT NULL default '0',
  PRIMARY KEY  (`bSerial`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Server`
--

/*!40000 ALTER TABLE `Server` DISABLE KEYS */;
LOCK TABLES `Server` WRITE;
INSERT INTO `Server` VALUES (1,'International Plaza','DVS16 - Cameras 1-16','video,bobbycox,ip,demo','ip','216.195.99.67','216.195.99.67','127.0.0.1',8080,22,NOW(),'2002-09-01','plan1','2009-01-01',FALSE,'3.0',16,'','','',FALSE);
INSERT INTO `Server` VALUES (2,'Rosa\'s Cafe','Rosa\'s Cafe #16','video,bobbycox,rosas','rosas','65.66.116.234','65.66.116.234','127.0.0.1',8080,22,NOW(),'2002-09-01','plan1','2009-01-01',FALSE,'3.0',16,'','','',FALSE);
INSERT INTO `Server` VALUES (3,'Ronny Jordan','Ronny\'s Ranch','video,bobbycox,ronny','ronny','69.19.0.1','69.19.0.1','127.0.0.1',80,22,'2006-04-05 16:00:00','2007-03-06','free','2009-01-01',TRUE,'3.0',4,'','','',FALSE);
INSERT INTO `Server` VALUES (4,'Casters of Fort Worth','Ace Warehouse','video,ace','ace','68.89.124.38','68.89.124.38','127.0.0.1',80,22,'2006-05-30 09:36:54','2007-03-06','no','2009-01-01',FALSE,'2.5',0,'','','',FALSE);
INSERT INTO `Server` VALUES (5,'United Texas Entertainment','Blockbuster #34','video,bobbycox,ute,blockbuster','ute','208.180.246.43','208.180.246.43','127.0.0.1',80,22,NOW(),'2002-09-01','plan1','2009-01-01',FALSE,'3.0',8,'','','',FALSE);
UNLOCK TABLES;
/*!40000 ALTER TABLE `Server` ENABLE KEYS */;

--
-- Table structure for table `Camera`
--

DROP TABLE IF EXISTS `Camera`;
CREATE TABLE `Camera` (
	`bID` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
  `bSerial` SMALLINT UNSIGNED NOT NULL,
  `bCamera` SMALLINT UNSIGNED NOT NULL,
  `dTimestamp` DATETIME,
  `fSkip` BOOLEAN NOT NULL default '0',
	PRIMARY KEY  (`bID`),
  UNIQUE `Camera` (`bSerial`,`bCamera`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Camera`
--

/*!40000 ALTER TABLE `Camera` DISABLE KEYS */;
LOCK TABLES `Camera` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `Camera` ENABLE KEYS */;

--
-- Table structure for table `Misc`
--

DROP TABLE IF EXISTS `Misc`;
CREATE TABLE `Misc` (
  `sModule` VARCHAR(32) NOT NULL default '',
  `sName` VARCHAR(32) NOT NULL default '',
  `sValue` VARCHAR(32) NOT NULL default '',
	UNIQUE `sName` (`sModule`,`sName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Misc`
--

/*!40000 ALTER TABLE `Misc` DISABLE KEYS */;
LOCK TABLES `Misc` WRITE;
INSERT INTO `Misc` VALUES ( 'bugzilla', 'resolved-reminder-last', '0' );
INSERT INTO `Misc` VALUES ( 'bugzilla', 'install-reminder-last', '0' );
UNLOCK TABLES;
/*!40000 ALTER TABLE `Misc` ENABLE KEYS */;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
CREATE TABLE `log` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
  `timestamp` CHAR(14) NOT NULL default '00000000000000',
  `user_id` BIGINT UNSIGNED NOT NULL default '0',
  `message` VARCHAR(255),
  PRIMARY KEY  (`id`),
  KEY `timestamp` (`timestamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Tables for DVSLog Events 
--
DROP TABLE IF EXISTS `DVSLog`;

CREATE TABLE `DVSLog` (
`bID` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
`bSerial` BIGINT UNSIGNED NOT NULL,
`bEventID` BIGINT UNSIGNED NOT NULL,
`sData` VARCHAR(256) NOT NULL default '',
`dTimeStamp`  DATETIME,
 PRIMARY KEY (`bID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `CustSession`
--

DROP TABLE IF EXISTS `CustSession`;
CREATE TABLE `CustSession` (
  `bSerial` SMALLINT UNSIGNED NOT NULL default '0',
  `bUserID` BIGINT UNSIGNED NOT NULL UNIQUE,
  `dLastAccess` DATETIME NOT NULL,
  `sSessID` VARCHAR(255) NOT NULL default '',
  UNIQUE `sSessid` (`sSessID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `CustUser`;
CREATE TABLE `CustUser` (
  `bSerial` SMALLINT UNSIGNED NOT NULL default '0',
  `bID` BIGINT UNSIGNED NOT NULL default '0',
  `sName` VARCHAR(64) NOT NULL default '',
  `sPassword` VARCHAR(16) default NULL,
  `sDescription` VARCHAR(64) NOT NULL default '',
  `bType` TINYINT UNSIGNED NOT NULL default '0'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

