-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: hostal
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

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

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hora_ingreso` time DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo_doc` varchar(50) NOT NULL,
  `numero_doc` varchar(50) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `procedencia` varchar(100) NOT NULL,
  `check_in` datetime DEFAULT NULL,
  `check_out` datetime DEFAULT NULL,
  `valor` decimal(10,2) NOT NULL,
  `observacion` text DEFAULT NULL,
  `habitacion_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `habitacion_id` (`habitacion_id`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`habitacion_id`) REFERENCES `habitaciones` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (32,'22:22:00','ivan niño','C.c','1095830951','3102048686','VELEZ','2025-08-11 22:22:00','2025-08-12 10:17:54',40000.00,'',1),(33,'10:20:00','GUILLERMO ARIZA ','C.c','13956154','3506378124','VELEZ ','2025-08-12 10:20:00','2025-08-12 13:00:00',40000.00,'RATO PAREJA ',23),(36,'10:59:00','jaime ariza mateus','C.c','17044018','3212037811','bogota','2025-08-12 10:59:00','2025-08-13 13:00:00',40000.00,'',14),(37,'15:12:00','jhon delgado ','C.c','91112265','3212299294','bmanga ','2025-08-12 15:12:00','2025-08-14 13:00:00',800000.00,'sale el jueves ',15),(40,'18:14:00','erika taita','C.c','1052414598','3142462549','duitama','2025-08-12 18:14:00','2025-08-13 13:00:00',40000.00,'',2),(41,'18:29:00','catalina echevarria muñoz','C.c','1214714954','3219872060','medellin ','2025-08-12 18:29:00','2025-08-13 13:00:00',70000.00,'',11),(42,'18:29:00','david arango','C.c','1026149135','32119872060','medellin ','2025-08-12 18:29:00','2025-08-13 13:00:00',70000.00,'',11),(43,'19:14:00','JORGE ALBEIRO','C.c','91133280','3167442029','VELEZ','2025-08-12 19:14:00','2025-08-13 13:00:00',400000.00,'',18),(44,'09:16:00','OSWALDO DE JESU POSADA MEJIA','C.c','91070843','3212303679','SNAGIL','2025-08-11 09:16:00','2025-09-11 13:00:00',380000.00,'PAGA MES ANTICIPADO',25),(45,'09:22:00','WILSON GALEANO','C.c','XXXX','3158608814','bogota','2025-07-22 09:22:00','2025-08-22 13:00:00',380000.00,'MENSUALIDAD',24),(46,'09:30:00',' CARLOS IVAN MARTINES ALVARODO','C.c','91178571','3152131540','VELEZCC','2025-07-20 09:30:00','2025-08-20 13:00:00',420000.00,'MENSUALIDAD',29),(47,'09:32:00','TATIANA PIÑA','C.c','1017197633','3107985198','GUEBSA','2025-06-30 09:32:00','2025-07-30 13:00:00',450000.00,'MENSUALIDAD',1),(48,'09:35:00','TATIANA PIÑA','C.c','1017197633','3107985198','GUEBSA','2025-07-30 09:35:00','2025-07-30 13:00:00',450000.00,'MENSUALIDAD',31),(49,'10:09:00','FAIBER AMAYA MANZANO','C.c','88285245','3104127168','bucaramanga','2025-08-11 10:09:00','2025-08-13 10:11:40',420000.00,'MENSUALIDAD',1),(50,'10:10:00','FAIBER AMAYA MANZANO','C.c','88285245','3104127168','bucaramanga','2025-08-11 10:10:00','2025-08-13 10:27:41',420000.00,'',3),(51,'10:12:00','FAIBER AMAYA MANZANO','C.c','88285245','3104127168','bucaramanga','2025-08-11 10:12:00','2025-09-11 13:00:00',420000.00,'MENSUALIDAD',17),(52,'10:15:00','RODOLFO LOPEZ','C.c','80771601','3153544168','bucaramanga','2025-07-21 10:15:00','2025-08-21 13:00:00',420000.00,'MENSUALIDAD',1),(53,'10:18:00','RODOLFO LOPEZ','C.c','80771601','3153544168','bucaramanga','2025-07-21 10:18:00','2025-08-21 13:00:00',420000.00,'MENSUALIDAD',12),(54,'10:22:00','TATIANA PIÑA','C.c','1017197633','3107985198 PEND AGOS','GUEBSA','2025-07-30 10:22:00','2025-08-30 13:00:00',450000.00,'MENSUALIDAD DEBE AGOSTO',31),(55,'10:28:00','PERONAL','C.c','XXXX','XXXX','XXXX','2025-08-01 10:28:00','2025-08-30 13:00:00',0.00,'HABITACION DE DESCANSO',3);
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `habitaciones`
--

DROP TABLE IF EXISTS `habitaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `habitaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `numero` varchar(10) NOT NULL,
  `estado` enum('libre','ocupada','reservado','mantenimiento') NOT NULL,
  `descripcion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `habitaciones`
--

LOCK TABLES `habitaciones` WRITE;
/*!40000 ALTER TABLE `habitaciones` DISABLE KEYS */;
INSERT INTO `habitaciones` VALUES (1,'102','libre','sencilla'),(2,'103','libre','sencilla'),(3,'104','libre','sencilla'),(4,'105','libre','doble'),(5,'106','mantenimiento','doble'),(6,'107','mantenimiento','doble'),(7,'108','libre','sencilla'),(8,'109','libre','sencilla'),(9,'202','libre','doble'),(10,'203','libre','sencilla'),(11,'204','libre','sencilla'),(12,'205','libre','sencilla'),(13,'206','libre','sencilla'),(14,'207','libre','sencilla'),(15,'208','libre','sencilla'),(16,'209','libre','doble'),(17,'210','libre','sencilla'),(18,'211','libre','sencilla'),(19,'212','libre','sencilla'),(20,'301','libre','doble'),(21,'302','libre','sencilla'),(22,'303','libre','sencilla'),(23,'304','libre','sencilla'),(24,'305','libre','sencilla'),(25,'306','libre','sencilla'),(26,'307','libre','sencilla'),(27,'401','libre','doble'),(28,'402','libre','sencilla'),(29,'403','libre','sencilla'),(30,'404','libre','sencilla'),(31,'405','libre','sencilla');
/*!40000 ALTER TABLE `habitaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `huespedes`
--

DROP TABLE IF EXISTS `huespedes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `huespedes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `hora_ingreso` time NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo_doc` varchar(50) NOT NULL,
  `numero_doc` varchar(50) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `procedencia` varchar(100) NOT NULL,
  `check_in` date NOT NULL,
  `check_out` date NOT NULL,
  `valor` decimal(10,2) NOT NULL,
  `observacion` text DEFAULT NULL,
  `habitacion_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `habitacion_id` (`habitacion_id`),
  CONSTRAINT `huespedes_ibfk_1` FOREIGN KEY (`habitacion_id`) REFERENCES `habitaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `huespedes`
--

LOCK TABLES `huespedes` WRITE;
/*!40000 ALTER TABLE `huespedes` DISABLE KEYS */;
/*!40000 ALTER TABLE `huespedes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-13 19:14:24
