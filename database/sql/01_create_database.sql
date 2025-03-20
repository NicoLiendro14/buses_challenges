-- Create database if not exists
CREATE DATABASE IF NOT EXISTS school_buses;
USE school_buses;

CREATE TABLE IF NOT EXISTS `buses` (
    `id` int NOT NULL AUTO_INCREMENT,
    `title` varchar(256) DEFAULT NULL,
    `year` varchar(10) DEFAULT NULL,
    `make` varchar(25) DEFAULT NULL,
    `model` varchar(50) DEFAULT NULL,
    `body` varchar(25) DEFAULT NULL,
    `chassis` varchar(25) DEFAULT NULL,
    `engine` varchar(60) DEFAULT NULL,
    `transmission` varchar(60) DEFAULT NULL,
    `mileage` varchar(100) DEFAULT NULL,
    `passengers` varchar(60) DEFAULT NULL,
    `wheelchair` varchar(60) DEFAULT NULL,
    `color` varchar(60) DEFAULT NULL,
    `interior_color` varchar(60) DEFAULT NULL,
    `exterior_color` varchar(60) DEFAULT NULL,
    `published` tinyint(1) DEFAULT 0,
    `featured` tinyint(1) DEFAULT 0,
    `sold` tinyint(1) DEFAULT 0,
    `scraped` tinyint(1) DEFAULT 0,
    `draft` tinyint(1) DEFAULT 0,
    `source` varchar(300) DEFAULT NULL,
    `source_url` varchar(1000) DEFAULT NULL,
    `price` varchar(30) DEFAULT NULL,
    `cprice` varchar(30) DEFAULT NULL,
    `vin` varchar(60) DEFAULT NULL,
    `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    `gvwr` varchar(50) DEFAULT NULL,
    `dimensions` varchar(300) DEFAULT NULL,
    `luggage` tinyint(1) DEFAULT 0,
    `state_bus_standard` varchar(25) DEFAULT NULL,
    `airconditioning` enum('REAR', 'DASH', 'BOTH', 'OTHER', 'NONE') DEFAULT 'OTHER',
    `location` varchar(30) DEFAULT NULL,
    `brake` varchar(30) DEFAULT NULL,
    `contact_email` varchar(100) DEFAULT NULL,
    `contact_phone` varchar(100) DEFAULT NULL,
    `us_region` enum('NORTHEAST', 'MIDWEST', 'WEST', 'SOUTHWEST', 'SOUTHEAST', 'OTHER') DEFAULT 'OTHER',
    `description` longtext DEFAULT NULL,
    `score` tinyint(1) DEFAULT 0,
    `category_id` int DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_bus_year` (`year`),
    KEY `idx_bus_make` (`make`),
    KEY `idx_bus_model` (`model`),
    KEY `idx_bus_price` (`price`),
    KEY `idx_bus_mileage` (`mileage`),
    KEY `idx_bus_location` (`location`),
    KEY `idx_bus_us_region` (`us_region`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `buses_overview` (
    `id` int NOT NULL AUTO_INCREMENT,
    `bus_id` int DEFAULT NULL,
    `mdesc` longtext DEFAULT NULL,
    `intdesc` longtext DEFAULT NULL,
    `extdesc` longtext DEFAULT NULL,
    `features` longtext DEFAULT NULL,
    `specs` longtext DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `busld` (`bus_id`),
    CONSTRAINT `buses_overview_ibfk_1` FOREIGN KEY (`bus_id`) REFERENCES `buses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `buses_images` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(64) DEFAULT NULL,
    `url` varchar(1000) DEFAULT NULL,
    `description` longtext DEFAULT NULL,
    `image_index` INT DEFAULT 0,
    `bus_id` int DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `busid` (`bus_id`) USING BTREE,
    CONSTRAINT `buses_images_ibfk_1` FOREIGN KEY (`bus_id`) REFERENCES `buses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4; 