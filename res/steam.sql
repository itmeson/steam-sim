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
	`user_id` INT NOT NULL UNIQUE,
	`joined` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`image` TEXT NOT NULL,
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
	`token` VARCHAR(12) NOT NULL PRIMARY KEY,
	`user_id` INT NOT NULL UNIQUE,
	`lastupdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS `problems`;
CREATE TABLE `problems` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`type` INT NOT NULL,
	`name` TEXT NOT NULL,
	`desc` TEXT NOT NULL,
	`creator` INT NOT NULL,
	`background` TEXT NOT NULL,
	`handler` TEXT NOT NULL
);

DROP TABLE IF EXISTS `problemsets`;
CREATE TABLE `problemsets` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name` TEXT NOT NULL,
	`desc` TEXT NOT NULL,
	`creator` INT NOT NULL
);

DROP TABLE IF EXISTS `set_links`;
CREATE TABLE `set_links` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`set_id` INT NOT NULL,
	`problem_id` INT NOT NULL	
);

DROP TABLE IF EXISTS `problem_instances`;
CREATE TABLE `problem_instances` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`problem_id` INT NOT NULL,
	`user_id` INT NOT NULL,
	`completed` BOOLEAN NOT NULL,
	`start` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`end` timestamp NOT NULL,
	`data` TEXT NOT NULL
);

DROP TABLE IF EXISTS `problem_urls`;
CREATE TABLE `problem_urls` (
	`id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`problem_id` INT NOT NULL,
	`url` TEXT NOT NULL
);

-- -- Adding A New Problem -- --
--------------------------------
-- id: OMIT
-- type: 0=science, 1=technology, 2=engineering, 3=art, 4=math
-- name: Title of the problem
-- desc: FORMATTED description of problem. May include variable replacements
-- -- -- in the form of: {vars[vname]} within the string
-- creator: See below
-- background: Background information to the problem
-- handler: Name of the handler.
--------------------------------
INSERT INTO problems(`type`, `name`, `desc`, `background`, `handler`, `creator`)
	/* Modify as appropriate for your user account */
	VALUES(4, "Sum of two numbers", "Write a program to return the sum of {vars[x]} and {vars[y]}.", "This is a simple addition problem.", "AdditionHandler", (SELECT id FROM user_accounts WHERE username="wilhall"));
-- -- Adding Problem URLs -- --
--------------------------------
-- id: ID of the problem the URL is for
-- url: The URL
--------------------------------
INSERT INTO problem_urls(`problem_id`, `url`)
	/* This will work as long as it was the last problem added */
	VALUES((SELECT MAX(id) FROM problems), "http://en.wikipedia.org/wiki/Addition");

INSERT INTO problems(`type`, `name`, `desc`, `background`, `handler`, `creator`)
	VALUES(4, "Summation of numbers", "Write a program to return the summation of the following set of numbers: {vars[dataset]}", "This is a summation problem.", "SummationHandler", (SELECT id FROM user_accounts WHERE username="wilhall"));

INSERT INTO problem_urls(`problem_id`, `url`)
	VALUES((SELECT MAX(id) FROM problems), "http://en.wikipedia.org/wiki/Summation");

INSERT INTO problemsets(`name`, `desc`, `creator`)
	VALUES("Science", "Science problems", -1);

INSERT INTO problemsets(`name`, `desc`, `creator`)
	VALUES("Technology", "Technology problems", -1);

INSERT INTO problemsets(`name`, `desc`, `creator`)
	VALUES("Engineering", "Engineering problems", -1);

INSERT INTO problemsets(`name`, `desc`, `creator`)
	VALUES("Art", "Art problems", -1);

INSERT INTO problemsets(`name`, `desc`, `creator`)
	VALUES("Math", "Math problems", -1);