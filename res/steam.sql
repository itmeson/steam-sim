USE steam;

DROP TABLE IF EXISTS `users`;
| uas_users_accounts | CREATE TABLE `uas_users_accounts` (
  `User_ID` int(11) NOT NULL AUTO_INCREMENT,
  `School_ID` int(11) NOT NULL,
  `Username` varchar(25) NOT NULL,
  `Email` varchar(60) NOT NULL,
  `Password` varchar(60) NOT NULL,
  `FirstName` varchar(25) NOT NULL,
  `LastName` varchar(25) NOT NULL,
  PRIMARY KEY (`User_ID`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Password` (`Password`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 |

DROP TABLE IF EXISTS `sessions`;
| uas_users_sessions | CREATE TABLE `uas_users_sessions` (
  `Session_ID` int(11) NOT NULL AUTO_INCREMENT,
  `User_ID` int(11) NOT NULL,
  `Token` varchar(12) NOT NULL,
  `LastUpdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Session_ID`),
  UNIQUE KEY `Token` (`Token`)
);