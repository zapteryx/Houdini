-- MySQL dump 10.16  Distrib 10.2.12-MariaDB, for osx10.13 (x86_64)
--
-- Host: localhost    Database: houdoo
-- ------------------------------------------------------
-- Server version	10.2.12-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activation_key`
--

DROP TABLE IF EXISTS `activation_key`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activation_key` (
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Penguin ID',
  `ActivationKey` char(255) NOT NULL COMMENT 'Penguin activation key',
  PRIMARY KEY (`PenguinID`,`ActivationKey`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin activation keys';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activation_key`
--

LOCK TABLES `activation_key` WRITE;
/*!40000 ALTER TABLE `activation_key` DISABLE KEYS */;
/*!40000 ALTER TABLE `activation_key` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ban`
--

DROP TABLE IF EXISTS `ban`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ban` (
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Banned penguin ID',
  `Issued` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Issue date',
  `Expires` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Expiry date',
  `ModeratorID` int(10) unsigned DEFAULT NULL COMMENT 'Moderator penguin ID',
  `Reason` tinyint(3) unsigned NOT NULL COMMENT 'Reason #',
  `Comment` text DEFAULT NULL,
  PRIMARY KEY (`PenguinID`,`Issued`,`Expires`),
  KEY `ModeratorID` (`ModeratorID`),
  CONSTRAINT `ban_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ban_ibfk_2` FOREIGN KEY (`ModeratorID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin ban records';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ban`
--

LOCK TABLES `ban` WRITE;
/*!40000 ALTER TABLE `ban` DISABLE KEYS */;
/*!40000 ALTER TABLE `ban` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buddy_list`
--

DROP TABLE IF EXISTS `buddy_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `buddy_list` (
  `PenguinID` int(10) unsigned NOT NULL,
  `BuddyID` int(10) unsigned NOT NULL,
  PRIMARY KEY (`PenguinID`,`BuddyID`),
  KEY `BuddyID` (`BuddyID`),
  CONSTRAINT `buddy_list_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `buddy_list_ibfk_2` FOREIGN KEY (`BuddyID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin buddy relationships';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buddy_list`
--

LOCK TABLES `buddy_list` WRITE;
/*!40000 ALTER TABLE `buddy_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `buddy_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cover_stamps`
--

DROP TABLE IF EXISTS `cover_stamps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cover_stamps` (
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Unique penguin ID',
  `Stamp` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Cover stamp or item ID',
  `X` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Cover X position',
  `Y` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Cover Y position',
  `Type` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Cover item type',
  `Rotation` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Stamp cover rotation',
  `Depth` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Stamp cover depth\n',
  PRIMARY KEY (`PenguinID`,`Stamp`),
  CONSTRAINT `cover_stamps_penguin_ID_fk` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Stamps placed on book cover';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cover_stamps`
--

LOCK TABLES `cover_stamps` WRITE;
/*!40000 ALTER TABLE `cover_stamps` DISABLE KEYS */;
/*!40000 ALTER TABLE `cover_stamps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deck`
--

DROP TABLE IF EXISTS `deck`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deck` (
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Owner penguin ID',
  `CardID` smallint(5) unsigned NOT NULL COMMENT 'Card type ID',
  `Quantity` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Quantity owned',
  PRIMARY KEY (`PenguinID`,`CardID`),
  KEY `PenguinID` (`PenguinID`),
  CONSTRAINT `deck_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin card jitsu decks';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deck`
--

LOCK TABLES `deck` WRITE;
/*!40000 ALTER TABLE `deck` DISABLE KEYS */;
/*!40000 ALTER TABLE `deck` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `furniture_inventory`
--

DROP TABLE IF EXISTS `furniture_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `furniture_inventory` (
  `PenguinID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Owner penguin ID',
  `FurnitureID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Furniture item ID',
  `Quantity` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Quantity owned',
  PRIMARY KEY (`PenguinID`,`FurnitureID`),
  CONSTRAINT `furniture_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin owned furniture';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `furniture_inventory`
--

LOCK TABLES `furniture_inventory` WRITE;
/*!40000 ALTER TABLE `furniture_inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `furniture_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `igloo`
--

DROP TABLE IF EXISTS `igloo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `igloo` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique igloo ID',
  `PenguinID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Owner penguin ID',
  `Type` smallint(5) unsigned NOT NULL DEFAULT 1 COMMENT 'Igloo type ID',
  `Floor` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Igloo flooring ID',
  `Music` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Igloo music ID',
  `Locked` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is igloo locked?',
  PRIMARY KEY (`ID`),
  KEY `PenguinID` (`PenguinID`),
  CONSTRAINT `igloo_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COMMENT='Penguin igloo settings';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `igloo`
--

LOCK TABLES `igloo` WRITE;
/*!40000 ALTER TABLE `igloo` DISABLE KEYS */;
/*!40000 ALTER TABLE `igloo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `igloo_furniture`
--

DROP TABLE IF EXISTS `igloo_furniture`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `igloo_furniture` (
  `IglooID` int(10) unsigned NOT NULL COMMENT 'Furniture igloo ID',
  `FurnitureID` mediumint(8) unsigned NOT NULL DEFAULT 1 COMMENT 'Furniture item ID',
  `X` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Igloo X position',
  `Y` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Igloo Y position',
  `Frame` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Furniture frame ID',
  `Rotation` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Furniture rotation ID',
  PRIMARY KEY (`IglooID`,`FurnitureID`,`X`,`Y`,`Frame`,`Rotation`),
  KEY `igloo_furniture_ibfk_1` (`IglooID`),
  CONSTRAINT `igloo_furniture_ibfk_1` FOREIGN KEY (`IglooID`) REFERENCES `igloo` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Furniture placed inside igloos';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `igloo_furniture`
--

LOCK TABLES `igloo_furniture` WRITE;
/*!40000 ALTER TABLE `igloo_furniture` DISABLE KEYS */;
/*!40000 ALTER TABLE `igloo_furniture` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `igloo_inventory`
--

DROP TABLE IF EXISTS `igloo_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `igloo_inventory` (
  `PenguinID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Owner penguin ID',
  `IglooID` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'Igloo ID',
  PRIMARY KEY (`PenguinID`,`IglooID`),
  CONSTRAINT `igloo_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin owned igloos';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `igloo_inventory`
--

LOCK TABLES `igloo_inventory` WRITE;
/*!40000 ALTER TABLE `igloo_inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `igloo_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ignore_list`
--

DROP TABLE IF EXISTS `ignore_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ignore_list` (
  `PenguinID` int(10) unsigned NOT NULL,
  `IgnoreID` int(10) unsigned NOT NULL,
  PRIMARY KEY (`PenguinID`,`IgnoreID`),
  KEY `IgnoreID` (`IgnoreID`),
  CONSTRAINT `ignore_list_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ignore_list_ibfk_2` FOREIGN KEY (`IgnoreID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin ignore relationships';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ignore_list`
--

LOCK TABLES `ignore_list` WRITE;
/*!40000 ALTER TABLE `ignore_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `ignore_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory` (
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Owner penguin ID',
  `ItemID` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Clothing item ID',
  PRIMARY KEY (`PenguinID`,`ItemID`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin owned clothing items';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES (101,1);
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login`
--

DROP TABLE IF EXISTS `login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `login` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique login ID',
  `PenguinID` int(10) unsigned NOT NULL,
  `Date` datetime NOT NULL DEFAULT current_timestamp(),
  `IPAddress` char(255) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `PenguinID` (`PenguinID`),
  CONSTRAINT `login_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=340 DEFAULT CHARSET=latin1 COMMENT='Penguin login records';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login`
--

LOCK TABLES `login` WRITE;
/*!40000 ALTER TABLE `login` DISABLE KEYS */;
/*!40000 ALTER TABLE `login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `penguin`
--

DROP TABLE IF EXISTS `penguin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `penguin` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique penguin ID',
  `Username` varchar(12) NOT NULL COMMENT 'Penguin login name',
  `Nickname` varchar(12) NOT NULL COMMENT 'Penguin display name',
  `Approval` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Username approval',
  `Password` char(255) NOT NULL COMMENT 'Password hash',
  `LoginKey` char(255) DEFAULT '',
  `Email` varchar(255) NOT NULL COMMENT 'User email address',
  `RegistrationDate` datetime NOT NULL DEFAULT current_timestamp(),
  `Active` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Email activated',
  `LastPaycheck` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'EPF previous paycheck',
  `MinutesPlayed` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Total minutes connected',
  `Moderator` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is user moderator?',
  `MascotStamp` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Mascot stamp ID',
  `Coins` mediumint(8) unsigned NOT NULL DEFAULT 500 COMMENT 'Penguin coins',
  `Color` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Penguin color ID',
  `Head` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin head item ID',
  `Face` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin face item ID',
  `Neck` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin neck item ID',
  `Body` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin body item ID',
  `Hand` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin hand item ID',
  `Feet` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin feet item ID',
  `Photo` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin background ID',
  `Flag` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT 'Penguin pin ID',
  `Permaban` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is penguin banned forever?',
  `BookModified` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is book cover modified?',
  `BookColor` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Stampbook cover color',
  `BookHighlight` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Stampbook cover color',
  `BookPattern` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Stampbook cover pattern',
  `BookIcon` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Stampbook cover icon',
  `AgentStatus` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is penguin EPF agent?',
  `FieldOpStatus` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is field op complete?',
  `CareerMedals` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'Total career medals',
  `AgentMedals` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'Current medals',
  `LastFieldOp` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date of last field op',
  `NinjaRank` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Ninja rank',
  `NinjaProgress` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Ninja progress',
  `FireNinjaRank` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Fire ninja rank',
  `FireNinjaProgress` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Fire ninja progress',
  `WaterNinjaRank` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Water ninja rank',
  `WaterNinjaProgress` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Water ninja progress',
  `NinjaMatchesWon` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'CardJitsu matches won',
  `FireMatchesWon` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'JitsuFire matches won',
  `WaterMatchesWon` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'JitsuWater matces won',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Username` (`Username`),
  KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=latin1 COMMENT='Penguins';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `penguin`
--

LOCK TABLES `penguin` WRITE;
/*!40000 ALTER TABLE `penguin` DISABLE KEYS */;
INSERT INTO `penguin` VALUES (101,'Basil','Basil',1,'$2b$12$CCYijGFRZyymIJWWNpkmP.pysAEN5E1mRwPtrjIDmTR3LnhKdJeBK','','basil@solero.me','2018-03-05 12:53:03',1,'2018-03-01 00:00:00',1055,1,7,42448,1,1099,0,3035,225,0,380,0,501,0,1,4,12,6,5,1,2,4,2,'2018-03-14 18:39:38',1,32,0,0,0,0,0,0,0);
/*!40000 ALTER TABLE `penguin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `penguin_redemption`
--

DROP TABLE IF EXISTS `penguin_redemption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `penguin_redemption` (
  `PenguinID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Unique penguin ID',
  `CodeID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Unique code ID',
  PRIMARY KEY (`PenguinID`,`CodeID`),
  KEY `penguin_redemption_redemption_code_ID_fk` (`CodeID`),
  CONSTRAINT `penguin_redemption_penguin_ID_fk` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `penguin_redemption_redemption_code_ID_fk` FOREIGN KEY (`CodeID`) REFERENCES `redemption_code` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Redeemed codes';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `penguin_redemption`
--

LOCK TABLES `penguin_redemption` WRITE;
/*!40000 ALTER TABLE `penguin_redemption` DISABLE KEYS */;
/*!40000 ALTER TABLE `penguin_redemption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postcard`
--

DROP TABLE IF EXISTS `postcard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `postcard` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique postcard ID',
  `SenderID` int(10) unsigned DEFAULT NULL COMMENT 'Sender penguin ID',
  `RecipientID` int(10) unsigned NOT NULL COMMENT 'Recipient penguin ID',
  `Type` smallint(5) unsigned NOT NULL COMMENT 'Postcard type ID',
  `SendDate` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date sent',
  `Details` char(255) NOT NULL DEFAULT '',
  `HasRead` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Is read?',
  PRIMARY KEY (`ID`),
  KEY `SenderID` (`SenderID`),
  KEY `RecipientID` (`RecipientID`),
  CONSTRAINT `postcard_ibfk_1` FOREIGN KEY (`SenderID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `postcard_ibfk_2` FOREIGN KEY (`RecipientID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1 COMMENT='Sent postcards';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postcard`
--

LOCK TABLES `postcard` WRITE;
/*!40000 ALTER TABLE `postcard` DISABLE KEYS */;
/*!40000 ALTER TABLE `postcard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `puffle`
--

DROP TABLE IF EXISTS `puffle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `puffle` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique puffle ID',
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Owner penguin ID',
  `Name` varchar(16) NOT NULL COMMENT 'Puffle name',
  `AdoptionDate` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date of adoption',
  `Type` tinyint(3) unsigned NOT NULL COMMENT 'Puffle type ID',
  `Health` tinyint(3) unsigned NOT NULL COMMENT 'Puffle health %',
  `Hunger` tinyint(3) unsigned NOT NULL COMMENT 'Puffle hunger %',
  `Rest` tinyint(3) unsigned NOT NULL COMMENT 'Puffle rest %',
  `Walking` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`ID`),
  KEY `PenguinID` (`PenguinID`),
  CONSTRAINT `puffle_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COMMENT='Adopted puffles';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `puffle`
--

LOCK TABLES `puffle` WRITE;
/*!40000 ALTER TABLE `puffle` DISABLE KEYS */;
/*!40000 ALTER TABLE `puffle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `redemption_award`
--

DROP TABLE IF EXISTS `redemption_award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `redemption_award` (
  `CodeID` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Unique code ID',
  `Award` smallint(5) unsigned NOT NULL DEFAULT 1 COMMENT 'Award item ID',
  PRIMARY KEY (`CodeID`,`Award`),
  CONSTRAINT `redemption_award_remption_code_ID_fk` FOREIGN KEY (`CodeID`) REFERENCES `redemption_code` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Redemption code awards';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `redemption_award`
--

LOCK TABLES `redemption_award` WRITE;
/*!40000 ALTER TABLE `redemption_award` DISABLE KEYS */;
INSERT INTO `redemption_award` VALUES (3,14436);
/*!40000 ALTER TABLE `redemption_award` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `redemption_code`
--

DROP TABLE IF EXISTS `redemption_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `redemption_code` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Unique code ID',
  `Code` varchar(16) NOT NULL DEFAULT '' COMMENT 'Remption code',
  `Type` enum('DS','BLANKET','CARD','GOLDEN','CAMPAIGN') NOT NULL DEFAULT 'BLANKET' COMMENT 'Code type',
  `Coins` mediumint(8) unsigned NOT NULL DEFAULT 0 COMMENT 'Code coins amount',
  `Expires` datetime DEFAULT NULL COMMENT 'Expiry date',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `remption_code_ID_uindex` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COMMENT='Redemption codes';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `redemption_code`
--

LOCK TABLES `redemption_code` WRITE;
/*!40000 ALTER TABLE `redemption_code` DISABLE KEYS */;
INSERT INTO `redemption_code` VALUES (3,'FREEHOOD','BLANKET',0,'2018-03-11 21:13:41');
/*!40000 ALTER TABLE `redemption_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stamp`
--

DROP TABLE IF EXISTS `stamp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stamp` (
  `PenguinID` int(10) unsigned NOT NULL COMMENT 'Stamp penguin ID',
  `Stamp` smallint(5) unsigned NOT NULL COMMENT 'Stamp ID',
  `Recent` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Is recently earned?',
  PRIMARY KEY (`PenguinID`,`Stamp`),
  CONSTRAINT `stamp_penguin_ID_fk` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin earned stamps';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stamp`
--

LOCK TABLES `stamp` WRITE;
/*!40000 ALTER TABLE `stamp` DISABLE KEYS */;
/*!40000 ALTER TABLE `stamp` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-17  0:09:14
