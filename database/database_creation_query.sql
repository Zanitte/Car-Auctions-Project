CREATE DATABASE IF NOT EXISTS `database` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `database`;

-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
-- Host: localhost    Database: database
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Table structure for table `accounts`
DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `id_user` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `password` varchar(45) DEFAULT NULL,
  `question` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_user`),
  KEY `email` (`email`),
  KEY `id_user` (`id_user`),
  KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `car_listings`
DROP TABLE IF EXISTS `car_listings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `car_listings` (
  `make` varchar(45) DEFAULT NULL,
  `model` varchar(45) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `price` int DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `image_path` text,
  `start_date` datetime(6) DEFAULT NULL,
  `listing_id` int NOT NULL AUTO_INCREMENT,
  `highest_bidder` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `id_user` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`listing_id`),
  KEY `idx_make_model_year` (`make`,`model`,`year`),
  KEY `listing_id` (`listing_id`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `bids`
DROP TABLE IF EXISTS `bids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bids` (
  `id` int NOT NULL AUTO_INCREMENT,
  `make` varchar(30) DEFAULT NULL,
  `model` varchar(30) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `bidder_email` varchar(40) DEFAULT NULL,
  `bid_amount` int DEFAULT NULL,
  `bid_timestamp` datetime DEFAULT NULL,
  `listing_id` int DEFAULT NULL,
  `bidder_username` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bids_ibfk_1` (`make`,`model`,`year`),
  CONSTRAINT `bids_ibfk_1` FOREIGN KEY (`make`, `model`, `year`) REFERENCES `car_listings` (`make`, `model`, `year`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `comments`
DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id_comment` int NOT NULL AUTO_INCREMENT,
  `listing_id` int NOT NULL,
  `username` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `comment_text` text NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_comment`),
  KEY `listing_id` (`listing_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`listing_id`) REFERENCES `car_listings` (`listing_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `documents`
DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `documents_id` int NOT NULL AUTO_INCREMENT,
  `images` text,
  `listing_id` int DEFAULT NULL,
  PRIMARY KEY (`documents_id`),
  KEY `listing_id` (`listing_id`) /*!80000 INVISIBLE */,
  CONSTRAINT `fk_documents_listing_id` FOREIGN KEY (`listing_id`) REFERENCES `car_listings` (`listing_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `user_address`
DROP TABLE IF EXISTS `user_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_address` (
  `id_user` int NOT NULL,
  `city` varchar(45) DEFAULT NULL,
  `street` varchar(45) DEFAULT NULL,
  `number_h` int DEFAULT NULL,
  PRIMARY KEY (`id_user`),
  CONSTRAINT `id_user` FOREIGN KEY (`id_user`) REFERENCES `accounts` (`id_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `payment_method`
DROP TABLE IF EXISTS `payment_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_method` (
  `id_user` int NOT NULL,
  `bank` varchar(45) DEFAULT NULL,
  `credit_card_number` varchar(45) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `cvv` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_user`),
  CONSTRAINT `fk_payment_method_user_address` FOREIGN KEY (`id_user`) REFERENCES `user_address` (`id_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Insert data for table `accounts`
LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (23,'Zanitte','edyzanitte@yahoo.com','12345','edi'),(24,'Polo','polok@gmail.com','1234','george'),(25,'zont','edycoupe@gmail.com','1234','edi'),(26,'Kont','edic@gmail.com','1234','edi');
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

-- Insert data for table `car_listings`
LOCK TABLES `car_listings` WRITE;
/*!40000 ALTER TABLE `car_listings` DISABLE KEYS */;
INSERT INTO `car_listings` VALUES ('Chevrolet','Camaro',2001,1500,'Masina se afla intr-o stare decenta',NULL,'2024-07-10 21:20:59.410167',93,'Polo','edyzanitte@yahoo.com',23,23);
/*!40000 ALTER TABLE `car_listings` ENABLE KEYS */;
UNLOCK TABLES;

-- Insert data for table `bids`
LOCK TABLES `bids` WRITE;
/*!40000 ALTER TABLE `bids` DISABLE KEYS */;
INSERT INTO `bids` VALUES (91, 'Chevrolet', 'Camaro', 2001, 'bidder@example.com', 1600, '2024-07-11 14:30:00', 93, 'Bidder1');
/*!40000 ALTER TABLE `bids` ENABLE KEYS */;
UNLOCK TABLES;

-- Insert data for table `comments`
LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (29, 93, 'user1', 'user1@example.com', 'Nice car!', '2024-07-12 10:00:00');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

-- Insert data for table `documents`
LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES (23, 'image1.jpg,image2.jpg', 93);
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;

-- Insert data for table `user_address`
LOCK TABLES `user_address` WRITE;
/*!40000 ALTER TABLE `user_address` DISABLE KEYS */;
INSERT INTO `user_address` VALUES (23, 'City1', 'Street1', 1);
/*!40000 ALTER TABLE `user_address` ENABLE KEYS */;
UNLOCK TABLES;

-- Insert data for table `payment_method`
LOCK TABLES `payment_method` WRITE;
/*!40000 ALTER TABLE `payment_method` DISABLE KEYS */;
INSERT INTO `payment_method` VALUES (23, 'Bank1', '1234567890123456', '2024-12-31', '123');
/*!40000 ALTER TABLE `payment_method` ENABLE KEYS */;
UNLOCK TABLES;
