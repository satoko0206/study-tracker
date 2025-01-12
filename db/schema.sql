-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- ホスト: 127.0.0.1
-- 生成日時: 2025-01-12 07:53:38
-- サーバのバージョン： 10.4.32-MariaDB
-- PHP のバージョン: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- データベース: `sample`
--

-- --------------------------------------------------------

--
-- テーブルの構造 `study_records`
--

CREATE TABLE `study_records` (
  `id` int(11) NOT NULL,
  `user_email` varchar(255) NOT NULL,
  `category` varchar(100) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `study_date` date NOT NULL,
  `study_time` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- テーブルのデータのダンプ `study_records`
--

INSERT INTO `study_records` (`id`, `user_email`, `category`, `start_time`, `end_time`, `study_date`, `study_time`) VALUES
(22, 'ok@ok', 'a', '2024-12-18 00:00:00', '2024-12-18 01:08:00', '2024-12-18', 68),
(25, 'ok@ok', 'a', '2024-12-16 13:04:00', '2024-12-16 13:19:00', '2024-12-16', 15),
(26, 'ok@ok', 'a', '2024-12-18 14:27:00', '2024-12-18 14:30:00', '2024-12-18', 3);

-- --------------------------------------------------------

--
-- テーブルの構造 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL DEFAULT '',
  `passwd` varchar(255) NOT NULL,
  `tel` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `admin` int(1) DEFAULT NULL,
  `create_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_login` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- テーブルのデータのダンプ `users`
--

INSERT INTO `users` (`id`, `email`, `passwd`, `tel`, `name`, `admin`, `create_at`, `last_login`) VALUES
(1, 'koki.ohsato.5b@stu.hosei.ac.jp', 'scrypt:32768:8:1$1IMn5ispw0KF52XS$5fc184cc8ddbd7c573c02e4539745cb7a466aaa6dbee280b62e2899e3c43c9103f125d6e5d543c3ea565fcf53c00580ff2e1b512d3197dd7c2af855c7b6edf71', '1234567890', '大里恒貴', 1, '2024-12-17 13:41:43', '2025-01-12 15:48:18'),
(9, 'ok@ok', 'scrypt:32768:8:1$joI0kQof0VTno65q$dd6632a46669caf287802ced2fb5dfe866f81bcc14e6bb36de65981769a071c07417cd77baafc00f37aa498471adf3f371de4ee0274e9c0313858b547ebef7d9', '1234567890', '特別枠', NULL, '2024-12-17 16:07:51', '2025-01-12 15:48:46');

--
-- ダンプしたテーブルのインデックス
--

--
-- テーブルのインデックス `study_records`
--
ALTER TABLE `study_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_user_email` (`user_email`);

--
-- テーブルのインデックス `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `admin` (`admin`);

--
-- ダンプしたテーブルの AUTO_INCREMENT
--

--
-- テーブルの AUTO_INCREMENT `study_records`
--
ALTER TABLE `study_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- テーブルの AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- ダンプしたテーブルの制約
--

--
-- テーブルの制約 `study_records`
--
ALTER TABLE `study_records`
  ADD CONSTRAINT `fk_user_email` FOREIGN KEY (`user_email`) REFERENCES `users` (`email`) ON DELETE CASCADE,
  ADD CONSTRAINT `study_records_ibfk_1` FOREIGN KEY (`user_email`) REFERENCES `users` (`email`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
