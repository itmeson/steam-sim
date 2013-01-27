USE steam;

DROP TABLE IF EXISTS `user_accounts`;
CREATE TABLE `user_accounts` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`username` VARCHAR(25) NOT NULL UNIQUE,
	`email` VARCHAR(60) NOT NULL UNIQUE,
	`password` VARCHAR(60) NOT NULL,
	`first_name` VARCHAR(25) NOT NULL,
	`last_name` VARCHAR(25) NOT NULL,
	`admin` BOOLEAN NOT NULL DEFAULT FALSE,
	`superadmin` BOOLEAN NOT NULL DEFAULT FALSE 
	
);

DROP TABLE IF EXISTS `user_sessions`;
CREATE TABLE `user_sessions` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`user_id` INT NOT NULL UNIQUE,
	`token` VARCHAR(12) NOT NULL UNIQUE,
	`lastupdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS `perms_problem`;
CREATE TABLE `perms_problem` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`user_id` INT NOT NULL,
	`problem_id` INT NOT NULL,
	`level` INT NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS `perms_problemset`;
CREATE TABLE `perms_problemset` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`user_id` INT NOT NULL,
	`problemset_id` INT NOT NULL,
	`level` INT NOT NULL DEFAULT 0
);