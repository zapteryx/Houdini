# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: 127.0.0.1 (MySQL 5.6.35)
# Database: houdini
# Generation Time: 2017-10-17 12:37:02 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table bans
# ------------------------------------------------------------

DROP TABLE IF EXISTS `bans`;

CREATE TABLE `bans` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Moderator` char(12) NOT NULL,
  `Player` int(11) unsigned NOT NULL,
  `Comment` text NOT NULL,
  `Expiration` int(8) NOT NULL,
  `Time` int(8) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Time` (`Time`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table igloos
# ------------------------------------------------------------

DROP TABLE IF EXISTS `igloos`;

CREATE TABLE `igloos` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Owner` int(10) unsigned NOT NULL,
  `Type` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `Floor` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Music` smallint(6) NOT NULL DEFAULT '0',
  `Furniture` text NOT NULL,
  `Locked` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `igloos` WRITE;
/*!40000 ALTER TABLE `igloos` DISABLE KEYS */;

INSERT INTO `igloos` (`ID`, `Owner`, `Type`, `Floor`, `Music`, `Furniture`, `Locked`)
VALUES
	(1,101,18,0,0,'454|441|283|1|1,450|332|277|1|1,452|243|289|1|1',1),
	(2,102,1,0,0,'',1);

/*!40000 ALTER TABLE `igloos` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table penguins
# ------------------------------------------------------------

DROP TABLE IF EXISTS `penguins`;

CREATE TABLE `penguins` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Username` char(12) NOT NULL,
  `Nickname` char(16) NOT NULL,
  `Password` char(255) NOT NULL,
  `LoginKey` char(32) NOT NULL,
  `Email` char(254) NOT NULL,
  `RegistrationDate` int(8) NOT NULL,
  `LastPaycheck` int(8) NOT NULL,
  `Moderator` tinyint(1) NOT NULL DEFAULT '0',
  `Inventory` text NOT NULL,
  `Coins` mediumint(7) unsigned NOT NULL DEFAULT '500',
  `Igloo` int(10) unsigned NOT NULL COMMENT 'Current active igloo',
  `Igloos` text NOT NULL COMMENT 'Owned igloo types',
  `Floors` text NOT NULL COMMENT 'Owned floorings',
  `Furniture` text NOT NULL COMMENT 'Furniture inventory',
  `Color` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `Head` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Face` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Neck` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Body` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Hand` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Feet` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Photo` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Flag` smallint(5) unsigned NOT NULL DEFAULT '0',
  `Walking` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Puffle ID',
  `Banned` varchar(20) NOT NULL DEFAULT '0' COMMENT 'Timestamp of ban',
  `Stamps` text NOT NULL,
  `RecentStamps` text NOT NULL,
  `StampBook` varchar(150) NOT NULL DEFAULT '1%1%0%1',
  `EPF` varchar(9) NOT NULL DEFAULT '0,0,0,0',
  `Buddies` text NOT NULL,
  `Ignore` text NOT NULL,
  `NinjaRank` tinyint(10) NOT NULL DEFAULT '0'
  `NinjaRank` tinyint(100) NOT NULL DEFAULT '0'
  `Deck` varchar(2048) NOT NULL DEFAULT = '1,1|6,1|9,1|14,1|17,1|20,1|22,1|23,1|26,1|73,1|89,1|81,1'
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `penguins` WRITE;
/*!40000 ALTER TABLE `penguins` DISABLE KEYS */;

INSERT INTO `penguins` (`ID`, `Username`, `Nickname`, `Password`, `LoginKey`, `Email`, `RegistrationDate`, `Moderator`, `Inventory`, `Coins`, `Igloo`, `Igloos`, `Floors`, `Furniture`, `Color`, `Head`, `Face`, `Neck`, `Body`, `Hand`, `Feet`, `Photo`, `Flag`, `Walking`, `Banned`, `Stamps`, `RecentStamps`, `StampBook`, `EPF`, `Buddies`)
VALUES
	(101,'Basil','Basil','$2b$12$CCYijGFRZyymIJWWNpkmP.pysAEN5E1mRwPtrjIDmTR3LnhKdJeBK','','basil@basil.me',1505088789,1,'4%7%352%225%323%229%1099%904%1%172%3038%169%3035%3%12%15%6%9%10%5',196105,1,'1|18|30|13|33','','377|1%450|1%452|1%454|1%486|2',4,1099,0,172,225,0,352,904,0,0,'0','','','1%1%1%1','0,0,0,0','102|Feels'),
	(102,'Feels','Feels','$2b$12$CCYijGFRZyymIJWWNpkmP.pysAEN5E1mRwPtrjIDmTR3LnhKdJeBK','','feels@basil.me',1505088789,1,'4%7%352%225%323%229%1099%904',198490,1,'1','','',4,1099,0,0,229,323,352,904,0,0,'0','','','1%1%1%1','0,0,0,0','101|Basil');

/*!40000 ALTER TABLE `penguins` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table postcards
# ------------------------------------------------------------

DROP TABLE IF EXISTS `postcards`;

CREATE TABLE `postcards` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Recipient` int(10) unsigned NOT NULL,
  `SenderName` char(12) NOT NULL,
  `SenderID` int(10) unsigned NOT NULL,
  `Details` varchar(12) NOT NULL,
  `Date` int(8) NOT NULL,
  `Type` smallint(5) unsigned NOT NULL,
  `HasRead` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table puffles
# ------------------------------------------------------------

DROP TABLE IF EXISTS `puffles`;

CREATE TABLE `puffles` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Owner` int(10) unsigned NOT NULL,
  `Name` char(12) NOT NULL,
  `AdoptionDate` int(8) NOT NULL,
  `Type` tinyint(3) unsigned NOT NULL,
  `Health` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Hunger` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Rest` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Walking` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `puffles` WRITE;
/*!40000 ALTER TABLE `puffles` DISABLE KEYS */;

INSERT INTO `puffles` (`ID`, `Owner`, `Name`, `AdoptionDate`, `Type`, `Health`, `Hunger`, `Rest`, `Walking`)
VALUES
	(1,101,'Sweet',1508206792,1,100,100,100,0),
	(2,101,'Ying',1508240196,2,100,100,100,0);

/*!40000 ALTER TABLE `puffles` ENABLE KEYS */;
UNLOCK TABLES;



/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
