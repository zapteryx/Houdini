# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: 127.0.0.1 (MySQL 5.6.35)
# Database: houdini
# Generation Time: 2017-10-14 10:55:49 +0000
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

CREATE TABLE `bans` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Moderator` char(12) NOT NULL,
  `Player` int(11) unsigned NOT NULL,
  `Comment` text NOT NULL,
  `Expiration` int(8) NOT NULL,
  `Time` int(8) NOT NULL,
  `Type` smallint(3) unsigned NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Time` (`Time`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table igloos
# ------------------------------------------------------------

CREATE TABLE `igloos` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Owner` int(10) unsigned NOT NULL,
  `Type` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `Floor` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Music` smallint(6) NOT NULL DEFAULT '0',
  `Furniture` text NOT NULL,
  `Locked` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

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

CREATE TABLE `penguins` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Username` char(12) NOT NULL,
  `Nickname` char(16) NOT NULL,
  `Password` char(255) NOT NULL,
  `LoginKey` char(32) NOT NULL,
  `Avatar` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT 'Don''t think ID will go beyond 255',
  `AvatarAttributes` char(98) NOT NULL DEFAULT '{"spriteScale":100,"spriteSpeed":100,"ignoresBlockLayer":false,"invisible":false,"floating":false}',
  `Email` char(254) NOT NULL,
  `RegistrationDate` int(8) NOT NULL,
  `Moderator` tinyint(1) NOT NULL DEFAULT '0',
  `Inventory` text NOT NULL,
  `Coins` mediumint(7) unsigned NOT NULL DEFAULT '200000',
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
  `StampBook` varchar(150) NOT NULL DEFAULT '1%1%1%1',
  `EPF` varchar(9) NOT NULL DEFAULT '0,0,0',
  `Buddies` text NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=latin1;

LOCK TABLES `penguins` WRITE;
/*!40000 ALTER TABLE `penguins` DISABLE KEYS */;

INSERT INTO `penguins` (`ID`, `Username`, `Nickname`, `Password`, `LoginKey`, `Avatar`, `AvatarAttributes`, `Email`, `RegistrationDate`, `Moderator`, `Inventory`, `Coins`, `Igloo`, `Igloos`, `Floors`, `Furniture`, `Color`, `Head`, `Face`, `Neck`, `Body`, `Hand`, `Feet`, `Photo`, `Flag`, `Walking`, `Banned`, `Stamps`, `StampBook`, `EPF`, `Buddies`)
VALUES
	(101,'Basil','Basil','$2b$12$CCYijGFRZyymIJWWNpkmP.pysAEN5E1mRwPtrjIDmTR3LnhKdJeBK','',0,'{\"spriteScale\":100,\"spriteSpeed\":100,\"ignoresBlockLayer\":false,\"invisible\":false,\"floating\":false}','basil@basil.me',1505088789,1,'4%7%352%225%323%229%1099%904%1%172%3038%169%3035%3%12%15%6%9%10%5',197705,1,'1|18|30|13|33','','377|1%450|1%452|1%454|1%486|2',4,1099,0,172,225,323,352,904,0,0,'0','','1%1%1%1','0,0,0','102|Feels'),
	(102,'Feels','Feels','$2b$12$CCYijGFRZyymIJWWNpkmP.pysAEN5E1mRwPtrjIDmTR3LnhKdJeBK','',0,'{\"spriteScale\":100,\"spriteSpeed\":100,\"ignoresBlockLayer\":false,\"invisible\":false,\"floating\":false}','feels@basil.me',1505088789,1,'4%7%352%225%323%229%1099%904',198490,1,'1','','',4,1099,0,0,229,323,352,904,0,0,'0','','1%1%1%1','0,0,0','101|Basil');

/*!40000 ALTER TABLE `penguins` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table postcards
# ------------------------------------------------------------

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

CREATE TABLE `puffles` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Owner` int(10) unsigned NOT NULL,
  `Name` char(12) NOT NULL,
  `AdoptionDate` int(8) NOT NULL,
  `Type` tinyint(3) unsigned NOT NULL,
  `Subtype` smallint(5) unsigned NOT NULL,
  `Hat` smallint(5) unsigned NOT NULL,
  `Food` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Play` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Rest` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Clean` tinyint(3) unsigned NOT NULL DEFAULT '100',
  `Backyard` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
