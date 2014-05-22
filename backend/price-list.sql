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

USE monarch;

/*GRANT ALL ON monarch.* TO 'monarch' IDENTIFIED BY 'monarch';*/
/*GRANT ALL ON monarch.* TO 'monarch'@'localhost' IDENTIFIED BY 'monarch';*/

--
-- Table structure for table `PLCategory`
--

DROP TABLE IF EXISTS `PLCategory`;
CREATE TABLE `PLCategory` (
  `bID` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
  `sName` VARCHAR(32) NOT NULL default '',
  PRIMARY KEY  (`bID`),
	UNIQUE `sName` (`sName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PLCategory`
--

--
-- Table structure for table `PLItem`
--

DROP TABLE IF EXISTS `PLItem`;
CREATE TABLE `PLItem` (
  `bID` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
  `bCategory` BIGINT UNSIGNED NOT NULL default '0',
  `sName` VARCHAR(32) NOT NULL default '',
  `sDescription` VARCHAR(256) NOT NULL default '',
  `bCost` DECIMAL(6,2) UNSIGNED NOT NULL default '0.0',
  `bRetail` DECIMAL(6,2) UNSIGNED NOT NULL default '0.0',
  `bDiscount` DECIMAL(4,2) UNSIGNED NOT NULL default '0.0',
  PRIMARY KEY  (`bID`),
	UNIQUE `sItem` (`bCategory`, `sName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PLItem`
--

--
-- Table structure for table `PLMisc`
--

DROP TABLE IF EXISTS `PLMisc`;
CREATE TABLE `PLMisc` (
  `sName` VARCHAR(32) NOT NULL default '',
  `sValue` VARCHAR(32) NOT NULL default '',
	UNIQUE `sName` (`sName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PLMisc`
--

/*!40000 ALTER TABLE `PLMisc` DISABLE KEYS */;
LOCK TABLES `PLMisc` WRITE;
INSERT INTO `PLMisc` VALUES ('discount','20.00');
UNLOCK TABLES;
/*!40000 ALTER TABLE `PLMisc` ENABLE KEYS */;


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

