USE steam;

DROP TABLE IF EXISTS `user_accounts`;
CREATE TABLE `user_accounts` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`profile_id` INT DEFAULT NULL,
	`username` VARCHAR(25) NOT NULL UNIQUE,
	`email` VARCHAR(60) NOT NULL UNIQUE,
	`password` VARCHAR(60) NOT NULL,
	`first_name` VARCHAR(25) NOT NULL,
	`last_name` VARCHAR(25) NOT NULL,
	`active` BOOLEAN NOT NULL DEFAULT FALSE,
	`admin` BOOLEAN NOT NULL DEFAULT FALSE,
	`superadmin` BOOLEAN NOT NULL DEFAULT FALSE 
);

DROP TABLE IF EXISTS `user_profiles`;
CREATE TABLE `user_profiles` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`interest_science` BOOLEAN NOT NULL DEFAULT FALSE,
	`interest_technology` BOOLEAN NOT NULL DEFAULT FALSE,
	`interest_engineering` BOOLEAN NOT NULL DEFAULT FALSE,
	`interest_art` BOOLEAN NOT NULL DEFAULT FALSE,
	`interest_math` BOOLEAN NOT NULL DEFAULT FALSE
);

DROP TABLE IF EXISTS `verification_tokens`;
CREATE TABLE `verification_tokens` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`user_id` INT NOT NULL UNIQUE,
	`token` VARCHAR(48) NOT NULL UNIQUE
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