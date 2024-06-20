-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: db:3306
-- Creato il: Giu 10, 2024 alle 08:02
-- Versione del server: 8.4.0
-- Versione PHP: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sql-db-2`
--

-- --------------------------------------------------------

CREATE TABLE `Logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `date_time` datetime NOT NULL,
  `status_code` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

CREATE TABLE `Successes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `log_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `successes_log_id_fk` (`log_id`),
  CONSTRAINT `successes_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `Logs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

CREATE TABLE `Warnings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `log_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `warnings_log_id_fk` (`log_id`),
  CONSTRAINT `warnings_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `Logs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

CREATE TABLE `Errors` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `log_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `errors_log_id_fk` (`log_id`),
  CONSTRAINT `errors_log_id_fk` FOREIGN KEY (`log_id`) REFERENCES `Logs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

COMMIT;