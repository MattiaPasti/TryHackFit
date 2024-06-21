-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Creato il: Giu 20, 2024 alle 23:24
-- Versione del server: 10.4.32-MariaDB
-- Versione PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sql-db-1`
--

-- --------------------------------------------------------

-- Admin Login

-- Email: superadminflaskapp@fitstickeeper.com

-- Pass: I.UUxR!CAur+k0{V0{eQ5Mf,2

-- --------------------------------------------------------

--
-- Struttura della tabella `Password`
--

CREATE TABLE `Password` (
  `id` bigint(20) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `Role`
--

CREATE TABLE `Role` (
  `id` bigint(20) NOT NULL,
  `role` varchar(255) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dump dei dati per la tabella `Role`
--

INSERT INTO `Role` (`id`, `role`, `user_id`) VALUES
(1, 'gAAAAABmdJ32JHAhSxFc0777S2nQ5kCOBuNfPXiD-UPaZL_0hbVqjmSndAZ2sAVUfB-8Yl8h8dXHqL2y8jTxmDxHW33AmkqH5A==', 1);

-- --------------------------------------------------------

--
-- Struttura della tabella `User`
--

CREATE TABLE `User` (
  `id` bigint(20) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dump dei dati per la tabella `User`
--

INSERT INTO `User` (`id`, `username`, `email`, `password`) VALUES
(1, 'Admin', 'b4a55a91a7eb9965b9e4a0167f8ba392ca352127788d71ac52f7e0dc220f7829', '1e172d906cfb9071e96ef6111a33928cf873f8253c4b6125f077059e020b09d9');

-- --------------------------------------------------------

--
-- Struttura della tabella `UserSalt`
--

CREATE TABLE `UserSalt` (
  `id` bigint(20) NOT NULL,
  `salt_email` varchar(255) NOT NULL,
  `salt_password` varchar(255) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dump dei dati per la tabella `UserSalt`
--

INSERT INTO `UserSalt` (`id`, `salt_email`, `salt_password`, `user_id`) VALUES
(1, 'f97947c6afa1dd8cba0f78994dd857a5', '0760a60638374f25bffddc90a2d1ab0f', 1);

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `Password`
--
ALTER TABLE `Password`
  ADD PRIMARY KEY (`id`),
  ADD KEY `password_user_id_fk` (`user_id`);

--
-- Indici per le tabelle `Role`
--
ALTER TABLE `Role`
  ADD PRIMARY KEY (`id`),
  ADD KEY `role_user_id_fk` (`user_id`);

--
-- Indici per le tabelle `User`
--
ALTER TABLE `User`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indici per le tabelle `UserSalt`
--
ALTER TABLE `UserSalt`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `Password`
--
ALTER TABLE `Password`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `Role`
--
ALTER TABLE `Role`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT per la tabella `User`
--
ALTER TABLE `User`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT per la tabella `UserSalt`
--
ALTER TABLE `UserSalt`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `Password`
--
ALTER TABLE `Password`
  ADD CONSTRAINT `Password_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `Role`
--
ALTER TABLE `Role`
  ADD CONSTRAINT `Role_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Limiti per la tabella `UserSalt`
--
ALTER TABLE `UserSalt`
  ADD CONSTRAINT `UserSalt_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;


