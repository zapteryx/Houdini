SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `activation_key` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Penguin ID',
  `ActivationKey` char(255) NOT NULL COMMENT 'Penguin activation key'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin activation keys';

CREATE TABLE `ban` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Banned penguin ID',
  `Issued` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Issue date',
  `Expires` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Expiry date',
  `ModeratorID` int(10) UNSIGNED DEFAULT NULL COMMENT 'Moderator penguin ID',
  `Reason` tinyint(3) UNSIGNED NOT NULL COMMENT 'Reason #',
  `Comment` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin ban records';

CREATE TABLE `buddy_list` (
  `PenguinID` int(10) UNSIGNED NOT NULL,
  `BuddyID` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin buddy relationships';

CREATE TABLE `care_inventory` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Owner penguin ID',
  `ItemID` int(10) UNSIGNED NOT NULL COMMENT 'Care item ID',
  `Quantity` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Quantity owned'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `care_inventory` (`PenguinID`, `ItemID`, `Quantity`) VALUES
(101, 3, 8),
(101, 21, 1),
(101, 52, 1),
(101, 71, 1),
(101, 72, 1),
(101, 77, 8),
(101, 78, 8),
(101, 79, 7),
(101, 143, 9),
(101, 145, 8),
(101, 146, 7),
(101, 153, 9),
(102, 3, 10),
(102, 79, 10);

CREATE TABLE `cover_stamps` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Unique penguin ID',
  `Stamp` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Cover stamp or item ID',
  `X` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Cover X position',
  `Y` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Cover Y position',
  `Type` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Cover item type',
  `Rotation` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Stamp cover rotation',
  `Depth` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Stamp cover depth\n'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Stamps placed on book cover';

CREATE TABLE `deck` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Owner penguin ID',
  `CardID` smallint(5) UNSIGNED NOT NULL COMMENT 'Card type ID',
  `Quantity` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Quantity owned'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin card jitsu decks';

CREATE TABLE `floor_inventory` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Owner penguin ID',
  `FloorID` int(10) UNSIGNED NOT NULL COMMENT 'Floor ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `furniture_inventory` (
  `PenguinID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Owner penguin ID',
  `FurnitureID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Furniture item ID',
  `Quantity` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Quantity owned'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin owned furniture';

INSERT INTO `furniture_inventory` (`PenguinID`, `FurnitureID`, `Quantity`) VALUES
(101, 201, 1),
(101, 206, 1),
(101, 211, 1),
(101, 225, 1),
(101, 226, 1),
(101, 536, 1),
(101, 596, 1),
(101, 616, 1),
(101, 617, 1),
(101, 632, 1),
(101, 653, 1),
(101, 662, 1),
(101, 961, 1),
(101, 2053, 1);

CREATE TABLE `igloo` (
  `ID` int(10) UNSIGNED NOT NULL COMMENT 'Unique igloo ID',
  `PenguinID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Owner penguin ID',
  `Type` smallint(5) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Igloo type ID',
  `Floor` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Igloo flooring ID',
  `Music` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Igloo music ID',
  `Location` smallint(5) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Igloo location ID',
  `Locked` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Is igloo locked?'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin igloo settings';

INSERT INTO `igloo` (`ID`, `PenguinID`, `Type`, `Floor`, `Music`, `Location`, `Locked`) VALUES
(1, 101, 23, 0, 3, 8, 0),
(10, 101, 63, 0, 0, 8, 1),
(11, 101, 69, 0, 0, 8, 1),
(12, 102, 1, 0, 0, 1, 1),
(13, 103, 1, 0, 0, 1, 1);

CREATE TABLE `igloo_furniture` (
  `IglooID` int(10) UNSIGNED NOT NULL COMMENT 'Furniture igloo ID',
  `FurnitureID` mediumint(8) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Furniture item ID',
  `X` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Igloo X position',
  `Y` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Igloo Y position',
  `Frame` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Furniture frame ID',
  `Rotation` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Furniture rotation ID'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Furniture placed inside igloos';

INSERT INTO `igloo_furniture` (`IglooID`, `FurnitureID`, `X`, `Y`, `Frame`, `Rotation`) VALUES
(1, 201, 434, 346, 1, 1),
(1, 206, 460, 293, 1, 1),
(1, 211, 498, 337, 1, 1),
(1, 225, 520, 286, 1, 1),
(1, 536, 604, 225, 1, 2),
(1, 617, 394, 288, 1, 1),
(1, 653, 398, 170, 1, 1),
(1, 662, 607, 147, 1, 2),
(1, 961, 218, 323, 1, 2),
(11, 616, 395, 176, 1, 2);

CREATE TABLE `igloo_inventory` (
  `PenguinID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Owner penguin ID',
  `IglooID` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Igloo ID'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin owned igloos';

INSERT INTO `igloo_inventory` (`PenguinID`, `IglooID`) VALUES
(101, 23),
(101, 57),
(101, 61),
(101, 62),
(101, 63),
(101, 65),
(101, 66),
(101, 68),
(101, 69),
(101, 70),
(101, 71),
(101, 73),
(101, 75),
(101, 84);

CREATE TABLE `igloo_likes` (
  `IglooID` int(10) UNSIGNED NOT NULL COMMENT 'Igloo''s unique ID',
  `OwnerID` int(10) UNSIGNED NOT NULL COMMENT 'Owner''s player ID',
  `PlayerID` int(10) UNSIGNED NOT NULL COMMENT 'Liker''s playeer ID',
  `Count` int(11) NOT NULL COMMENT 'Amount of likes',
  `Date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of like'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `igloo_likes` (`IglooID`, `OwnerID`, `PlayerID`, `Count`, `Date`) VALUES
(1, 101, 101, 1, '2018-05-08 15:07:32'),
(1, 101, 102, 1, '2018-08-07 18:23:49'),
(10, 101, 101, 1, '2018-05-08 15:07:28'),
(11, 101, 101, 1, '2018-05-08 15:07:24');

CREATE TABLE `ignore_list` (
  `PenguinID` int(10) UNSIGNED NOT NULL,
  `IgnoreID` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin ignore relationships';

CREATE TABLE `inventory` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Owner penguin ID',
  `ItemID` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Clothing item ID'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin owned clothing items';

INSERT INTO `inventory` (`PenguinID`, `ItemID`) VALUES
(101, 4),
(101, 114),
(101, 251),
(101, 323),
(101, 352),
(101, 357),
(101, 501),
(101, 652),
(101, 843),
(101, 929),
(101, 1597),
(101, 2101),
(101, 3032),
(101, 3064),
(101, 4107),
(101, 5108),
(101, 5126),
(101, 9298),
(101, 24318);

CREATE TABLE `location_inventory` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Owner penguin ID',
  `LocationID` int(10) UNSIGNED NOT NULL COMMENT 'Location ID'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `location_inventory` (`PenguinID`, `LocationID`) VALUES
(101, 8);

CREATE TABLE `login` (
  `ID` int(10) UNSIGNED NOT NULL COMMENT 'Unique login ID',
  `PenguinID` int(10) UNSIGNED NOT NULL,
  `Date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `IPAddress` char(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin login records';

INSERT INTO `login` (`ID`, `PenguinID`, `Date`, `IPAddress`) VALUES
(24, 101, '2018-08-04 12:53:50', '127.0.0.1'),
(25, 101, '2018-08-04 13:45:08', '127.0.0.1'),
(26, 101, '2018-08-04 13:50:42', '127.0.0.1'),
(27, 101, '2018-08-04 14:25:18', '127.0.0.1'),
(28, 101, '2018-08-04 14:37:03', '127.0.0.1'),
(29, 101, '2018-08-04 14:38:14', '127.0.0.1'),
(30, 101, '2018-08-04 16:18:13', '127.0.0.1'),
(31, 101, '2018-08-04 16:36:21', '127.0.0.1'),
(32, 101, '2018-08-04 16:42:00', '127.0.0.1'),
(33, 101, '2018-08-04 16:47:41', '127.0.0.1'),
(34, 101, '2018-08-04 16:56:20', '127.0.0.1'),
(35, 101, '2018-08-04 16:57:35', '127.0.0.1'),
(36, 101, '2018-08-04 18:01:26', '127.0.0.1'),
(37, 101, '2018-08-06 12:03:40', '127.0.0.1'),
(38, 101, '2018-08-06 12:09:44', '127.0.0.1'),
(39, 101, '2018-08-06 12:11:38', '127.0.0.1'),
(40, 101, '2018-08-06 12:17:07', '127.0.0.1'),
(41, 101, '2018-08-06 15:21:33', '127.0.0.1'),
(42, 101, '2018-08-06 16:25:06', '127.0.0.1'),
(43, 101, '2018-08-06 16:30:03', '127.0.0.1'),
(44, 101, '2018-08-06 16:31:20', '127.0.0.1'),
(45, 101, '2018-08-06 16:37:09', '127.0.0.1'),
(46, 101, '2018-08-06 17:10:01', '127.0.0.1'),
(47, 101, '2018-08-07 14:05:41', '127.0.0.1'),
(48, 102, '2018-08-07 14:40:22', '127.0.0.1'),
(49, 101, '2018-08-07 14:38:35', '127.0.0.1'),
(50, 101, '2018-08-07 15:39:32', '127.0.0.1'),
(51, 101, '2018-08-07 15:54:15', '127.0.0.1'),
(52, 101, '2018-08-07 15:55:50', '127.0.0.1'),
(53, 101, '2018-08-07 16:37:39', '127.0.0.1'),
(54, 101, '2018-08-07 16:38:26', '127.0.0.1'),
(55, 101, '2018-08-07 16:39:24', '127.0.0.1'),
(56, 101, '2018-08-07 16:42:42', '127.0.0.1'),
(57, 101, '2018-08-07 17:58:11', '127.0.0.1'),
(58, 101, '2018-08-07 18:14:34', '127.0.0.1'),
(59, 101, '2018-08-07 18:19:40', '127.0.0.1'),
(60, 102, '2018-08-07 18:22:19', '127.0.0.1'),
(61, 101, '2018-08-07 18:20:15', '127.0.0.1'),
(62, 102, '2018-08-07 18:26:23', '127.0.0.1'),
(63, 101, '2018-08-07 18:25:09', '127.0.0.1'),
(64, 101, '2018-08-07 18:27:48', '127.0.0.1'),
(65, 102, '2018-08-07 18:27:46', '127.0.0.1'),
(66, 102, '2018-08-07 18:30:02', '127.0.0.1'),
(67, 101, '2018-08-07 18:29:59', '127.0.0.1'),
(68, 103, '2018-08-07 18:30:53', '127.0.0.1'),
(69, 101, '2018-08-08 10:57:14', '127.0.0.1'),
(70, 101, '2018-08-08 11:12:01', '127.0.0.1'),
(71, 101, '2018-08-08 11:16:26', '127.0.0.1'),
(72, 101, '2018-08-08 11:25:41', '127.0.0.1'),
(73, 101, '2018-08-08 11:33:30', '127.0.0.1'),
(74, 101, '2018-08-08 12:24:46', '127.0.0.1'),
(75, 101, '2018-08-08 12:53:44', '127.0.0.1');

CREATE TABLE `penguin` (
  `ID` int(10) UNSIGNED NOT NULL COMMENT 'Unique penguin ID',
  `Username` varchar(12) NOT NULL COMMENT 'Penguin login name',
  `Nickname` varchar(12) NOT NULL COMMENT 'Penguin display name',
  `Approval` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Username approval',
  `Password` char(255) NOT NULL COMMENT 'Password hash',
  `LoginKey` char(255) DEFAULT '',
  `ConfirmationHash` char(255) DEFAULT NULL,
  `Email` varchar(255) NOT NULL COMMENT 'User email address',
  `RegistrationDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Active` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Email activated',
  `Igloo` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Player''s active igloo',
  `LastPaycheck` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'EPF previous paycheck',
  `MinutesPlayed` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Total minutes connected',
  `Moderator` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is user moderator?',
  `MascotStamp` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Mascot stamp ID',
  `Coins` mediumint(8) UNSIGNED NOT NULL DEFAULT '500' COMMENT 'Penguin coins',
  `Color` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Penguin color ID',
  `Head` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin head item ID',
  `Face` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin face item ID',
  `Neck` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin neck item ID',
  `Body` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin body item ID',
  `Hand` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin hand item ID',
  `Feet` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin feet item ID',
  `Photo` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin background ID',
  `Flag` smallint(5) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Penguin pin ID',
  `Permaban` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is penguin banned forever?',
  `BookModified` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is book cover modified?',
  `BookColor` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Stampbook cover color',
  `BookHighlight` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Stampbook cover color',
  `BookPattern` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Stampbook cover pattern',
  `BookIcon` tinyint(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Stampbook cover icon',
  `AgentStatus` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is penguin EPF agent?',
  `FieldOpStatus` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is field op complete?',
  `CareerMedals` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Total career medals',
  `AgentMedals` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Current medals',
  `LastFieldOp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of last field op',
  `NinjaRank` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Ninja rank',
  `NinjaProgress` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Ninja progress',
  `FireNinjaRank` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Fire ninja rank',
  `FireNinjaProgress` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Fire ninja progress',
  `WaterNinjaRank` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Water ninja rank',
  `WaterNinjaProgress` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Water ninja progress',
  `NinjaMatchesWon` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'CardJitsu matches won',
  `FireMatchesWon` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'JitsuFire matches won',
  `WaterMatchesWon` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'JitsuWater matces won',
  `Rank` tinyint(1) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguins';

INSERT INTO `penguin` (`ID`, `Username`, `Nickname`, `Approval`, `Password`, `LoginKey`, `ConfirmationHash`, `Email`, `RegistrationDate`, `Active`, `Igloo`, `LastPaycheck`, `MinutesPlayed`, `Moderator`, `MascotStamp`, `Coins`, `Color`, `Head`, `Face`, `Neck`, `Body`, `Hand`, `Feet`, `Photo`, `Flag`, `Permaban`, `BookModified`, `BookColor`, `BookHighlight`, `BookPattern`, `BookIcon`, `AgentStatus`, `FieldOpStatus`, `CareerMedals`, `AgentMedals`, `LastFieldOp`, `NinjaRank`, `NinjaProgress`, `FireNinjaRank`, `FireNinjaProgress`, `WaterNinjaRank`, `WaterNinjaProgress`, `NinjaMatchesWon`, `FireMatchesWon`, `WaterMatchesWon`, `Rank`) VALUES
(101, 'Houdini', 'Houdini', 1, '$2y$12$dBWhLSF76Xw6RMxOXCByAunyj7boiz2nVxQ2PNlXVT7dXYp/gSo0u', '', '3dd3e91dca2e8b740d1c71b9fda33c30', 'houdini@hou.dini', '2018-05-08 10:19:15', 1, 1, '2018-08-01 00:00:00', 227, 0, 0, 481010, 4, 652, 114, 0, 4107, 0, 352, 9298, 501, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, '2018-05-08 10:19:15', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
(102, 'Basil', 'Basil', 1, '$2y$12$dBWhLSF76Xw6RMxOXCByAunyj7boiz2nVxQ2PNlXVT7dXYp/gSo0u', '', '9e9b330cc72e83673f2fe3e746c16f56', 'basil@baesel.net', '2018-08-07 14:38:28', 1, 12, '2018-08-01 00:00:00', 15, 0, 0, 49200, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, '2018-08-07 14:38:28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
(103, 'Arty', 'Arty', 1, '$2y$12$dBWhLSF76Xw6RMxOXCByAunyj7boiz2nVxQ2PNlXVT7dXYp/gSo0u', '', 'f6b4490235cdef77dfbe6aad8dc6d1ad', 'arty@solero.me', '2018-08-07 18:30:44', 1, 13, '2018-08-01 00:00:00', 4, 0, 0, 50000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, '2018-08-07 18:30:44', 0, 0, 0, 0, 0, 0, 0, 0, 0, 1);

CREATE TABLE `penguin_redemption` (
  `PenguinID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Unique penguin ID',
  `CodeID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Unique code ID'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Redeemed codes';

CREATE TABLE `postcard` (
  `ID` int(10) UNSIGNED NOT NULL COMMENT 'Unique postcard ID',
  `SenderID` int(10) UNSIGNED DEFAULT NULL COMMENT 'Sender penguin ID',
  `RecipientID` int(10) UNSIGNED NOT NULL COMMENT 'Recipient penguin ID',
  `Type` smallint(5) UNSIGNED NOT NULL COMMENT 'Postcard type ID',
  `SendDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date sent',
  `Details` char(255) NOT NULL DEFAULT '',
  `HasRead` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Is read?'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Sent postcards';

INSERT INTO `postcard` (`ID`, `SenderID`, `RecipientID`, `Type`, `SendDate`, `Details`, `HasRead`) VALUES
(51, NULL, 102, 111, '2018-08-07 14:41:00', 'Tabby', 0),
(55, NULL, 102, 112, '2018-08-07 18:22:20', '', 0),
(56, NULL, 101, 112, '2018-08-08 10:53:50', '', 0),
(57, NULL, 103, 112, '2018-08-08 12:25:42', '', 0);

CREATE TABLE `puffle` (
  `ID` int(10) UNSIGNED NOT NULL COMMENT 'Unique puffle ID',
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Owner penguin ID',
  `Name` varchar(16) NOT NULL COMMENT 'Puffle name',
  `AdoptionDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of adoption',
  `Type` tinyint(3) UNSIGNED NOT NULL COMMENT 'Puffle type ID',
  `Subtype` smallint(5) UNSIGNED NOT NULL COMMENT 'Puffle subtype ID',
  `Food` tinyint(3) UNSIGNED NOT NULL COMMENT 'Puffle food %',
  `Play` tinyint(3) UNSIGNED NOT NULL COMMENT 'Puffle play %',
  `Rest` tinyint(3) UNSIGNED NOT NULL COMMENT 'Puffle rest %',
  `Clean` tinyint(3) UNSIGNED NOT NULL COMMENT 'Puffle clean %',
  `Walking` tinyint(4) DEFAULT '0',
  `Hat` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Puffle hat ID',
  `Backyard` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Determines the puffle''s location'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Adopted puffles';

INSERT INTO `puffle` (`ID`, `PenguinID`, `Name`, `AdoptionDate`, `Type`, `Subtype`, `Food`, `Play`, `Rest`, `Clean`, `Walking`, `Hat`, `Backyard`) VALUES
(22, 101, 'Wee', '2018-08-06 17:10:49', 1, 0, 100, 0, 41, 91, 0, 52, 0),
(23, 102, 'Tabby', '2018-08-07 14:41:00', 8, 1007, 100, 80, 120, 100, 0, 0, 0),
(24, 101, 'Blurp', '2018-08-07 14:55:59', 4, 0, 37, 100, 4, 67, 0, 72, 0);

CREATE TABLE `redemption_award` (
  `CodeID` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Unique code ID',
  `Award` smallint(5) UNSIGNED NOT NULL DEFAULT '1' COMMENT 'Award item ID'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Redemption code awards';

CREATE TABLE `redemption_code` (
  `ID` int(10) UNSIGNED NOT NULL COMMENT 'Unique code ID',
  `Code` varchar(16) NOT NULL DEFAULT '' COMMENT 'Remption code',
  `Type` enum('DS','BLANKET','CARD','GOLDEN','CAMPAIGN') NOT NULL DEFAULT 'BLANKET' COMMENT 'Code type',
  `Coins` mediumint(8) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Code coins amount',
  `Expires` datetime DEFAULT NULL COMMENT 'Expiry date'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Redemption codes';

CREATE TABLE `stamp` (
  `PenguinID` int(10) UNSIGNED NOT NULL COMMENT 'Stamp penguin ID',
  `Stamp` smallint(5) UNSIGNED NOT NULL COMMENT 'Stamp ID',
  `Recent` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Is recently earned?'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Penguin earned stamps';


ALTER TABLE `activation_key`
  ADD PRIMARY KEY (`PenguinID`,`ActivationKey`);

ALTER TABLE `ban`
  ADD PRIMARY KEY (`PenguinID`,`Issued`,`Expires`),
  ADD KEY `ModeratorID` (`ModeratorID`);

ALTER TABLE `buddy_list`
  ADD PRIMARY KEY (`PenguinID`,`BuddyID`),
  ADD KEY `BuddyID` (`BuddyID`);

ALTER TABLE `care_inventory`
  ADD PRIMARY KEY (`PenguinID`,`ItemID`);

ALTER TABLE `cover_stamps`
  ADD PRIMARY KEY (`PenguinID`,`Stamp`);

ALTER TABLE `deck`
  ADD PRIMARY KEY (`PenguinID`,`CardID`),
  ADD KEY `PenguinID` (`PenguinID`);

ALTER TABLE `floor_inventory`
  ADD PRIMARY KEY (`PenguinID`,`FloorID`);

ALTER TABLE `furniture_inventory`
  ADD PRIMARY KEY (`PenguinID`,`FurnitureID`);

ALTER TABLE `igloo`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `PenguinID` (`PenguinID`);

ALTER TABLE `igloo_furniture`
  ADD PRIMARY KEY (`IglooID`,`FurnitureID`,`X`,`Y`,`Frame`,`Rotation`),
  ADD KEY `igloo_furniture_ibfk_1` (`IglooID`);

ALTER TABLE `igloo_inventory`
  ADD PRIMARY KEY (`PenguinID`,`IglooID`);

ALTER TABLE `igloo_likes`
  ADD PRIMARY KEY (`IglooID`,`PlayerID`),
  ADD KEY `OwnerID` (`OwnerID`),
  ADD KEY `PlayerID` (`PlayerID`);

ALTER TABLE `ignore_list`
  ADD PRIMARY KEY (`PenguinID`,`IgnoreID`),
  ADD KEY `IgnoreID` (`IgnoreID`);

ALTER TABLE `inventory`
  ADD PRIMARY KEY (`PenguinID`,`ItemID`);

ALTER TABLE `location_inventory`
  ADD PRIMARY KEY (`PenguinID`,`LocationID`);

ALTER TABLE `login`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `PenguinID` (`PenguinID`);

ALTER TABLE `penguin`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `Username` (`Username`),
  ADD KEY `Email` (`Email`);

ALTER TABLE `penguin_redemption`
  ADD PRIMARY KEY (`PenguinID`,`CodeID`),
  ADD KEY `penguin_redemption_redemption_code_ID_fk` (`CodeID`);

ALTER TABLE `postcard`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `SenderID` (`SenderID`),
  ADD KEY `RecipientID` (`RecipientID`);

ALTER TABLE `puffle`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `PenguinID` (`PenguinID`);

ALTER TABLE `redemption_award`
  ADD PRIMARY KEY (`CodeID`,`Award`);

ALTER TABLE `redemption_code`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `remption_code_ID_uindex` (`ID`);

ALTER TABLE `stamp`
  ADD PRIMARY KEY (`PenguinID`,`Stamp`);


ALTER TABLE `igloo`
  MODIFY `ID` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique igloo ID', AUTO_INCREMENT=14;

ALTER TABLE `login`
  MODIFY `ID` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique login ID', AUTO_INCREMENT=76;

ALTER TABLE `penguin`
  MODIFY `ID` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique penguin ID', AUTO_INCREMENT=104;

ALTER TABLE `postcard`
  MODIFY `ID` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique postcard ID', AUTO_INCREMENT=58;

ALTER TABLE `puffle`
  MODIFY `ID` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique puffle ID', AUTO_INCREMENT=25;

ALTER TABLE `redemption_code`
  MODIFY `ID` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique code ID';


ALTER TABLE `ban`
  ADD CONSTRAINT `ban_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `ban_ibfk_2` FOREIGN KEY (`ModeratorID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `buddy_list`
  ADD CONSTRAINT `buddy_list_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `buddy_list_ibfk_2` FOREIGN KEY (`BuddyID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `care_inventory`
  ADD CONSTRAINT `care_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `cover_stamps`
  ADD CONSTRAINT `cover_stamps_penguin_ID_fk` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `deck`
  ADD CONSTRAINT `deck_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `floor_inventory`
  ADD CONSTRAINT `floor_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `furniture_inventory`
  ADD CONSTRAINT `furniture_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `igloo`
  ADD CONSTRAINT `igloo_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `igloo_furniture`
  ADD CONSTRAINT `igloo_furniture_ibfk_1` FOREIGN KEY (`IglooID`) REFERENCES `igloo` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `igloo_inventory`
  ADD CONSTRAINT `igloo_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `igloo_likes`
  ADD CONSTRAINT `igloo_likes_ibfk_1` FOREIGN KEY (`IglooID`) REFERENCES `igloo` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `igloo_likes_ibfk_2` FOREIGN KEY (`OwnerID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `igloo_likes_ibfk_3` FOREIGN KEY (`PlayerID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `ignore_list`
  ADD CONSTRAINT `ignore_list_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `ignore_list_ibfk_2` FOREIGN KEY (`IgnoreID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `inventory`
  ADD CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `location_inventory`
  ADD CONSTRAINT `location_inventory_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `login`
  ADD CONSTRAINT `login_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `penguin_redemption`
  ADD CONSTRAINT `penguin_redemption_penguin_ID_fk` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `penguin_redemption_redemption_code_ID_fk` FOREIGN KEY (`CodeID`) REFERENCES `redemption_code` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `postcard`
  ADD CONSTRAINT `postcard_ibfk_1` FOREIGN KEY (`SenderID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `postcard_ibfk_2` FOREIGN KEY (`RecipientID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `puffle`
  ADD CONSTRAINT `puffle_ibfk_1` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `redemption_award`
  ADD CONSTRAINT `redemption_award_remption_code_ID_fk` FOREIGN KEY (`CodeID`) REFERENCES `redemption_code` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `stamp`
  ADD CONSTRAINT `stamp_penguin_ID_fk` FOREIGN KEY (`PenguinID`) REFERENCES `penguin` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
