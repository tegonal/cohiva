/*M!999999\- enable the sandbox mode */
-- MariaDB dump 10.19  Distrib 10.5.29-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: cohiva-demo_django
-- ------------------------------------------------------
-- Server version	10.5.29-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (2,'Editors');
INSERT INTO `auth_group` VALUES (3,'Geschäftsstelle');
INSERT INTO `auth_group` VALUES (1,'Moderators');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=185 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (2,1,1);
INSERT INTO `auth_group_permissions` VALUES (6,1,2);
INSERT INTO `auth_group_permissions` VALUES (7,1,3);
INSERT INTO `auth_group_permissions` VALUES (8,1,4);
INSERT INTO `auth_group_permissions` VALUES (10,1,5);
INSERT INTO `auth_group_permissions` VALUES (15,1,6);
INSERT INTO `auth_group_permissions` VALUES (16,1,7);
INSERT INTO `auth_group_permissions` VALUES (14,1,8);
INSERT INTO `auth_group_permissions` VALUES (18,1,9);
INSERT INTO `auth_group_permissions` VALUES (1,2,1);
INSERT INTO `auth_group_permissions` VALUES (3,2,2);
INSERT INTO `auth_group_permissions` VALUES (4,2,3);
INSERT INTO `auth_group_permissions` VALUES (5,2,4);
INSERT INTO `auth_group_permissions` VALUES (9,2,5);
INSERT INTO `auth_group_permissions` VALUES (12,2,6);
INSERT INTO `auth_group_permissions` VALUES (13,2,7);
INSERT INTO `auth_group_permissions` VALUES (11,2,8);
INSERT INTO `auth_group_permissions` VALUES (17,2,9);
INSERT INTO `auth_group_permissions` VALUES (19,3,10);
INSERT INTO `auth_group_permissions` VALUES (20,3,11);
INSERT INTO `auth_group_permissions` VALUES (21,3,12);
INSERT INTO `auth_group_permissions` VALUES (22,3,13);
INSERT INTO `auth_group_permissions` VALUES (23,3,14);
INSERT INTO `auth_group_permissions` VALUES (24,3,15);
INSERT INTO `auth_group_permissions` VALUES (25,3,16);
INSERT INTO `auth_group_permissions` VALUES (26,3,17);
INSERT INTO `auth_group_permissions` VALUES (27,3,18);
INSERT INTO `auth_group_permissions` VALUES (28,3,19);
INSERT INTO `auth_group_permissions` VALUES (34,3,27);
INSERT INTO `auth_group_permissions` VALUES (36,3,30);
INSERT INTO `auth_group_permissions` VALUES (37,3,31);
INSERT INTO `auth_group_permissions` VALUES (38,3,32);
INSERT INTO `auth_group_permissions` VALUES (39,3,33);
INSERT INTO `auth_group_permissions` VALUES (40,3,34);
INSERT INTO `auth_group_permissions` VALUES (41,3,35);
INSERT INTO `auth_group_permissions` VALUES (42,3,36);
INSERT INTO `auth_group_permissions` VALUES (43,3,37);
INSERT INTO `auth_group_permissions` VALUES (56,3,51);
INSERT INTO `auth_group_permissions` VALUES (57,3,52);
INSERT INTO `auth_group_permissions` VALUES (58,3,53);
INSERT INTO `auth_group_permissions` VALUES (59,3,54);
INSERT INTO `auth_group_permissions` VALUES (60,3,55);
INSERT INTO `auth_group_permissions` VALUES (63,3,58);
INSERT INTO `auth_group_permissions` VALUES (64,3,59);
INSERT INTO `auth_group_permissions` VALUES (65,3,60);
INSERT INTO `auth_group_permissions` VALUES (66,3,61);
INSERT INTO `auth_group_permissions` VALUES (67,3,62);
INSERT INTO `auth_group_permissions` VALUES (68,3,63);
INSERT INTO `auth_group_permissions` VALUES (69,3,64);
INSERT INTO `auth_group_permissions` VALUES (70,3,65);
INSERT INTO `auth_group_permissions` VALUES (71,3,66);
INSERT INTO `auth_group_permissions` VALUES (72,3,67);
INSERT INTO `auth_group_permissions` VALUES (73,3,68);
INSERT INTO `auth_group_permissions` VALUES (74,3,69);
INSERT INTO `auth_group_permissions` VALUES (75,3,70);
INSERT INTO `auth_group_permissions` VALUES (76,3,71);
INSERT INTO `auth_group_permissions` VALUES (77,3,72);
INSERT INTO `auth_group_permissions` VALUES (78,3,73);
INSERT INTO `auth_group_permissions` VALUES (79,3,74);
INSERT INTO `auth_group_permissions` VALUES (80,3,75);
INSERT INTO `auth_group_permissions` VALUES (81,3,76);
INSERT INTO `auth_group_permissions` VALUES (82,3,77);
INSERT INTO `auth_group_permissions` VALUES (83,3,78);
INSERT INTO `auth_group_permissions` VALUES (84,3,79);
INSERT INTO `auth_group_permissions` VALUES (89,3,89);
INSERT INTO `auth_group_permissions` VALUES (90,3,90);
INSERT INTO `auth_group_permissions` VALUES (91,3,91);
INSERT INTO `auth_group_permissions` VALUES (92,3,92);
INSERT INTO `auth_group_permissions` VALUES (93,3,93);
INSERT INTO `auth_group_permissions` VALUES (94,3,94);
INSERT INTO `auth_group_permissions` VALUES (95,3,95);
INSERT INTO `auth_group_permissions` VALUES (96,3,96);
INSERT INTO `auth_group_permissions` VALUES (97,3,97);
INSERT INTO `auth_group_permissions` VALUES (98,3,98);
INSERT INTO `auth_group_permissions` VALUES (99,3,99);
INSERT INTO `auth_group_permissions` VALUES (100,3,100);
INSERT INTO `auth_group_permissions` VALUES (105,3,105);
INSERT INTO `auth_group_permissions` VALUES (106,3,106);
INSERT INTO `auth_group_permissions` VALUES (107,3,107);
INSERT INTO `auth_group_permissions` VALUES (108,3,108);
INSERT INTO `auth_group_permissions` VALUES (109,3,109);
INSERT INTO `auth_group_permissions` VALUES (110,3,110);
INSERT INTO `auth_group_permissions` VALUES (111,3,111);
INSERT INTO `auth_group_permissions` VALUES (112,3,112);
INSERT INTO `auth_group_permissions` VALUES (117,3,117);
INSERT INTO `auth_group_permissions` VALUES (118,3,118);
INSERT INTO `auth_group_permissions` VALUES (119,3,119);
INSERT INTO `auth_group_permissions` VALUES (120,3,120);
INSERT INTO `auth_group_permissions` VALUES (121,3,161);
INSERT INTO `auth_group_permissions` VALUES (122,3,162);
INSERT INTO `auth_group_permissions` VALUES (123,3,163);
INSERT INTO `auth_group_permissions` VALUES (124,3,164);
INSERT INTO `auth_group_permissions` VALUES (125,3,165);
INSERT INTO `auth_group_permissions` VALUES (126,3,166);
INSERT INTO `auth_group_permissions` VALUES (127,3,167);
INSERT INTO `auth_group_permissions` VALUES (128,3,168);
INSERT INTO `auth_group_permissions` VALUES (129,3,169);
INSERT INTO `auth_group_permissions` VALUES (130,3,170);
INSERT INTO `auth_group_permissions` VALUES (131,3,171);
INSERT INTO `auth_group_permissions` VALUES (132,3,172);
INSERT INTO `auth_group_permissions` VALUES (133,3,173);
INSERT INTO `auth_group_permissions` VALUES (134,3,174);
INSERT INTO `auth_group_permissions` VALUES (135,3,175);
INSERT INTO `auth_group_permissions` VALUES (136,3,176);
INSERT INTO `auth_group_permissions` VALUES (137,3,177);
INSERT INTO `auth_group_permissions` VALUES (138,3,182);
INSERT INTO `auth_group_permissions` VALUES (139,3,183);
INSERT INTO `auth_group_permissions` VALUES (140,3,184);
INSERT INTO `auth_group_permissions` VALUES (141,3,185);
INSERT INTO `auth_group_permissions` VALUES (146,3,372);
INSERT INTO `auth_group_permissions` VALUES (147,3,373);
INSERT INTO `auth_group_permissions` VALUES (148,3,374);
INSERT INTO `auth_group_permissions` VALUES (149,3,375);
INSERT INTO `auth_group_permissions` VALUES (150,3,376);
INSERT INTO `auth_group_permissions` VALUES (151,3,377);
INSERT INTO `auth_group_permissions` VALUES (152,3,378);
INSERT INTO `auth_group_permissions` VALUES (153,3,379);
INSERT INTO `auth_group_permissions` VALUES (154,3,380);
INSERT INTO `auth_group_permissions` VALUES (155,3,381);
INSERT INTO `auth_group_permissions` VALUES (156,3,382);
INSERT INTO `auth_group_permissions` VALUES (157,3,383);
INSERT INTO `auth_group_permissions` VALUES (158,3,384);
INSERT INTO `auth_group_permissions` VALUES (159,3,385);
INSERT INTO `auth_group_permissions` VALUES (160,3,386);
INSERT INTO `auth_group_permissions` VALUES (161,3,387);
INSERT INTO `auth_group_permissions` VALUES (162,3,388);
INSERT INTO `auth_group_permissions` VALUES (163,3,389);
INSERT INTO `auth_group_permissions` VALUES (164,3,390);
INSERT INTO `auth_group_permissions` VALUES (165,3,391);
INSERT INTO `auth_group_permissions` VALUES (166,3,392);
INSERT INTO `auth_group_permissions` VALUES (167,3,393);
INSERT INTO `auth_group_permissions` VALUES (168,3,394);
INSERT INTO `auth_group_permissions` VALUES (169,3,395);
INSERT INTO `auth_group_permissions` VALUES (170,3,396);
INSERT INTO `auth_group_permissions` VALUES (171,3,397);
INSERT INTO `auth_group_permissions` VALUES (172,3,398);
INSERT INTO `auth_group_permissions` VALUES (173,3,399);
INSERT INTO `auth_group_permissions` VALUES (174,3,400);
INSERT INTO `auth_group_permissions` VALUES (175,3,401);
INSERT INTO `auth_group_permissions` VALUES (176,3,402);
INSERT INTO `auth_group_permissions` VALUES (177,3,403);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=504 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can access Wagtail admin',3,'access_admin');
INSERT INTO `auth_permission` VALUES (2,'Can add document',4,'add_document');
INSERT INTO `auth_permission` VALUES (3,'Can change document',4,'change_document');
INSERT INTO `auth_permission` VALUES (4,'Can delete document',4,'delete_document');
INSERT INTO `auth_permission` VALUES (5,'Can choose document',4,'choose_document');
INSERT INTO `auth_permission` VALUES (6,'Can add image',5,'add_image');
INSERT INTO `auth_permission` VALUES (7,'Can change image',5,'change_image');
INSERT INTO `auth_permission` VALUES (8,'Can delete image',5,'delete_image');
INSERT INTO `auth_permission` VALUES (9,'Can choose image',5,'choose_image');
INSERT INTO `auth_permission` VALUES (10,'Can add Adresse',6,'add_address');
INSERT INTO `auth_permission` VALUES (11,'Can change Adresse',6,'change_address');
INSERT INTO `auth_permission` VALUES (12,'Can delete Adresse',6,'delete_address');
INSERT INTO `auth_permission` VALUES (13,'Can view Adresse',6,'view_address');
INSERT INTO `auth_permission` VALUES (14,'Can add Mitglied',7,'add_member');
INSERT INTO `auth_permission` VALUES (15,'Can change Mitglied',7,'change_member');
INSERT INTO `auth_permission` VALUES (16,'Can delete Mitglied',7,'delete_member');
INSERT INTO `auth_permission` VALUES (17,'Can view Mitglied',7,'view_member');
INSERT INTO `auth_permission` VALUES (18,'Can see members',7,'canview_member');
INSERT INTO `auth_permission` VALUES (19,'Can see member overview',7,'canview_member_overview');
INSERT INTO `auth_permission` VALUES (20,'Can see member mailinglist information',7,'canview_member_mailinglists');
INSERT INTO `auth_permission` VALUES (21,'Can see billing/payment information',7,'canview_billing');
INSERT INTO `auth_permission` VALUES (22,'Kann Zahlungen überprüfen',7,'check_payments');
INSERT INTO `auth_permission` VALUES (23,'Kann Zahlungen erfassen',7,'transaction');
INSERT INTO `auth_permission` VALUES (24,'Kann Rechnungen erstellen und bezahlte erfassen',7,'transaction_invoice');
INSERT INTO `auth_permission` VALUES (25,'Can import data',7,'admin_import');
INSERT INTO `auth_permission` VALUES (26,'Can run admin maintenance tasks',7,'admin_maintenance');
INSERT INTO `auth_permission` VALUES (27,'Can send emails to members/users',7,'send_mail');
INSERT INTO `auth_permission` VALUES (28,'Kann neue Beitritte bestätigen',7,'send_newmembers');
INSERT INTO `auth_permission` VALUES (29,'Kann Gegensprechanlage (ADIT) Daten sehen/bearbeiten',7,'adit');
INSERT INTO `auth_permission` VALUES (30,'Can add Mitglieder Attribut',8,'add_memberattribute');
INSERT INTO `auth_permission` VALUES (31,'Can change Mitglieder Attribut',8,'change_memberattribute');
INSERT INTO `auth_permission` VALUES (32,'Can delete Mitglieder Attribut',8,'delete_memberattribute');
INSERT INTO `auth_permission` VALUES (33,'Can view Mitglieder Attribut',8,'view_memberattribute');
INSERT INTO `auth_permission` VALUES (34,'Can add Mitglieder Attribut Typ',9,'add_memberattributetype');
INSERT INTO `auth_permission` VALUES (35,'Can change Mitglieder Attribut Typ',9,'change_memberattributetype');
INSERT INTO `auth_permission` VALUES (36,'Can delete Mitglieder Attribut Typ',9,'delete_memberattributetype');
INSERT INTO `auth_permission` VALUES (37,'Can view Mitglieder Attribut Typ',9,'view_memberattributetype');
INSERT INTO `auth_permission` VALUES (38,'Can add Beteiligung',10,'add_share');
INSERT INTO `auth_permission` VALUES (39,'Can change Beteiligung',10,'change_share');
INSERT INTO `auth_permission` VALUES (40,'Can delete Beteiligung',10,'delete_share');
INSERT INTO `auth_permission` VALUES (41,'Can view Beteiligung',10,'view_share');
INSERT INTO `auth_permission` VALUES (42,'Can view shares',10,'canview_share');
INSERT INTO `auth_permission` VALUES (43,'Can see share overview',10,'canview_share_overview');
INSERT INTO `auth_permission` VALUES (44,'Kann Betiligungen bestätigen',10,'confirm_share');
INSERT INTO `auth_permission` VALUES (45,'Kann Zins-/Kontoauszüge erstellen und Zinsen anpassen',10,'share_interest_statments');
INSERT INTO `auth_permission` VALUES (46,'Kann Mailing zu Beteiligungen erstellen',10,'share_mailing');
INSERT INTO `auth_permission` VALUES (47,'Can add Beteiligungstyp',11,'add_sharetype');
INSERT INTO `auth_permission` VALUES (48,'Can change Beteiligungstyp',11,'change_sharetype');
INSERT INTO `auth_permission` VALUES (49,'Can delete Beteiligungstyp',11,'delete_sharetype');
INSERT INTO `auth_permission` VALUES (50,'Can view Beteiligungstyp',11,'view_sharetype');
INSERT INTO `auth_permission` VALUES (51,'Can add Dokument',12,'add_document');
INSERT INTO `auth_permission` VALUES (52,'Can change Dokument',12,'change_document');
INSERT INTO `auth_permission` VALUES (53,'Can delete Dokument',12,'delete_document');
INSERT INTO `auth_permission` VALUES (54,'Can view Dokument',12,'view_document');
INSERT INTO `auth_permission` VALUES (55,'Can regenerate documents',12,'regenerate_document');
INSERT INTO `auth_permission` VALUES (56,'Kann ODT in PDFs umwandeln',12,'tools_odt2pdf');
INSERT INTO `auth_permission` VALUES (57,'Kann PDFs frankieren',12,'tools_webstamp');
INSERT INTO `auth_permission` VALUES (58,'Can add Dokumenttyp',13,'add_documenttype');
INSERT INTO `auth_permission` VALUES (59,'Can change Dokumenttyp',13,'change_documenttype');
INSERT INTO `auth_permission` VALUES (60,'Can delete Dokumenttyp',13,'delete_documenttype');
INSERT INTO `auth_permission` VALUES (61,'Can view Dokumenttyp',13,'view_documenttype');
INSERT INTO `auth_permission` VALUES (62,'Can add Anmeldung',14,'add_registration');
INSERT INTO `auth_permission` VALUES (63,'Can change Anmeldung',14,'change_registration');
INSERT INTO `auth_permission` VALUES (64,'Can delete Anmeldung',14,'delete_registration');
INSERT INTO `auth_permission` VALUES (65,'Can view Anmeldung',14,'view_registration');
INSERT INTO `auth_permission` VALUES (66,'Can add Anmeldung-Anlass',15,'add_registrationevent');
INSERT INTO `auth_permission` VALUES (67,'Can change Anmeldung-Anlass',15,'change_registrationevent');
INSERT INTO `auth_permission` VALUES (68,'Can delete Anmeldung-Anlass',15,'delete_registrationevent');
INSERT INTO `auth_permission` VALUES (69,'Can view Anmeldung-Anlass',15,'view_registrationevent');
INSERT INTO `auth_permission` VALUES (70,'Can add Anmeldung-Termin',16,'add_registrationslot');
INSERT INTO `auth_permission` VALUES (71,'Can change Anmeldung-Termin',16,'change_registrationslot');
INSERT INTO `auth_permission` VALUES (72,'Can delete Anmeldung-Termin',16,'delete_registrationslot');
INSERT INTO `auth_permission` VALUES (73,'Can view Anmeldung-Termin',16,'view_registrationslot');
INSERT INTO `auth_permission` VALUES (74,'Can add Vertrag',17,'add_contract');
INSERT INTO `auth_permission` VALUES (75,'Can change Vertrag',17,'change_contract');
INSERT INTO `auth_permission` VALUES (76,'Can delete Vertrag',17,'delete_contract');
INSERT INTO `auth_permission` VALUES (77,'Can view Vertrag',17,'view_contract');
INSERT INTO `auth_permission` VALUES (78,'Kann Mietverträge erstellen, NK-Abrechung, Pflichtanteile überprüfen',17,'rental_contracts');
INSERT INTO `auth_permission` VALUES (79,'Kann Mieter-/Objektespiegel erstellen und Mietobjekt-Dokumente erstellen',17,'rental_objects');
INSERT INTO `auth_permission` VALUES (80,'Kann Versand an Mieter*innen erstellen',17,'send_mail_rental');
INSERT INTO `auth_permission` VALUES (81,'Can add Rechnung',18,'add_invoice');
INSERT INTO `auth_permission` VALUES (82,'Can change Rechnung',18,'change_invoice');
INSERT INTO `auth_permission` VALUES (83,'Can delete Rechnung',18,'delete_invoice');
INSERT INTO `auth_permission` VALUES (84,'Can view Rechnung',18,'view_invoice');
INSERT INTO `auth_permission` VALUES (85,'Can add lookup table',19,'add_lookuptable');
INSERT INTO `auth_permission` VALUES (86,'Can change lookup table',19,'change_lookuptable');
INSERT INTO `auth_permission` VALUES (87,'Can delete lookup table',19,'delete_lookuptable');
INSERT INTO `auth_permission` VALUES (88,'Can view lookup table',19,'view_lookuptable');
INSERT INTO `auth_permission` VALUES (89,'Can add Mietobjekt',20,'add_rentalunit');
INSERT INTO `auth_permission` VALUES (90,'Can change Mietobjekt',20,'change_rentalunit');
INSERT INTO `auth_permission` VALUES (91,'Can delete Mietobjekt',20,'delete_rentalunit');
INSERT INTO `auth_permission` VALUES (92,'Can view Mietobjekt',20,'view_rentalunit');
INSERT INTO `auth_permission` VALUES (93,'Can add Kind',21,'add_child');
INSERT INTO `auth_permission` VALUES (94,'Can change Kind',21,'change_child');
INSERT INTO `auth_permission` VALUES (95,'Can delete Kind',21,'delete_child');
INSERT INTO `auth_permission` VALUES (96,'Can view Kind',21,'view_child');
INSERT INTO `auth_permission` VALUES (97,'Can add Vorlage',22,'add_contenttemplate');
INSERT INTO `auth_permission` VALUES (98,'Can change Vorlage',22,'change_contenttemplate');
INSERT INTO `auth_permission` VALUES (99,'Can delete Vorlage',22,'delete_contenttemplate');
INSERT INTO `auth_permission` VALUES (100,'Can view Vorlage',22,'view_contenttemplate');
INSERT INTO `auth_permission` VALUES (101,'Can add Rechnungstyp',23,'add_invoicecategory');
INSERT INTO `auth_permission` VALUES (102,'Can change Rechnungstyp',23,'change_invoicecategory');
INSERT INTO `auth_permission` VALUES (103,'Can delete Rechnungstyp',23,'delete_invoicecategory');
INSERT INTO `auth_permission` VALUES (104,'Can view Rechnungstyp',23,'view_invoicecategory');
INSERT INTO `auth_permission` VALUES (105,'Can add Attribut',24,'add_genericattribute');
INSERT INTO `auth_permission` VALUES (106,'Can change Attribut',24,'change_genericattribute');
INSERT INTO `auth_permission` VALUES (107,'Can delete Attribut',24,'delete_genericattribute');
INSERT INTO `auth_permission` VALUES (108,'Can view Attribut',24,'view_genericattribute');
INSERT INTO `auth_permission` VALUES (109,'Can add Gebäude',25,'add_building');
INSERT INTO `auth_permission` VALUES (110,'Can change Gebäude',25,'change_building');
INSERT INTO `auth_permission` VALUES (111,'Can delete Gebäude',25,'delete_building');
INSERT INTO `auth_permission` VALUES (112,'Can view Gebäude',25,'view_building');
INSERT INTO `auth_permission` VALUES (113,'Can add Nutzer:in',26,'add_tenant');
INSERT INTO `auth_permission` VALUES (114,'Can change Nutzer:in',26,'change_tenant');
INSERT INTO `auth_permission` VALUES (115,'Can delete Nutzer:in',26,'delete_tenant');
INSERT INTO `auth_permission` VALUES (116,'Can view Nutzer:in',26,'view_tenant');
INSERT INTO `auth_permission` VALUES (117,'Can add Vorlagenoption',27,'add_contenttemplateoption');
INSERT INTO `auth_permission` VALUES (118,'Can change Vorlagenoption',27,'change_contenttemplateoption');
INSERT INTO `auth_permission` VALUES (119,'Can delete Vorlagenoption',27,'delete_contenttemplateoption');
INSERT INTO `auth_permission` VALUES (120,'Can view Vorlagenoption',27,'view_contenttemplateoption');
INSERT INTO `auth_permission` VALUES (121,'Can add log entry',28,'add_logentry');
INSERT INTO `auth_permission` VALUES (122,'Can change log entry',28,'change_logentry');
INSERT INTO `auth_permission` VALUES (123,'Can delete log entry',28,'delete_logentry');
INSERT INTO `auth_permission` VALUES (124,'Can view log entry',28,'view_logentry');
INSERT INTO `auth_permission` VALUES (125,'Can add permission',29,'add_permission');
INSERT INTO `auth_permission` VALUES (126,'Can change permission',29,'change_permission');
INSERT INTO `auth_permission` VALUES (127,'Can delete permission',29,'delete_permission');
INSERT INTO `auth_permission` VALUES (128,'Can view permission',29,'view_permission');
INSERT INTO `auth_permission` VALUES (129,'Can add group',30,'add_group');
INSERT INTO `auth_permission` VALUES (130,'Can change group',30,'change_group');
INSERT INTO `auth_permission` VALUES (131,'Can delete group',30,'delete_group');
INSERT INTO `auth_permission` VALUES (132,'Can view group',30,'view_group');
INSERT INTO `auth_permission` VALUES (133,'Can add user',31,'add_user');
INSERT INTO `auth_permission` VALUES (134,'Can change user',31,'change_user');
INSERT INTO `auth_permission` VALUES (135,'Can delete user',31,'delete_user');
INSERT INTO `auth_permission` VALUES (136,'Can view user',31,'view_user');
INSERT INTO `auth_permission` VALUES (137,'Can add content type',32,'add_contenttype');
INSERT INTO `auth_permission` VALUES (138,'Can change content type',32,'change_contenttype');
INSERT INTO `auth_permission` VALUES (139,'Can delete content type',32,'delete_contenttype');
INSERT INTO `auth_permission` VALUES (140,'Can view content type',32,'view_contenttype');
INSERT INTO `auth_permission` VALUES (141,'Can add session',33,'add_session');
INSERT INTO `auth_permission` VALUES (142,'Can change session',33,'change_session');
INSERT INTO `auth_permission` VALUES (143,'Can delete session',33,'delete_session');
INSERT INTO `auth_permission` VALUES (144,'Can view session',33,'view_session');
INSERT INTO `auth_permission` VALUES (145,'Can add site',34,'add_site');
INSERT INTO `auth_permission` VALUES (146,'Can change site',34,'change_site');
INSERT INTO `auth_permission` VALUES (147,'Can delete site',34,'delete_site');
INSERT INTO `auth_permission` VALUES (148,'Can view site',34,'view_site');
INSERT INTO `auth_permission` VALUES (149,'Can add source',35,'add_source');
INSERT INTO `auth_permission` VALUES (150,'Can change source',35,'change_source');
INSERT INTO `auth_permission` VALUES (151,'Can delete source',35,'delete_source');
INSERT INTO `auth_permission` VALUES (152,'Can view source',35,'view_source');
INSERT INTO `auth_permission` VALUES (153,'Can add thumbnail',36,'add_thumbnail');
INSERT INTO `auth_permission` VALUES (154,'Can change thumbnail',36,'change_thumbnail');
INSERT INTO `auth_permission` VALUES (155,'Can delete thumbnail',36,'delete_thumbnail');
INSERT INTO `auth_permission` VALUES (156,'Can view thumbnail',36,'view_thumbnail');
INSERT INTO `auth_permission` VALUES (157,'Can add thumbnail dimensions',37,'add_thumbnaildimensions');
INSERT INTO `auth_permission` VALUES (158,'Can change thumbnail dimensions',37,'change_thumbnaildimensions');
INSERT INTO `auth_permission` VALUES (159,'Can delete thumbnail dimensions',37,'delete_thumbnaildimensions');
INSERT INTO `auth_permission` VALUES (160,'Can view thumbnail dimensions',37,'view_thumbnaildimensions');
INSERT INTO `auth_permission` VALUES (161,'Can add clipboard',38,'add_clipboard');
INSERT INTO `auth_permission` VALUES (162,'Can change clipboard',38,'change_clipboard');
INSERT INTO `auth_permission` VALUES (163,'Can delete clipboard',38,'delete_clipboard');
INSERT INTO `auth_permission` VALUES (164,'Can view clipboard',38,'view_clipboard');
INSERT INTO `auth_permission` VALUES (165,'Can add clipboard item',39,'add_clipboarditem');
INSERT INTO `auth_permission` VALUES (166,'Can change clipboard item',39,'change_clipboarditem');
INSERT INTO `auth_permission` VALUES (167,'Can delete clipboard item',39,'delete_clipboarditem');
INSERT INTO `auth_permission` VALUES (168,'Can view clipboard item',39,'view_clipboarditem');
INSERT INTO `auth_permission` VALUES (169,'Can add file',40,'add_file');
INSERT INTO `auth_permission` VALUES (170,'Can change file',40,'change_file');
INSERT INTO `auth_permission` VALUES (171,'Can delete file',40,'delete_file');
INSERT INTO `auth_permission` VALUES (172,'Can view file',40,'view_file');
INSERT INTO `auth_permission` VALUES (173,'Can add Folder',41,'add_folder');
INSERT INTO `auth_permission` VALUES (174,'Can change Folder',41,'change_folder');
INSERT INTO `auth_permission` VALUES (175,'Can delete Folder',41,'delete_folder');
INSERT INTO `auth_permission` VALUES (176,'Can view Folder',41,'view_folder');
INSERT INTO `auth_permission` VALUES (177,'Can use directory listing',41,'can_use_directory_listing');
INSERT INTO `auth_permission` VALUES (178,'Can add folder permission',42,'add_folderpermission');
INSERT INTO `auth_permission` VALUES (179,'Can change folder permission',42,'change_folderpermission');
INSERT INTO `auth_permission` VALUES (180,'Can delete folder permission',42,'delete_folderpermission');
INSERT INTO `auth_permission` VALUES (181,'Can view folder permission',42,'view_folderpermission');
INSERT INTO `auth_permission` VALUES (182,'Can add image',43,'add_image');
INSERT INTO `auth_permission` VALUES (183,'Can change image',43,'change_image');
INSERT INTO `auth_permission` VALUES (184,'Can delete image',43,'delete_image');
INSERT INTO `auth_permission` VALUES (185,'Can view image',43,'view_image');
INSERT INTO `auth_permission` VALUES (186,'Can add thumbnail option',44,'add_thumbnailoption');
INSERT INTO `auth_permission` VALUES (187,'Can change thumbnail option',44,'change_thumbnailoption');
INSERT INTO `auth_permission` VALUES (188,'Can delete thumbnail option',44,'delete_thumbnailoption');
INSERT INTO `auth_permission` VALUES (189,'Can view thumbnail option',44,'view_thumbnailoption');
INSERT INTO `auth_permission` VALUES (190,'Can add Token',45,'add_token');
INSERT INTO `auth_permission` VALUES (191,'Can change Token',45,'change_token');
INSERT INTO `auth_permission` VALUES (192,'Can delete Token',45,'delete_token');
INSERT INTO `auth_permission` VALUES (193,'Can view Token',45,'view_token');
INSERT INTO `auth_permission` VALUES (194,'Can add token',46,'add_tokenproxy');
INSERT INTO `auth_permission` VALUES (195,'Can change token',46,'change_tokenproxy');
INSERT INTO `auth_permission` VALUES (196,'Can delete token',46,'delete_tokenproxy');
INSERT INTO `auth_permission` VALUES (197,'Can view token',46,'view_tokenproxy');
INSERT INTO `auth_permission` VALUES (198,'Can add form submission',47,'add_formsubmission');
INSERT INTO `auth_permission` VALUES (199,'Can change form submission',47,'change_formsubmission');
INSERT INTO `auth_permission` VALUES (200,'Can delete form submission',47,'delete_formsubmission');
INSERT INTO `auth_permission` VALUES (201,'Can view form submission',47,'view_formsubmission');
INSERT INTO `auth_permission` VALUES (202,'Can add redirect',48,'add_redirect');
INSERT INTO `auth_permission` VALUES (203,'Can change redirect',48,'change_redirect');
INSERT INTO `auth_permission` VALUES (204,'Can delete redirect',48,'delete_redirect');
INSERT INTO `auth_permission` VALUES (205,'Can view redirect',48,'view_redirect');
INSERT INTO `auth_permission` VALUES (206,'Can add embed',49,'add_embed');
INSERT INTO `auth_permission` VALUES (207,'Can change embed',49,'change_embed');
INSERT INTO `auth_permission` VALUES (208,'Can delete embed',49,'delete_embed');
INSERT INTO `auth_permission` VALUES (209,'Can view embed',49,'view_embed');
INSERT INTO `auth_permission` VALUES (210,'Can add user profile',50,'add_userprofile');
INSERT INTO `auth_permission` VALUES (211,'Can change user profile',50,'change_userprofile');
INSERT INTO `auth_permission` VALUES (212,'Can delete user profile',50,'delete_userprofile');
INSERT INTO `auth_permission` VALUES (213,'Can view user profile',50,'view_userprofile');
INSERT INTO `auth_permission` VALUES (214,'Can view document',4,'view_document');
INSERT INTO `auth_permission` VALUES (215,'Can add uploaded document',51,'add_uploadeddocument');
INSERT INTO `auth_permission` VALUES (216,'Can change uploaded document',51,'change_uploadeddocument');
INSERT INTO `auth_permission` VALUES (217,'Can delete uploaded document',51,'delete_uploadeddocument');
INSERT INTO `auth_permission` VALUES (218,'Can view uploaded document',51,'view_uploadeddocument');
INSERT INTO `auth_permission` VALUES (219,'Can view image',5,'view_image');
INSERT INTO `auth_permission` VALUES (220,'Can add rendition',52,'add_rendition');
INSERT INTO `auth_permission` VALUES (221,'Can change rendition',52,'change_rendition');
INSERT INTO `auth_permission` VALUES (222,'Can delete rendition',52,'delete_rendition');
INSERT INTO `auth_permission` VALUES (223,'Can view rendition',52,'view_rendition');
INSERT INTO `auth_permission` VALUES (224,'Can add uploaded image',53,'add_uploadedimage');
INSERT INTO `auth_permission` VALUES (225,'Can change uploaded image',53,'change_uploadedimage');
INSERT INTO `auth_permission` VALUES (226,'Can delete uploaded image',53,'delete_uploadedimage');
INSERT INTO `auth_permission` VALUES (227,'Can view uploaded image',53,'view_uploadedimage');
INSERT INTO `auth_permission` VALUES (228,'Can add query',54,'add_query');
INSERT INTO `auth_permission` VALUES (229,'Can change query',54,'change_query');
INSERT INTO `auth_permission` VALUES (230,'Can delete query',54,'delete_query');
INSERT INTO `auth_permission` VALUES (231,'Can view query',54,'view_query');
INSERT INTO `auth_permission` VALUES (232,'Can add Query Daily Hits',55,'add_querydailyhits');
INSERT INTO `auth_permission` VALUES (233,'Can change Query Daily Hits',55,'change_querydailyhits');
INSERT INTO `auth_permission` VALUES (234,'Can delete Query Daily Hits',55,'delete_querydailyhits');
INSERT INTO `auth_permission` VALUES (235,'Can view Query Daily Hits',55,'view_querydailyhits');
INSERT INTO `auth_permission` VALUES (236,'Can add page',1,'add_page');
INSERT INTO `auth_permission` VALUES (237,'Can change page',1,'change_page');
INSERT INTO `auth_permission` VALUES (238,'Can delete page',1,'delete_page');
INSERT INTO `auth_permission` VALUES (239,'Can view page',1,'view_page');
INSERT INTO `auth_permission` VALUES (240,'Can add group page permission',56,'add_grouppagepermission');
INSERT INTO `auth_permission` VALUES (241,'Can change group page permission',56,'change_grouppagepermission');
INSERT INTO `auth_permission` VALUES (242,'Can delete group page permission',56,'delete_grouppagepermission');
INSERT INTO `auth_permission` VALUES (243,'Can view group page permission',56,'view_grouppagepermission');
INSERT INTO `auth_permission` VALUES (244,'Can add page revision',57,'add_pagerevision');
INSERT INTO `auth_permission` VALUES (245,'Can change page revision',57,'change_pagerevision');
INSERT INTO `auth_permission` VALUES (246,'Can delete page revision',57,'delete_pagerevision');
INSERT INTO `auth_permission` VALUES (247,'Can view page revision',57,'view_pagerevision');
INSERT INTO `auth_permission` VALUES (248,'Can add page view restriction',58,'add_pageviewrestriction');
INSERT INTO `auth_permission` VALUES (249,'Can change page view restriction',58,'change_pageviewrestriction');
INSERT INTO `auth_permission` VALUES (250,'Can delete page view restriction',58,'delete_pageviewrestriction');
INSERT INTO `auth_permission` VALUES (251,'Can view page view restriction',58,'view_pageviewrestriction');
INSERT INTO `auth_permission` VALUES (252,'Can add site',59,'add_site');
INSERT INTO `auth_permission` VALUES (253,'Can change site',59,'change_site');
INSERT INTO `auth_permission` VALUES (254,'Can delete site',59,'delete_site');
INSERT INTO `auth_permission` VALUES (255,'Can view site',59,'view_site');
INSERT INTO `auth_permission` VALUES (256,'Can add collection',60,'add_collection');
INSERT INTO `auth_permission` VALUES (257,'Can change collection',60,'change_collection');
INSERT INTO `auth_permission` VALUES (258,'Can delete collection',60,'delete_collection');
INSERT INTO `auth_permission` VALUES (259,'Can view collection',60,'view_collection');
INSERT INTO `auth_permission` VALUES (260,'Can add group collection permission',61,'add_groupcollectionpermission');
INSERT INTO `auth_permission` VALUES (261,'Can change group collection permission',61,'change_groupcollectionpermission');
INSERT INTO `auth_permission` VALUES (262,'Can delete group collection permission',61,'delete_groupcollectionpermission');
INSERT INTO `auth_permission` VALUES (263,'Can view group collection permission',61,'view_groupcollectionpermission');
INSERT INTO `auth_permission` VALUES (264,'Can add collection view restriction',62,'add_collectionviewrestriction');
INSERT INTO `auth_permission` VALUES (265,'Can change collection view restriction',62,'change_collectionviewrestriction');
INSERT INTO `auth_permission` VALUES (266,'Can delete collection view restriction',62,'delete_collectionviewrestriction');
INSERT INTO `auth_permission` VALUES (267,'Can view collection view restriction',62,'view_collectionviewrestriction');
INSERT INTO `auth_permission` VALUES (268,'Can add task',63,'add_task');
INSERT INTO `auth_permission` VALUES (269,'Can change task',63,'change_task');
INSERT INTO `auth_permission` VALUES (270,'Can delete task',63,'delete_task');
INSERT INTO `auth_permission` VALUES (271,'Can view task',63,'view_task');
INSERT INTO `auth_permission` VALUES (272,'Can add Task state',64,'add_taskstate');
INSERT INTO `auth_permission` VALUES (273,'Can change Task state',64,'change_taskstate');
INSERT INTO `auth_permission` VALUES (274,'Can delete Task state',64,'delete_taskstate');
INSERT INTO `auth_permission` VALUES (275,'Can view Task state',64,'view_taskstate');
INSERT INTO `auth_permission` VALUES (276,'Can add workflow',65,'add_workflow');
INSERT INTO `auth_permission` VALUES (277,'Can change workflow',65,'change_workflow');
INSERT INTO `auth_permission` VALUES (278,'Can delete workflow',65,'delete_workflow');
INSERT INTO `auth_permission` VALUES (279,'Can view workflow',65,'view_workflow');
INSERT INTO `auth_permission` VALUES (280,'Can add Group approval task',2,'add_groupapprovaltask');
INSERT INTO `auth_permission` VALUES (281,'Can change Group approval task',2,'change_groupapprovaltask');
INSERT INTO `auth_permission` VALUES (282,'Can delete Group approval task',2,'delete_groupapprovaltask');
INSERT INTO `auth_permission` VALUES (283,'Can view Group approval task',2,'view_groupapprovaltask');
INSERT INTO `auth_permission` VALUES (284,'Can add Workflow state',66,'add_workflowstate');
INSERT INTO `auth_permission` VALUES (285,'Can change Workflow state',66,'change_workflowstate');
INSERT INTO `auth_permission` VALUES (286,'Can delete Workflow state',66,'delete_workflowstate');
INSERT INTO `auth_permission` VALUES (287,'Can view Workflow state',66,'view_workflowstate');
INSERT INTO `auth_permission` VALUES (288,'Can add workflow page',67,'add_workflowpage');
INSERT INTO `auth_permission` VALUES (289,'Can change workflow page',67,'change_workflowpage');
INSERT INTO `auth_permission` VALUES (290,'Can delete workflow page',67,'delete_workflowpage');
INSERT INTO `auth_permission` VALUES (291,'Can view workflow page',67,'view_workflowpage');
INSERT INTO `auth_permission` VALUES (292,'Can add workflow task order',68,'add_workflowtask');
INSERT INTO `auth_permission` VALUES (293,'Can change workflow task order',68,'change_workflowtask');
INSERT INTO `auth_permission` VALUES (294,'Can delete workflow task order',68,'delete_workflowtask');
INSERT INTO `auth_permission` VALUES (295,'Can view workflow task order',68,'view_workflowtask');
INSERT INTO `auth_permission` VALUES (296,'Can add page log entry',69,'add_pagelogentry');
INSERT INTO `auth_permission` VALUES (297,'Can change page log entry',69,'change_pagelogentry');
INSERT INTO `auth_permission` VALUES (298,'Can delete page log entry',69,'delete_pagelogentry');
INSERT INTO `auth_permission` VALUES (299,'Can view page log entry',69,'view_pagelogentry');
INSERT INTO `auth_permission` VALUES (300,'Can add locale',70,'add_locale');
INSERT INTO `auth_permission` VALUES (301,'Can change locale',70,'change_locale');
INSERT INTO `auth_permission` VALUES (302,'Can delete locale',70,'delete_locale');
INSERT INTO `auth_permission` VALUES (303,'Can view locale',70,'view_locale');
INSERT INTO `auth_permission` VALUES (304,'Can add comment',71,'add_comment');
INSERT INTO `auth_permission` VALUES (305,'Can change comment',71,'change_comment');
INSERT INTO `auth_permission` VALUES (306,'Can delete comment',71,'delete_comment');
INSERT INTO `auth_permission` VALUES (307,'Can view comment',71,'view_comment');
INSERT INTO `auth_permission` VALUES (308,'Can add comment reply',72,'add_commentreply');
INSERT INTO `auth_permission` VALUES (309,'Can change comment reply',72,'change_commentreply');
INSERT INTO `auth_permission` VALUES (310,'Can delete comment reply',72,'delete_commentreply');
INSERT INTO `auth_permission` VALUES (311,'Can view comment reply',72,'view_commentreply');
INSERT INTO `auth_permission` VALUES (312,'Can add page subscription',73,'add_pagesubscription');
INSERT INTO `auth_permission` VALUES (313,'Can change page subscription',73,'change_pagesubscription');
INSERT INTO `auth_permission` VALUES (314,'Can delete page subscription',73,'delete_pagesubscription');
INSERT INTO `auth_permission` VALUES (315,'Can view page subscription',73,'view_pagesubscription');
INSERT INTO `auth_permission` VALUES (316,'Can add tag',74,'add_tag');
INSERT INTO `auth_permission` VALUES (317,'Can change tag',74,'change_tag');
INSERT INTO `auth_permission` VALUES (318,'Can delete tag',74,'delete_tag');
INSERT INTO `auth_permission` VALUES (319,'Can view tag',74,'view_tag');
INSERT INTO `auth_permission` VALUES (320,'Can add tagged item',75,'add_taggeditem');
INSERT INTO `auth_permission` VALUES (321,'Can change tagged item',75,'change_taggeditem');
INSERT INTO `auth_permission` VALUES (322,'Can delete tagged item',75,'delete_taggeditem');
INSERT INTO `auth_permission` VALUES (323,'Can view tagged item',75,'view_taggeditem');
INSERT INTO `auth_permission` VALUES (324,'Can add Portal Hilfe Seite',76,'add_portalhelppage');
INSERT INTO `auth_permission` VALUES (325,'Can change Portal Hilfe Seite',76,'change_portalhelppage');
INSERT INTO `auth_permission` VALUES (326,'Can delete Portal Hilfe Seite',76,'delete_portalhelppage');
INSERT INTO `auth_permission` VALUES (327,'Can view Portal Hilfe Seite',76,'view_portalhelppage');
INSERT INTO `auth_permission` VALUES (328,'Can add portal help page section',77,'add_portalhelppagesection');
INSERT INTO `auth_permission` VALUES (329,'Can change portal help page section',77,'change_portalhelppagesection');
INSERT INTO `auth_permission` VALUES (330,'Can delete portal help page section',77,'delete_portalhelppagesection');
INSERT INTO `auth_permission` VALUES (331,'Can view portal help page section',77,'view_portalhelppagesection');
INSERT INTO `auth_permission` VALUES (332,'Can add Portal Seite',78,'add_portalpage');
INSERT INTO `auth_permission` VALUES (333,'Can change Portal Seite',78,'change_portalpage');
INSERT INTO `auth_permission` VALUES (334,'Can delete Portal Seite',78,'delete_portalpage');
INSERT INTO `auth_permission` VALUES (335,'Can view Portal Seite',78,'view_portalpage');
INSERT INTO `auth_permission` VALUES (336,'Can add Nutzeradmin',79,'add_tenantadmin');
INSERT INTO `auth_permission` VALUES (337,'Can change Nutzeradmin',79,'change_tenantadmin');
INSERT INTO `auth_permission` VALUES (338,'Can delete Nutzeradmin',79,'delete_tenantadmin');
INSERT INTO `auth_permission` VALUES (339,'Can view Nutzeradmin',79,'view_tenantadmin');
INSERT INTO `auth_permission` VALUES (340,'Can add application',80,'add_application');
INSERT INTO `auth_permission` VALUES (341,'Can change application',80,'change_application');
INSERT INTO `auth_permission` VALUES (342,'Can delete application',80,'delete_application');
INSERT INTO `auth_permission` VALUES (343,'Can view application',80,'view_application');
INSERT INTO `auth_permission` VALUES (344,'Can add access token',81,'add_accesstoken');
INSERT INTO `auth_permission` VALUES (345,'Can change access token',81,'change_accesstoken');
INSERT INTO `auth_permission` VALUES (346,'Can delete access token',81,'delete_accesstoken');
INSERT INTO `auth_permission` VALUES (347,'Can view access token',81,'view_accesstoken');
INSERT INTO `auth_permission` VALUES (348,'Can add grant',82,'add_grant');
INSERT INTO `auth_permission` VALUES (349,'Can change grant',82,'change_grant');
INSERT INTO `auth_permission` VALUES (350,'Can delete grant',82,'delete_grant');
INSERT INTO `auth_permission` VALUES (351,'Can view grant',82,'view_grant');
INSERT INTO `auth_permission` VALUES (352,'Can add refresh token',83,'add_refreshtoken');
INSERT INTO `auth_permission` VALUES (353,'Can change refresh token',83,'change_refreshtoken');
INSERT INTO `auth_permission` VALUES (354,'Can delete refresh token',83,'delete_refreshtoken');
INSERT INTO `auth_permission` VALUES (355,'Can view refresh token',83,'view_refreshtoken');
INSERT INTO `auth_permission` VALUES (356,'Can add id token',84,'add_idtoken');
INSERT INTO `auth_permission` VALUES (357,'Can change id token',84,'change_idtoken');
INSERT INTO `auth_permission` VALUES (358,'Can delete id token',84,'delete_idtoken');
INSERT INTO `auth_permission` VALUES (359,'Can view id token',84,'view_idtoken');
INSERT INTO `auth_permission` VALUES (360,'Can add cors model',85,'add_corsmodel');
INSERT INTO `auth_permission` VALUES (361,'Can change cors model',85,'change_corsmodel');
INSERT INTO `auth_permission` VALUES (362,'Can delete cors model',85,'delete_corsmodel');
INSERT INTO `auth_permission` VALUES (363,'Can view cors model',85,'view_corsmodel');
INSERT INTO `auth_permission` VALUES (364,'Can add Service Provider',86,'add_serviceprovider');
INSERT INTO `auth_permission` VALUES (365,'Can change Service Provider',86,'change_serviceprovider');
INSERT INTO `auth_permission` VALUES (366,'Can delete Service Provider',86,'delete_serviceprovider');
INSERT INTO `auth_permission` VALUES (367,'Can view Service Provider',86,'view_serviceprovider');
INSERT INTO `auth_permission` VALUES (368,'Can add Persistent Id',87,'add_persistentid');
INSERT INTO `auth_permission` VALUES (369,'Can change Persistent Id',87,'change_persistentid');
INSERT INTO `auth_permission` VALUES (370,'Can delete Persistent Id',87,'delete_persistentid');
INSERT INTO `auth_permission` VALUES (371,'Can view Persistent Id',87,'view_persistentid');
INSERT INTO `auth_permission` VALUES (372,'Can add Reservation',88,'add_reservation');
INSERT INTO `auth_permission` VALUES (373,'Can change Reservation',88,'change_reservation');
INSERT INTO `auth_permission` VALUES (374,'Can delete Reservation',88,'delete_reservation');
INSERT INTO `auth_permission` VALUES (375,'Can view Reservation',88,'view_reservation');
INSERT INTO `auth_permission` VALUES (376,'Can add Reservationsobjekt',89,'add_reservationobject');
INSERT INTO `auth_permission` VALUES (377,'Can change Reservationsobjekt',89,'change_reservationobject');
INSERT INTO `auth_permission` VALUES (378,'Can delete Reservationsobjekt',89,'delete_reservationobject');
INSERT INTO `auth_permission` VALUES (379,'Can view Reservationsobjekt',89,'view_reservationobject');
INSERT INTO `auth_permission` VALUES (380,'Can add Reservationstyp',90,'add_reservationtype');
INSERT INTO `auth_permission` VALUES (381,'Can change Reservationstyp',90,'change_reservationtype');
INSERT INTO `auth_permission` VALUES (382,'Can delete Reservationstyp',90,'delete_reservationtype');
INSERT INTO `auth_permission` VALUES (383,'Can view Reservationstyp',90,'view_reservationtype');
INSERT INTO `auth_permission` VALUES (384,'Can add Meldungstyp',91,'add_reporttype');
INSERT INTO `auth_permission` VALUES (385,'Can change Meldungstyp',91,'change_reporttype');
INSERT INTO `auth_permission` VALUES (386,'Can delete Meldungstyp',91,'delete_reporttype');
INSERT INTO `auth_permission` VALUES (387,'Can view Meldungstyp',91,'view_reporttype');
INSERT INTO `auth_permission` VALUES (388,'Can add Kategorie',92,'add_reportcategory');
INSERT INTO `auth_permission` VALUES (389,'Can change Kategorie',92,'change_reportcategory');
INSERT INTO `auth_permission` VALUES (390,'Can delete Kategorie',92,'delete_reportcategory');
INSERT INTO `auth_permission` VALUES (391,'Can view Kategorie',92,'view_reportcategory');
INSERT INTO `auth_permission` VALUES (392,'Can add Meldung',93,'add_report');
INSERT INTO `auth_permission` VALUES (393,'Can change Meldung',93,'change_report');
INSERT INTO `auth_permission` VALUES (394,'Can delete Meldung',93,'delete_report');
INSERT INTO `auth_permission` VALUES (395,'Can view Meldung',93,'view_report');
INSERT INTO `auth_permission` VALUES (396,'Can add Meldungsbild',94,'add_reportpicture');
INSERT INTO `auth_permission` VALUES (397,'Can change Meldungsbild',94,'change_reportpicture');
INSERT INTO `auth_permission` VALUES (398,'Can delete Meldungsbild',94,'delete_reportpicture');
INSERT INTO `auth_permission` VALUES (399,'Can view Meldungsbild',94,'view_reportpicture');
INSERT INTO `auth_permission` VALUES (400,'Can add Logbucheintrag',95,'add_reportlogentry');
INSERT INTO `auth_permission` VALUES (401,'Can change Logbucheintrag',95,'change_reportlogentry');
INSERT INTO `auth_permission` VALUES (402,'Can delete Logbucheintrag',95,'delete_reportlogentry');
INSERT INTO `auth_permission` VALUES (403,'Can view Logbucheintrag',95,'view_reportlogentry');
INSERT INTO `auth_permission` VALUES (404,'Can add Nutzungsart',96,'add_reservationusagetype');
INSERT INTO `auth_permission` VALUES (405,'Can change Nutzungsart',96,'change_reservationusagetype');
INSERT INTO `auth_permission` VALUES (406,'Can delete Nutzungsart',96,'delete_reservationusagetype');
INSERT INTO `auth_permission` VALUES (407,'Can view Nutzungsart',96,'view_reservationusagetype');
INSERT INTO `auth_permission` VALUES (408,'Can add Reservationstarif',97,'add_reservationprice');
INSERT INTO `auth_permission` VALUES (409,'Can change Reservationstarif',97,'change_reservationprice');
INSERT INTO `auth_permission` VALUES (410,'Can delete Reservationstarif',97,'delete_reservationprice');
INSERT INTO `auth_permission` VALUES (411,'Can view Reservationstarif',97,'view_reservationprice');
INSERT INTO `auth_permission` VALUES (412,'Can add Konto',98,'add_account');
INSERT INTO `auth_permission` VALUES (413,'Can change Konto',98,'change_account');
INSERT INTO `auth_permission` VALUES (414,'Can delete Konto',98,'delete_account');
INSERT INTO `auth_permission` VALUES (415,'Can view Konto',98,'view_account');
INSERT INTO `auth_permission` VALUES (416,'Can add Verkaufsstelle',99,'add_vendor');
INSERT INTO `auth_permission` VALUES (417,'Can change Verkaufsstelle',99,'change_vendor');
INSERT INTO `auth_permission` VALUES (418,'Can delete Verkaufsstelle',99,'delete_vendor');
INSERT INTO `auth_permission` VALUES (419,'Can view Verkaufsstelle',99,'view_vendor');
INSERT INTO `auth_permission` VALUES (420,'Can add Verkaufsstellenadmin',100,'add_vendoradmin');
INSERT INTO `auth_permission` VALUES (421,'Can change Verkaufsstellenadmin',100,'change_vendoradmin');
INSERT INTO `auth_permission` VALUES (422,'Can delete Verkaufsstellenadmin',100,'delete_vendoradmin');
INSERT INTO `auth_permission` VALUES (423,'Can view Verkaufsstellenadmin',100,'view_vendoradmin');
INSERT INTO `auth_permission` VALUES (424,'Can add Transaktion',101,'add_transaction');
INSERT INTO `auth_permission` VALUES (425,'Can change Transaktion',101,'change_transaction');
INSERT INTO `auth_permission` VALUES (426,'Can delete Transaktion',101,'delete_transaction');
INSERT INTO `auth_permission` VALUES (427,'Can view Transaktion',101,'view_transaction');
INSERT INTO `auth_permission` VALUES (428,'Can add Kontobesitzer:in',102,'add_accountowner');
INSERT INTO `auth_permission` VALUES (429,'Can change Kontobesitzer:in',102,'change_accountowner');
INSERT INTO `auth_permission` VALUES (430,'Can delete Kontobesitzer:in',102,'delete_accountowner');
INSERT INTO `auth_permission` VALUES (431,'Can view Kontobesitzer:in',102,'view_accountowner');
INSERT INTO `auth_permission` VALUES (432,'Can add Kontoeinstellung pro Benutzer',103,'add_useraccountsetting');
INSERT INTO `auth_permission` VALUES (433,'Can change Kontoeinstellung pro Benutzer',103,'change_useraccountsetting');
INSERT INTO `auth_permission` VALUES (434,'Can delete Kontoeinstellung pro Benutzer',103,'delete_useraccountsetting');
INSERT INTO `auth_permission` VALUES (435,'Can view Kontoeinstellung pro Benutzer',103,'view_useraccountsetting');
INSERT INTO `auth_permission` VALUES (436,'Can add Reporttyp',104,'add_reporttype');
INSERT INTO `auth_permission` VALUES (437,'Can change Reporttyp',104,'change_reporttype');
INSERT INTO `auth_permission` VALUES (438,'Can delete Reporttyp',104,'delete_reporttype');
INSERT INTO `auth_permission` VALUES (439,'Can view Reporttyp',104,'view_reporttype');
INSERT INTO `auth_permission` VALUES (440,'Can add Eingabefeld',105,'add_reportinputfield');
INSERT INTO `auth_permission` VALUES (441,'Can change Eingabefeld',105,'change_reportinputfield');
INSERT INTO `auth_permission` VALUES (442,'Can delete Eingabefeld',105,'delete_reportinputfield');
INSERT INTO `auth_permission` VALUES (443,'Can view Eingabefeld',105,'view_reportinputfield');
INSERT INTO `auth_permission` VALUES (444,'Can add Report',106,'add_report');
INSERT INTO `auth_permission` VALUES (445,'Can change Report',106,'change_report');
INSERT INTO `auth_permission` VALUES (446,'Can delete Report',106,'delete_report');
INSERT INTO `auth_permission` VALUES (447,'Can view Report',106,'view_report');
INSERT INTO `auth_permission` VALUES (448,'Can add Reportoutput',107,'add_reportoutput');
INSERT INTO `auth_permission` VALUES (449,'Can change Reportoutput',107,'change_reportoutput');
INSERT INTO `auth_permission` VALUES (450,'Can delete Reportoutput',107,'delete_reportoutput');
INSERT INTO `auth_permission` VALUES (451,'Can view Reportoutput',107,'view_reportoutput');
INSERT INTO `auth_permission` VALUES (452,'Can add Eingabewert',108,'add_reportinputdata');
INSERT INTO `auth_permission` VALUES (453,'Can change Eingabewert',108,'change_reportinputdata');
INSERT INTO `auth_permission` VALUES (454,'Can delete Eingabewert',108,'delete_reportinputdata');
INSERT INTO `auth_permission` VALUES (455,'Can view Eingabewert',108,'view_reportinputdata');
INSERT INTO `auth_permission` VALUES (456,'Can add model log entry',109,'add_modellogentry');
INSERT INTO `auth_permission` VALUES (457,'Can change model log entry',109,'change_modellogentry');
INSERT INTO `auth_permission` VALUES (458,'Can delete model log entry',109,'delete_modellogentry');
INSERT INTO `auth_permission` VALUES (459,'Can view model log entry',109,'view_modellogentry');
INSERT INTO `auth_permission` VALUES (460,'Can add reference index',110,'add_referenceindex');
INSERT INTO `auth_permission` VALUES (461,'Can change reference index',110,'change_referenceindex');
INSERT INTO `auth_permission` VALUES (462,'Can delete reference index',110,'delete_referenceindex');
INSERT INTO `auth_permission` VALUES (463,'Can view reference index',110,'view_referenceindex');
INSERT INTO `auth_permission` VALUES (464,'Delete pages with children',1,'bulk_delete_page');
INSERT INTO `auth_permission` VALUES (465,'Lock/unlock pages you\'ve locked',1,'lock_page');
INSERT INTO `auth_permission` VALUES (466,'Publish any page',1,'publish_page');
INSERT INTO `auth_permission` VALUES (467,'Unlock any page',1,'unlock_page');
INSERT INTO `auth_permission` VALUES (468,'Can add revision',57,'add_revision');
INSERT INTO `auth_permission` VALUES (469,'Can change revision',57,'change_revision');
INSERT INTO `auth_permission` VALUES (470,'Can delete revision',57,'delete_revision');
INSERT INTO `auth_permission` VALUES (471,'Can view revision',57,'view_revision');
INSERT INTO `auth_permission` VALUES (472,'Can add workflow content type',111,'add_workflowcontenttype');
INSERT INTO `auth_permission` VALUES (473,'Can change workflow content type',111,'change_workflowcontenttype');
INSERT INTO `auth_permission` VALUES (474,'Can delete workflow content type',111,'delete_workflowcontenttype');
INSERT INTO `auth_permission` VALUES (475,'Can view workflow content type',111,'view_workflowcontenttype');
INSERT INTO `auth_permission` VALUES (476,'Can add index entry',112,'add_indexentry');
INSERT INTO `auth_permission` VALUES (477,'Can change index entry',112,'change_indexentry');
INSERT INTO `auth_permission` VALUES (478,'Can delete index entry',112,'delete_indexentry');
INSERT INTO `auth_permission` VALUES (479,'Can view index entry',112,'view_indexentry');
INSERT INTO `auth_permission` VALUES (480,'Can add event',113,'add_event');
INSERT INTO `auth_permission` VALUES (481,'Can change event',113,'change_event');
INSERT INTO `auth_permission` VALUES (482,'Can delete event',113,'delete_event');
INSERT INTO `auth_permission` VALUES (483,'Can view event',113,'view_event');
INSERT INTO `auth_permission` VALUES (484,'Can add medienspiegel',114,'add_medienspiegel');
INSERT INTO `auth_permission` VALUES (485,'Can change medienspiegel',114,'change_medienspiegel');
INSERT INTO `auth_permission` VALUES (486,'Can delete medienspiegel',114,'delete_medienspiegel');
INSERT INTO `auth_permission` VALUES (487,'Can view medienspiegel',114,'view_medienspiegel');
INSERT INTO `auth_permission` VALUES (488,'Can add text block',115,'add_textblock');
INSERT INTO `auth_permission` VALUES (489,'Can change text block',115,'change_textblock');
INSERT INTO `auth_permission` VALUES (490,'Can delete text block',115,'delete_textblock');
INSERT INTO `auth_permission` VALUES (491,'Can view text block',115,'view_textblock');
INSERT INTO `auth_permission` VALUES (492,'Can add Website Seite',116,'add_websitepage');
INSERT INTO `auth_permission` VALUES (493,'Can change Website Seite',116,'change_websitepage');
INSERT INTO `auth_permission` VALUES (494,'Can delete Website Seite',116,'delete_websitepage');
INSERT INTO `auth_permission` VALUES (495,'Can view Website Seite',116,'view_websitepage');
INSERT INTO `auth_permission` VALUES (496,'Can add Website Hauptseite',117,'add_websitemainpage');
INSERT INTO `auth_permission` VALUES (497,'Can change Website Hauptseite',117,'change_websitemainpage');
INSERT INTO `auth_permission` VALUES (498,'Can delete Website Hauptseite',117,'delete_websitemainpage');
INSERT INTO `auth_permission` VALUES (499,'Can view Website Hauptseite',117,'view_websitemainpage');
INSERT INTO `auth_permission` VALUES (500,'Can add Vorlagenoptionentyp',118,'add_contenttemplateoptiontype');
INSERT INTO `auth_permission` VALUES (501,'Can change Vorlagenoptionentyp',118,'change_contenttemplateoptiontype');
INSERT INTO `auth_permission` VALUES (502,'Can delete Vorlagenoptionentyp',118,'delete_contenttemplateoptiontype');
INSERT INTO `auth_permission` VALUES (503,'Can view Vorlagenoptionentyp',118,'view_contenttemplateoptiontype');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (1,4,3);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authtoken_token`
--

DROP TABLE IF EXISTS `authtoken_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `corsheaders_corsmodel`
--

DROP TABLE IF EXISTS `corsheaders_corsmodel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `corsheaders_corsmodel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cors` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `corsheaders_corsmodel`
--

LOCK TABLES `corsheaders_corsmodel` WRITE;
/*!40000 ALTER TABLE `corsheaders_corsmodel` DISABLE KEYS */;
/*!40000 ALTER TABLE `corsheaders_corsmodel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_accounting_account`
--

DROP TABLE IF EXISTS `credit_accounting_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_accounting_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `pin` varchar(20) NOT NULL,
  `balance` decimal(10,2) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `vendor_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_pin_vendor` (`pin`,`vendor_id`),
  UNIQUE KEY `unique_name_vendor` (`name`,`vendor_id`),
  KEY `credit_accounting_ac_vendor_id_6e4f4248_fk_credit_ac` (`vendor_id`),
  CONSTRAINT `credit_accounting_ac_vendor_id_6e4f4248_fk_credit_ac` FOREIGN KEY (`vendor_id`) REFERENCES `credit_accounting_vendor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_accounting_account`
--

LOCK TABLES `credit_accounting_account` WRITE;
/*!40000 ALTER TABLE `credit_accounting_account` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_accounting_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_accounting_accountowner`
--

DROP TABLE IF EXISTS `credit_accounting_accountowner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_accounting_accountowner` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `owner_id` int(10) unsigned NOT NULL,
  `name_id` int(11) NOT NULL,
  `owner_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_accounting_ac_owner_type_id_a14fa806_fk_django_co` (`owner_type_id`),
  KEY `credit_accounting_ac_name_id_0fdb52f4_fk_credit_ac` (`name_id`),
  CONSTRAINT `credit_accounting_ac_name_id_0fdb52f4_fk_credit_ac` FOREIGN KEY (`name_id`) REFERENCES `credit_accounting_account` (`id`),
  CONSTRAINT `credit_accounting_ac_owner_type_id_a14fa806_fk_django_co` FOREIGN KEY (`owner_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_accounting_accountowner`
--

LOCK TABLES `credit_accounting_accountowner` WRITE;
/*!40000 ALTER TABLE `credit_accounting_accountowner` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_accounting_accountowner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_accounting_transaction`
--

DROP TABLE IF EXISTS `credit_accounting_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_accounting_transaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `date` datetime(6) NOT NULL,
  `description` varchar(255) NOT NULL,
  `account_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `transaction_id` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_accounting_tr_account_id_ce9c06c7_fk_credit_ac` (`account_id`),
  KEY `credit_accounting_transaction_user_id_44b83381_fk_auth_user_id` (`user_id`),
  KEY `credit_accounting_transaction_transaction_id_2513b285` (`transaction_id`),
  CONSTRAINT `credit_accounting_tr_account_id_ce9c06c7_fk_credit_ac` FOREIGN KEY (`account_id`) REFERENCES `credit_accounting_account` (`id`),
  CONSTRAINT `credit_accounting_transaction_user_id_44b83381_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_accounting_transaction`
--

LOCK TABLES `credit_accounting_transaction` WRITE;
/*!40000 ALTER TABLE `credit_accounting_transaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_accounting_transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_accounting_useraccountsetting`
--

DROP TABLE IF EXISTS `credit_accounting_useraccountsetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_accounting_useraccountsetting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `value` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `account_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_name_account_user` (`name`,`account_id`,`user_id`),
  KEY `credit_accounting_us_account_id_e820ab1d_fk_credit_ac` (`account_id`),
  KEY `credit_accounting_us_user_id_d01885be_fk_auth_user` (`user_id`),
  CONSTRAINT `credit_accounting_us_account_id_e820ab1d_fk_credit_ac` FOREIGN KEY (`account_id`) REFERENCES `credit_accounting_account` (`id`),
  CONSTRAINT `credit_accounting_us_user_id_d01885be_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_accounting_useraccountsetting`
--

LOCK TABLES `credit_accounting_useraccountsetting` WRITE;
/*!40000 ALTER TABLE `credit_accounting_useraccountsetting` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_accounting_useraccountsetting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_accounting_vendor`
--

DROP TABLE IF EXISTS `credit_accounting_vendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_accounting_vendor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `vendor_type` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `api_secret` varchar(50) NOT NULL,
  `qr_iban` varchar(21) NOT NULL,
  `qr_line1` varchar(50) NOT NULL,
  `qr_line2` varchar(50) NOT NULL,
  `qr_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_accounting_vendor`
--

LOCK TABLES `credit_accounting_vendor` WRITE;
/*!40000 ALTER TABLE `credit_accounting_vendor` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_accounting_vendor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_accounting_vendoradmin`
--

DROP TABLE IF EXISTS `credit_accounting_vendoradmin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_accounting_vendoradmin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `role` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `name_id` int(11) NOT NULL,
  `vendor_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_accounting_ve_name_id_cb293b8e_fk_geno_addr` (`name_id`),
  KEY `credit_accounting_ve_vendor_id_b164116d_fk_credit_ac` (`vendor_id`),
  CONSTRAINT `credit_accounting_ve_name_id_cb293b8e_fk_geno_addr` FOREIGN KEY (`name_id`) REFERENCES `geno_address` (`id`),
  CONSTRAINT `credit_accounting_ve_vendor_id_b164116d_fk_credit_ac` FOREIGN KEY (`vendor_id`) REFERENCES `credit_accounting_vendor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_accounting_vendoradmin`
--

LOCK TABLES `credit_accounting_vendoradmin` WRITE;
/*!40000 ALTER TABLE `credit_accounting_vendoradmin` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_accounting_vendoradmin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=364 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (28,'admin','logentry');
INSERT INTO `django_content_type` VALUES (30,'auth','group');
INSERT INTO `django_content_type` VALUES (29,'auth','permission');
INSERT INTO `django_content_type` VALUES (31,'auth','user');
INSERT INTO `django_content_type` VALUES (45,'authtoken','token');
INSERT INTO `django_content_type` VALUES (46,'authtoken','tokenproxy');
INSERT INTO `django_content_type` VALUES (32,'contenttypes','contenttype');
INSERT INTO `django_content_type` VALUES (85,'corsheaders','corsmodel');
INSERT INTO `django_content_type` VALUES (98,'credit_accounting','account');
INSERT INTO `django_content_type` VALUES (102,'credit_accounting','accountowner');
INSERT INTO `django_content_type` VALUES (101,'credit_accounting','transaction');
INSERT INTO `django_content_type` VALUES (103,'credit_accounting','useraccountsetting');
INSERT INTO `django_content_type` VALUES (99,'credit_accounting','vendor');
INSERT INTO `django_content_type` VALUES (100,'credit_accounting','vendoradmin');
INSERT INTO `django_content_type` VALUES (87,'djangosaml2idp','persistentid');
INSERT INTO `django_content_type` VALUES (86,'djangosaml2idp','serviceprovider');
INSERT INTO `django_content_type` VALUES (35,'easy_thumbnails','source');
INSERT INTO `django_content_type` VALUES (36,'easy_thumbnails','thumbnail');
INSERT INTO `django_content_type` VALUES (37,'easy_thumbnails','thumbnaildimensions');
INSERT INTO `django_content_type` VALUES (38,'filer','clipboard');
INSERT INTO `django_content_type` VALUES (39,'filer','clipboarditem');
INSERT INTO `django_content_type` VALUES (40,'filer','file');
INSERT INTO `django_content_type` VALUES (41,'filer','folder');
INSERT INTO `django_content_type` VALUES (42,'filer','folderpermission');
INSERT INTO `django_content_type` VALUES (43,'filer','image');
INSERT INTO `django_content_type` VALUES (44,'filer','thumbnailoption');
INSERT INTO `django_content_type` VALUES (6,'geno','address');
INSERT INTO `django_content_type` VALUES (25,'geno','building');
INSERT INTO `django_content_type` VALUES (21,'geno','child');
INSERT INTO `django_content_type` VALUES (22,'geno','contenttemplate');
INSERT INTO `django_content_type` VALUES (27,'geno','contenttemplateoption');
INSERT INTO `django_content_type` VALUES (118,'geno','contenttemplateoptiontype');
INSERT INTO `django_content_type` VALUES (17,'geno','contract');
INSERT INTO `django_content_type` VALUES (12,'geno','document');
INSERT INTO `django_content_type` VALUES (13,'geno','documenttype');
INSERT INTO `django_content_type` VALUES (24,'geno','genericattribute');
INSERT INTO `django_content_type` VALUES (18,'geno','invoice');
INSERT INTO `django_content_type` VALUES (23,'geno','invoicecategory');
INSERT INTO `django_content_type` VALUES (19,'geno','lookuptable');
INSERT INTO `django_content_type` VALUES (7,'geno','member');
INSERT INTO `django_content_type` VALUES (8,'geno','memberattribute');
INSERT INTO `django_content_type` VALUES (9,'geno','memberattributetype');
INSERT INTO `django_content_type` VALUES (14,'geno','registration');
INSERT INTO `django_content_type` VALUES (15,'geno','registrationevent');
INSERT INTO `django_content_type` VALUES (16,'geno','registrationslot');
INSERT INTO `django_content_type` VALUES (20,'geno','rentalunit');
INSERT INTO `django_content_type` VALUES (10,'geno','share');
INSERT INTO `django_content_type` VALUES (11,'geno','sharetype');
INSERT INTO `django_content_type` VALUES (26,'geno','tenant');
INSERT INTO `django_content_type` VALUES (81,'oauth2_provider','accesstoken');
INSERT INTO `django_content_type` VALUES (80,'oauth2_provider','application');
INSERT INTO `django_content_type` VALUES (82,'oauth2_provider','grant');
INSERT INTO `django_content_type` VALUES (84,'oauth2_provider','idtoken');
INSERT INTO `django_content_type` VALUES (83,'oauth2_provider','refreshtoken');
INSERT INTO `django_content_type` VALUES (76,'portal','portalhelppage');
INSERT INTO `django_content_type` VALUES (77,'portal','portalhelppagesection');
INSERT INTO `django_content_type` VALUES (78,'portal','portalpage');
INSERT INTO `django_content_type` VALUES (79,'portal','tenantadmin');
INSERT INTO `django_content_type` VALUES (106,'report','report');
INSERT INTO `django_content_type` VALUES (108,'report','reportinputdata');
INSERT INTO `django_content_type` VALUES (105,'report','reportinputfield');
INSERT INTO `django_content_type` VALUES (107,'report','reportoutput');
INSERT INTO `django_content_type` VALUES (104,'report','reporttype');
INSERT INTO `django_content_type` VALUES (93,'reservation','report');
INSERT INTO `django_content_type` VALUES (92,'reservation','reportcategory');
INSERT INTO `django_content_type` VALUES (95,'reservation','reportlogentry');
INSERT INTO `django_content_type` VALUES (94,'reservation','reportpicture');
INSERT INTO `django_content_type` VALUES (91,'reservation','reporttype');
INSERT INTO `django_content_type` VALUES (88,'reservation','reservation');
INSERT INTO `django_content_type` VALUES (89,'reservation','reservationobject');
INSERT INTO `django_content_type` VALUES (97,'reservation','reservationprice');
INSERT INTO `django_content_type` VALUES (90,'reservation','reservationtype');
INSERT INTO `django_content_type` VALUES (96,'reservation','reservationusagetype');
INSERT INTO `django_content_type` VALUES (33,'sessions','session');
INSERT INTO `django_content_type` VALUES (34,'sites','site');
INSERT INTO `django_content_type` VALUES (74,'taggit','tag');
INSERT INTO `django_content_type` VALUES (75,'taggit','taggeditem');
INSERT INTO `django_content_type` VALUES (3,'wagtailadmin','admin');
INSERT INTO `django_content_type` VALUES (60,'wagtailcore','collection');
INSERT INTO `django_content_type` VALUES (62,'wagtailcore','collectionviewrestriction');
INSERT INTO `django_content_type` VALUES (71,'wagtailcore','comment');
INSERT INTO `django_content_type` VALUES (72,'wagtailcore','commentreply');
INSERT INTO `django_content_type` VALUES (2,'wagtailcore','groupapprovaltask');
INSERT INTO `django_content_type` VALUES (61,'wagtailcore','groupcollectionpermission');
INSERT INTO `django_content_type` VALUES (56,'wagtailcore','grouppagepermission');
INSERT INTO `django_content_type` VALUES (70,'wagtailcore','locale');
INSERT INTO `django_content_type` VALUES (109,'wagtailcore','modellogentry');
INSERT INTO `django_content_type` VALUES (1,'wagtailcore','page');
INSERT INTO `django_content_type` VALUES (69,'wagtailcore','pagelogentry');
INSERT INTO `django_content_type` VALUES (73,'wagtailcore','pagesubscription');
INSERT INTO `django_content_type` VALUES (58,'wagtailcore','pageviewrestriction');
INSERT INTO `django_content_type` VALUES (110,'wagtailcore','referenceindex');
INSERT INTO `django_content_type` VALUES (57,'wagtailcore','revision');
INSERT INTO `django_content_type` VALUES (59,'wagtailcore','site');
INSERT INTO `django_content_type` VALUES (63,'wagtailcore','task');
INSERT INTO `django_content_type` VALUES (64,'wagtailcore','taskstate');
INSERT INTO `django_content_type` VALUES (65,'wagtailcore','workflow');
INSERT INTO `django_content_type` VALUES (111,'wagtailcore','workflowcontenttype');
INSERT INTO `django_content_type` VALUES (67,'wagtailcore','workflowpage');
INSERT INTO `django_content_type` VALUES (66,'wagtailcore','workflowstate');
INSERT INTO `django_content_type` VALUES (68,'wagtailcore','workflowtask');
INSERT INTO `django_content_type` VALUES (4,'wagtaildocs','document');
INSERT INTO `django_content_type` VALUES (51,'wagtaildocs','uploadeddocument');
INSERT INTO `django_content_type` VALUES (49,'wagtailembeds','embed');
INSERT INTO `django_content_type` VALUES (47,'wagtailforms','formsubmission');
INSERT INTO `django_content_type` VALUES (5,'wagtailimages','image');
INSERT INTO `django_content_type` VALUES (52,'wagtailimages','rendition');
INSERT INTO `django_content_type` VALUES (53,'wagtailimages','uploadedimage');
INSERT INTO `django_content_type` VALUES (48,'wagtailredirects','redirect');
INSERT INTO `django_content_type` VALUES (112,'wagtailsearch','indexentry');
INSERT INTO `django_content_type` VALUES (54,'wagtailsearch','query');
INSERT INTO `django_content_type` VALUES (55,'wagtailsearch','querydailyhits');
INSERT INTO `django_content_type` VALUES (50,'wagtailusers','userprofile');
INSERT INTO `django_content_type` VALUES (113,'website','event');
INSERT INTO `django_content_type` VALUES (114,'website','medienspiegel');
INSERT INTO `django_content_type` VALUES (115,'website','textblock');
INSERT INTO `django_content_type` VALUES (117,'website','websitemainpage');
INSERT INTO `django_content_type` VALUES (116,'website','websitepage');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=386 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2024-10-08 14:27:21.360925');
INSERT INTO `django_migrations` VALUES (2,'auth','0001_initial','2024-10-08 14:27:22.501094');
INSERT INTO `django_migrations` VALUES (3,'admin','0001_initial','2024-10-08 14:27:28.526386');
INSERT INTO `django_migrations` VALUES (4,'admin','0002_logentry_remove_auto_add','2024-10-08 14:27:29.610915');
INSERT INTO `django_migrations` VALUES (5,'admin','0003_logentry_add_action_flag_choices','2024-10-08 14:27:29.642959');
INSERT INTO `django_migrations` VALUES (6,'contenttypes','0002_remove_content_type_name','2024-10-08 14:27:30.100135');
INSERT INTO `django_migrations` VALUES (7,'auth','0002_alter_permission_name_max_length','2024-10-08 14:27:31.957381');
INSERT INTO `django_migrations` VALUES (8,'auth','0003_alter_user_email_max_length','2024-10-08 14:27:32.800363');
INSERT INTO `django_migrations` VALUES (9,'auth','0004_alter_user_username_opts','2024-10-08 14:27:32.850766');
INSERT INTO `django_migrations` VALUES (10,'auth','0005_alter_user_last_login_null','2024-10-08 14:27:33.551452');
INSERT INTO `django_migrations` VALUES (11,'auth','0006_require_contenttypes_0002','2024-10-08 14:27:33.595722');
INSERT INTO `django_migrations` VALUES (12,'auth','0007_alter_validators_add_error_messages','2024-10-08 14:27:33.648595');
INSERT INTO `django_migrations` VALUES (13,'auth','0008_alter_user_username_max_length','2024-10-08 14:27:33.950567');
INSERT INTO `django_migrations` VALUES (14,'auth','0009_alter_user_last_name_max_length','2024-10-08 14:27:34.094498');
INSERT INTO `django_migrations` VALUES (15,'auth','0010_alter_group_name_max_length','2024-10-08 14:27:34.548424');
INSERT INTO `django_migrations` VALUES (16,'auth','0011_update_proxy_permissions','2024-10-08 14:27:34.600745');
INSERT INTO `django_migrations` VALUES (17,'authtoken','0001_initial','2024-10-08 14:27:34.973065');
INSERT INTO `django_migrations` VALUES (18,'authtoken','0002_auto_20160226_1747','2024-10-08 14:27:37.284160');
INSERT INTO `django_migrations` VALUES (19,'authtoken','0003_tokenproxy','2024-10-08 14:27:37.396253');
INSERT INTO `django_migrations` VALUES (20,'corsheaders','0001_initial','2024-10-08 14:27:37.640706');
INSERT INTO `django_migrations` VALUES (124,'djangosaml2idp','0001_initial','2024-10-08 14:30:18.244043');
INSERT INTO `django_migrations` VALUES (125,'djangosaml2idp','0002_persistent_id','2024-10-08 14:30:19.008386');
INSERT INTO `django_migrations` VALUES (126,'easy_thumbnails','0001_initial','2024-10-08 14:30:21.101578');
INSERT INTO `django_migrations` VALUES (127,'easy_thumbnails','0002_thumbnaildimensions','2024-10-08 14:30:22.812589');
INSERT INTO `django_migrations` VALUES (128,'filer','0001_initial','2024-10-08 14:30:26.200372');
INSERT INTO `django_migrations` VALUES (129,'filer','0002_auto_20150606_2003','2024-10-08 14:30:51.301302');
INSERT INTO `django_migrations` VALUES (130,'filer','0003_thumbnailoption','2024-10-08 14:30:56.318861');
INSERT INTO `django_migrations` VALUES (131,'filer','0004_auto_20160328_1434','2024-10-08 14:30:56.695259');
INSERT INTO `django_migrations` VALUES (132,'filer','0005_auto_20160623_1425','2024-10-08 14:30:58.352176');
INSERT INTO `django_migrations` VALUES (133,'filer','0006_auto_20160623_1627','2024-10-08 14:30:58.728255');
INSERT INTO `django_migrations` VALUES (134,'filer','0007_auto_20161016_1055','2024-10-08 14:30:58.756712');
INSERT INTO `django_migrations` VALUES (135,'filer','0008_auto_20171117_1313','2024-10-08 14:30:58.787522');
INSERT INTO `django_migrations` VALUES (136,'filer','0009_auto_20171220_1635','2024-10-08 14:30:59.266067');
INSERT INTO `django_migrations` VALUES (137,'filer','0010_auto_20180414_2058','2024-10-08 14:30:59.647531');
INSERT INTO `django_migrations` VALUES (138,'filer','0011_auto_20190418_0137','2024-10-08 14:31:00.041207');
INSERT INTO `django_migrations` VALUES (139,'filer','0012_file_mime_type','2024-10-08 14:31:00.234292');
INSERT INTO `django_migrations` VALUES (140,'filer','0013_image_width_height_to_float','2024-10-08 14:31:00.849539');
INSERT INTO `django_migrations` VALUES (141,'filer','0014_folder_permission_choices','2024-10-08 14:31:00.903169');
INSERT INTO `django_migrations` VALUES (142,'filer','0015_alter_file_owner_alter_file_polymorphic_ctype_and_more','2024-10-08 14:31:02.964833');
INSERT INTO `django_migrations` VALUES (143,'filer','0016_alter_folder_index_together_remove_folder_level_and_more','2024-10-08 14:31:03.490198');
INSERT INTO `django_migrations` VALUES (144,'filer','0017_image__transparent','2024-10-08 14:31:03.607941');
INSERT INTO `django_migrations` VALUES (151,'oauth2_provider','0001_initial','2024-10-08 14:31:08.851717');
INSERT INTO `django_migrations` VALUES (152,'oauth2_provider','0002_auto_20190406_1805','2024-10-08 14:31:12.612098');
INSERT INTO `django_migrations` VALUES (153,'oauth2_provider','0003_auto_20201211_1314','2024-10-08 14:31:13.026119');
INSERT INTO `django_migrations` VALUES (154,'oauth2_provider','0004_auto_20200902_2022','2024-10-08 14:31:14.101480');
INSERT INTO `django_migrations` VALUES (155,'oauth2_provider','0005_auto_20211222_2352','2024-10-08 14:31:17.878056');
INSERT INTO `django_migrations` VALUES (156,'oauth2_provider','0006_alter_application_client_secret','2024-10-08 14:31:17.975421');
INSERT INTO `django_migrations` VALUES (157,'oauth2_provider','0007_application_post_logout_redirect_uris','2024-10-08 14:31:18.089293');
INSERT INTO `django_migrations` VALUES (158,'wagtailcore','0001_initial','2024-10-08 14:31:19.402232');
INSERT INTO `django_migrations` VALUES (159,'wagtailcore','0002_initial_data','2024-10-08 14:31:19.423988');
INSERT INTO `django_migrations` VALUES (160,'wagtailcore','0003_add_uniqueness_constraint_on_group_page_permission','2024-10-08 14:31:19.438871');
INSERT INTO `django_migrations` VALUES (161,'wagtailcore','0004_page_locked','2024-10-08 14:31:19.449957');
INSERT INTO `django_migrations` VALUES (162,'wagtailcore','0005_add_page_lock_permission_to_moderators','2024-10-08 14:31:19.461005');
INSERT INTO `django_migrations` VALUES (163,'wagtailcore','0006_add_lock_page_permission','2024-10-08 14:31:19.472048');
INSERT INTO `django_migrations` VALUES (164,'wagtailcore','0007_page_latest_revision_created_at','2024-10-08 14:31:19.483115');
INSERT INTO `django_migrations` VALUES (165,'wagtailcore','0008_populate_latest_revision_created_at','2024-10-08 14:31:19.494216');
INSERT INTO `django_migrations` VALUES (166,'wagtailcore','0009_remove_auto_now_add_from_pagerevision_created_at','2024-10-08 14:31:19.505222');
INSERT INTO `django_migrations` VALUES (167,'wagtailcore','0010_change_page_owner_to_null_on_delete','2024-10-08 14:31:19.516291');
INSERT INTO `django_migrations` VALUES (168,'wagtailcore','0011_page_first_published_at','2024-10-08 14:31:19.527373');
INSERT INTO `django_migrations` VALUES (169,'wagtailcore','0012_extend_page_slug_field','2024-10-08 14:31:19.538415');
INSERT INTO `django_migrations` VALUES (170,'wagtailcore','0013_update_golive_expire_help_text','2024-10-08 14:31:19.549529');
INSERT INTO `django_migrations` VALUES (171,'wagtailcore','0014_add_verbose_name','2024-10-08 14:31:19.560585');
INSERT INTO `django_migrations` VALUES (172,'wagtailcore','0015_add_more_verbose_names','2024-10-08 14:31:19.571726');
INSERT INTO `django_migrations` VALUES (173,'wagtailcore','0016_change_page_url_path_to_text_field','2024-10-08 14:31:19.582737');
INSERT INTO `django_migrations` VALUES (174,'wagtailcore','0017_change_edit_page_permission_description','2024-10-08 14:31:22.724617');
INSERT INTO `django_migrations` VALUES (175,'wagtailcore','0018_pagerevision_submitted_for_moderation_index','2024-10-08 14:31:22.862816');
INSERT INTO `django_migrations` VALUES (176,'wagtailcore','0019_verbose_names_cleanup','2024-10-08 14:31:22.941546');
INSERT INTO `django_migrations` VALUES (177,'wagtailcore','0020_add_index_on_page_first_published_at','2024-10-08 14:31:23.079296');
INSERT INTO `django_migrations` VALUES (178,'wagtailcore','0021_capitalizeverbose','2024-10-08 14:31:26.939709');
INSERT INTO `django_migrations` VALUES (179,'wagtailcore','0022_add_site_name','2024-10-08 14:31:27.018427');
INSERT INTO `django_migrations` VALUES (180,'wagtailcore','0023_alter_page_revision_on_delete_behaviour','2024-10-08 14:31:27.482291');
INSERT INTO `django_migrations` VALUES (181,'wagtailcore','0024_collection','2024-10-08 14:31:27.683642');
INSERT INTO `django_migrations` VALUES (182,'wagtailcore','0025_collection_initial_data','2024-10-08 14:31:28.036079');
INSERT INTO `django_migrations` VALUES (183,'wagtailcore','0026_group_collection_permission','2024-10-08 14:31:28.334930');
INSERT INTO `django_migrations` VALUES (184,'wagtailcore','0027_fix_collection_path_collation','2024-10-08 14:31:30.008512');
INSERT INTO `django_migrations` VALUES (185,'wagtailcore','0024_alter_page_content_type_on_delete_behaviour','2024-10-08 14:31:30.594931');
INSERT INTO `django_migrations` VALUES (186,'wagtailcore','0028_merge','2024-10-08 14:31:30.605778');
INSERT INTO `django_migrations` VALUES (187,'wagtailcore','0029_unicode_slugfield_dj19','2024-10-08 14:31:30.655416');
INSERT INTO `django_migrations` VALUES (188,'wagtailcore','0030_index_on_pagerevision_created_at','2024-10-08 14:31:30.893683');
INSERT INTO `django_migrations` VALUES (189,'wagtailcore','0031_add_page_view_restriction_types','2024-10-08 14:31:31.230523');
INSERT INTO `django_migrations` VALUES (190,'wagtailcore','0032_add_bulk_delete_page_permission','2024-10-08 14:31:32.659541');
INSERT INTO `django_migrations` VALUES (191,'wagtailcore','0033_remove_golive_expiry_help_text','2024-10-08 14:31:32.704053');
INSERT INTO `django_migrations` VALUES (192,'wagtailcore','0034_page_live_revision','2024-10-08 14:31:32.895539');
INSERT INTO `django_migrations` VALUES (193,'wagtailcore','0035_page_last_published_at','2024-10-08 14:31:33.520043');
INSERT INTO `django_migrations` VALUES (194,'wagtailcore','0036_populate_page_last_published_at','2024-10-08 14:31:33.619460');
INSERT INTO `django_migrations` VALUES (195,'wagtailcore','0037_set_page_owner_editable','2024-10-08 14:31:34.238757');
INSERT INTO `django_migrations` VALUES (196,'wagtailcore','0038_make_first_published_at_editable','2024-10-08 14:31:34.265399');
INSERT INTO `django_migrations` VALUES (197,'wagtailcore','0039_collectionviewrestriction','2024-10-08 14:31:35.597127');
INSERT INTO `django_migrations` VALUES (198,'wagtailcore','0040_page_draft_title','2024-10-08 14:31:38.634728');
INSERT INTO `django_migrations` VALUES (199,'wagtailcore','0041_group_collection_permissions_verbose_name_plural','2024-10-08 14:31:38.660061');
INSERT INTO `django_migrations` VALUES (200,'wagtailcore','0042_index_on_pagerevision_approved_go_live_at','2024-10-08 14:31:38.845069');
INSERT INTO `django_migrations` VALUES (201,'wagtailcore','0043_lock_fields','2024-10-08 14:31:39.019732');
INSERT INTO `django_migrations` VALUES (202,'wagtailcore','0044_add_unlock_grouppagepermission','2024-10-08 14:31:39.715015');
INSERT INTO `django_migrations` VALUES (203,'wagtailcore','0045_assign_unlock_grouppagepermission','2024-10-08 14:31:39.849135');
INSERT INTO `django_migrations` VALUES (204,'wagtailcore','0046_site_name_remove_null','2024-10-08 14:31:40.317199');
INSERT INTO `django_migrations` VALUES (205,'wagtailcore','0047_add_workflow_models','2024-10-08 14:31:41.768468');
INSERT INTO `django_migrations` VALUES (206,'wagtailcore','0048_add_default_workflows','2024-10-08 14:31:50.385994');
INSERT INTO `django_migrations` VALUES (207,'wagtailcore','0049_taskstate_finished_by','2024-10-08 14:31:50.470919');
INSERT INTO `django_migrations` VALUES (208,'wagtailcore','0050_workflow_rejected_to_needs_changes','2024-10-08 14:31:51.007861');
INSERT INTO `django_migrations` VALUES (209,'wagtailcore','0051_taskstate_comment','2024-10-08 14:31:51.096205');
INSERT INTO `django_migrations` VALUES (210,'wagtailcore','0052_pagelogentry','2024-10-08 14:31:51.251857');
INSERT INTO `django_migrations` VALUES (211,'wagtailcore','0053_locale_model','2024-10-08 14:31:52.326970');
INSERT INTO `django_migrations` VALUES (212,'wagtailcore','0054_initial_locale','2024-10-08 14:31:52.707699');
INSERT INTO `django_migrations` VALUES (213,'wagtailcore','0055_page_locale_fields','2024-10-08 14:31:53.010462');
INSERT INTO `django_migrations` VALUES (214,'wagtailcore','0056_page_locale_fields_populate','2024-10-08 14:31:53.631479');
INSERT INTO `django_migrations` VALUES (215,'wagtailcore','0057_page_locale_fields_notnull','2024-10-08 14:31:55.260201');
INSERT INTO `django_migrations` VALUES (216,'wagtailcore','0058_page_alias_of','2024-10-08 14:31:55.350343');
INSERT INTO `django_migrations` VALUES (217,'wagtailcore','0059_apply_collection_ordering','2024-10-08 14:31:56.221742');
INSERT INTO `django_migrations` VALUES (232,'sessions','0001_initial','2024-10-08 14:32:13.262291');
INSERT INTO `django_migrations` VALUES (233,'sites','0001_initial','2024-10-08 14:32:13.512740');
INSERT INTO `django_migrations` VALUES (234,'sites','0002_alter_domain_unique','2024-10-08 14:32:13.879075');
INSERT INTO `django_migrations` VALUES (235,'taggit','0001_initial','2024-10-08 14:32:14.200604');
INSERT INTO `django_migrations` VALUES (236,'taggit','0002_auto_20150616_2121','2024-10-08 14:32:15.218932');
INSERT INTO `django_migrations` VALUES (237,'taggit','0003_taggeditem_add_unique_index','2024-10-08 14:32:15.358711');
INSERT INTO `django_migrations` VALUES (238,'wagtailadmin','0001_create_admin_access_permissions','2024-10-08 14:32:15.506766');
INSERT INTO `django_migrations` VALUES (239,'wagtailadmin','0002_admin','2024-10-08 14:32:15.532710');
INSERT INTO `django_migrations` VALUES (240,'wagtailadmin','0003_admin_managed','2024-10-08 14:32:15.681134');
INSERT INTO `django_migrations` VALUES (241,'wagtailcore','0060_fix_workflow_unique_constraint','2024-10-08 14:32:15.757193');
INSERT INTO `django_migrations` VALUES (242,'wagtailcore','0061_change_promote_tab_helpt_text_and_verbose_names','2024-10-08 14:32:15.839281');
INSERT INTO `django_migrations` VALUES (243,'wagtailcore','0062_comment_models_and_pagesubscription','2024-10-08 14:32:16.581775');
INSERT INTO `django_migrations` VALUES (244,'wagtaildocs','0001_initial','2024-10-08 14:32:20.382135');
INSERT INTO `django_migrations` VALUES (245,'wagtaildocs','0002_initial_data','2024-10-08 14:32:20.956423');
INSERT INTO `django_migrations` VALUES (246,'wagtaildocs','0003_add_verbose_names','2024-10-08 14:32:21.439375');
INSERT INTO `django_migrations` VALUES (247,'wagtaildocs','0004_capitalizeverbose','2024-10-08 14:32:22.081739');
INSERT INTO `django_migrations` VALUES (248,'wagtaildocs','0005_document_collection','2024-10-08 14:32:22.262587');
INSERT INTO `django_migrations` VALUES (249,'wagtaildocs','0006_copy_document_permissions_to_collections','2024-10-08 14:32:22.723924');
INSERT INTO `django_migrations` VALUES (250,'wagtaildocs','0005_alter_uploaded_by_user_on_delete_action','2024-10-08 14:32:23.182159');
INSERT INTO `django_migrations` VALUES (251,'wagtaildocs','0007_merge','2024-10-08 14:32:23.192940');
INSERT INTO `django_migrations` VALUES (252,'wagtaildocs','0008_document_file_size','2024-10-08 14:32:23.294170');
INSERT INTO `django_migrations` VALUES (253,'wagtaildocs','0009_document_verbose_name_plural','2024-10-08 14:32:23.348957');
INSERT INTO `django_migrations` VALUES (254,'wagtaildocs','0010_document_file_hash','2024-10-08 14:32:23.481497');
INSERT INTO `django_migrations` VALUES (255,'wagtaildocs','0011_add_choose_permissions','2024-10-08 14:32:24.067895');
INSERT INTO `django_migrations` VALUES (256,'wagtaildocs','0012_uploadeddocument','2024-10-08 14:32:24.248466');
INSERT INTO `django_migrations` VALUES (257,'wagtailembeds','0001_initial','2024-10-08 14:32:24.787699');
INSERT INTO `django_migrations` VALUES (258,'wagtailembeds','0002_add_verbose_names','2024-10-08 14:32:24.804682');
INSERT INTO `django_migrations` VALUES (259,'wagtailembeds','0003_capitalizeverbose','2024-10-08 14:32:24.826425');
INSERT INTO `django_migrations` VALUES (260,'wagtailembeds','0004_embed_verbose_name_plural','2024-10-08 14:32:24.848521');
INSERT INTO `django_migrations` VALUES (261,'wagtailembeds','0005_specify_thumbnail_url_max_length','2024-10-08 14:32:24.920349');
INSERT INTO `django_migrations` VALUES (262,'wagtailembeds','0006_add_embed_hash','2024-10-08 14:32:25.021621');
INSERT INTO `django_migrations` VALUES (263,'wagtailembeds','0007_populate_hash','2024-10-08 14:32:25.147542');
INSERT INTO `django_migrations` VALUES (264,'wagtailembeds','0008_allow_long_urls','2024-10-08 14:32:26.249395');
INSERT INTO `django_migrations` VALUES (265,'wagtailforms','0001_initial','2024-10-08 14:32:26.431085');
INSERT INTO `django_migrations` VALUES (266,'wagtailforms','0002_add_verbose_names','2024-10-08 14:32:26.779124');
INSERT INTO `django_migrations` VALUES (267,'wagtailforms','0003_capitalizeverbose','2024-10-08 14:32:26.827626');
INSERT INTO `django_migrations` VALUES (268,'wagtailforms','0004_add_verbose_name_plural','2024-10-08 14:32:26.859803');
INSERT INTO `django_migrations` VALUES (269,'wagtailimages','0001_initial','2024-10-08 14:32:27.740173');
INSERT INTO `django_migrations` VALUES (270,'wagtailimages','0002_initial_data','2024-10-08 14:32:27.754885');
INSERT INTO `django_migrations` VALUES (271,'wagtailimages','0003_fix_focal_point_fields','2024-10-08 14:32:27.765887');
INSERT INTO `django_migrations` VALUES (272,'wagtailimages','0004_make_focal_point_key_not_nullable','2024-10-08 14:32:27.776926');
INSERT INTO `django_migrations` VALUES (273,'wagtailimages','0005_make_filter_spec_unique','2024-10-08 14:32:27.787985');
INSERT INTO `django_migrations` VALUES (274,'wagtailimages','0006_add_verbose_names','2024-10-08 14:32:27.799107');
INSERT INTO `django_migrations` VALUES (275,'wagtailimages','0007_image_file_size','2024-10-08 14:32:27.810117');
INSERT INTO `django_migrations` VALUES (276,'wagtailimages','0008_image_created_at_index','2024-10-08 14:32:27.821208');
INSERT INTO `django_migrations` VALUES (277,'wagtailimages','0009_capitalizeverbose','2024-10-08 14:32:27.832272');
INSERT INTO `django_migrations` VALUES (278,'wagtailimages','0010_change_on_delete_behaviour','2024-10-08 14:32:27.843305');
INSERT INTO `django_migrations` VALUES (279,'wagtailimages','0011_image_collection','2024-10-08 14:32:27.854439');
INSERT INTO `django_migrations` VALUES (280,'wagtailimages','0012_copy_image_permissions_to_collections','2024-10-08 14:32:27.865511');
INSERT INTO `django_migrations` VALUES (281,'wagtailimages','0013_make_rendition_upload_callable','2024-10-08 14:32:27.876580');
INSERT INTO `django_migrations` VALUES (282,'wagtailimages','0014_add_filter_spec_field','2024-10-08 14:32:27.887587');
INSERT INTO `django_migrations` VALUES (283,'wagtailimages','0015_fill_filter_spec_field','2024-10-08 14:32:27.909814');
INSERT INTO `django_migrations` VALUES (284,'wagtailimages','0016_deprecate_rendition_filter_relation','2024-10-08 14:32:27.920884');
INSERT INTO `django_migrations` VALUES (285,'wagtailimages','0017_reduce_focal_point_key_max_length','2024-10-08 14:32:27.931932');
INSERT INTO `django_migrations` VALUES (286,'wagtailimages','0018_remove_rendition_filter','2024-10-08 14:32:27.942992');
INSERT INTO `django_migrations` VALUES (287,'wagtailimages','0019_delete_filter','2024-10-08 14:32:27.954122');
INSERT INTO `django_migrations` VALUES (288,'wagtailimages','0020_add-verbose-name','2024-10-08 14:32:27.965129');
INSERT INTO `django_migrations` VALUES (289,'wagtailimages','0021_image_file_hash','2024-10-08 14:32:27.976192');
INSERT INTO `django_migrations` VALUES (290,'wagtailimages','0022_uploadedimage','2024-10-08 14:32:29.674862');
INSERT INTO `django_migrations` VALUES (291,'wagtailimages','0023_add_choose_permissions','2024-10-08 14:32:30.302585');
INSERT INTO `django_migrations` VALUES (292,'wagtailredirects','0001_initial','2024-10-08 14:32:30.608926');
INSERT INTO `django_migrations` VALUES (293,'wagtailredirects','0002_add_verbose_names','2024-10-08 14:32:31.893537');
INSERT INTO `django_migrations` VALUES (294,'wagtailredirects','0003_make_site_field_editable','2024-10-08 14:32:32.967584');
INSERT INTO `django_migrations` VALUES (295,'wagtailredirects','0004_set_unique_on_path_and_site','2024-10-08 14:32:33.288318');
INSERT INTO `django_migrations` VALUES (296,'wagtailredirects','0005_capitalizeverbose','2024-10-08 14:32:34.396427');
INSERT INTO `django_migrations` VALUES (297,'wagtailredirects','0006_redirect_increase_max_length','2024-10-08 14:32:34.484821');
INSERT INTO `django_migrations` VALUES (298,'wagtailsearch','0001_initial','2024-10-08 14:32:35.189489');
INSERT INTO `django_migrations` VALUES (299,'wagtailsearch','0002_add_verbose_names','2024-10-08 14:32:37.004356');
INSERT INTO `django_migrations` VALUES (300,'wagtailsearch','0003_remove_editors_pick','2024-10-08 14:32:37.091392');
INSERT INTO `django_migrations` VALUES (301,'wagtailsearch','0004_querydailyhits_verbose_name_plural','2024-10-08 14:32:37.127096');
INSERT INTO `django_migrations` VALUES (302,'wagtailusers','0001_initial','2024-10-08 14:32:37.342371');
INSERT INTO `django_migrations` VALUES (303,'wagtailusers','0002_add_verbose_name_on_userprofile','2024-10-08 14:32:37.907489');
INSERT INTO `django_migrations` VALUES (304,'wagtailusers','0003_add_verbose_names','2024-10-08 14:32:37.958661');
INSERT INTO `django_migrations` VALUES (305,'wagtailusers','0004_capitalizeverbose','2024-10-08 14:32:38.095469');
INSERT INTO `django_migrations` VALUES (306,'wagtailusers','0005_make_related_name_wagtail_specific','2024-10-08 14:32:38.554425');
INSERT INTO `django_migrations` VALUES (307,'wagtailusers','0006_userprofile_prefered_language','2024-10-08 14:32:38.694992');
INSERT INTO `django_migrations` VALUES (308,'wagtailusers','0007_userprofile_current_time_zone','2024-10-08 14:32:38.838628');
INSERT INTO `django_migrations` VALUES (309,'wagtailusers','0008_userprofile_avatar','2024-10-08 14:32:38.971584');
INSERT INTO `django_migrations` VALUES (310,'wagtailusers','0009_userprofile_verbose_name_plural','2024-10-08 14:32:39.017504');
INSERT INTO `django_migrations` VALUES (311,'wagtailusers','0010_userprofile_updated_comments_notifications','2024-10-08 14:32:39.149162');
INSERT INTO `django_migrations` VALUES (312,'wagtailimages','0001_squashed_0021','2024-10-08 14:32:39.173391');
INSERT INTO `django_migrations` VALUES (313,'wagtailcore','0001_squashed_0016_change_page_url_path_to_text_field','2024-10-08 14:32:39.190656');
INSERT INTO `django_migrations` VALUES (316,'auth','0012_alter_user_first_name_max_length','2025-06-20 14:09:46.592069');
INSERT INTO `django_migrations` VALUES (317,'authtoken','0004_alter_tokenproxy_options','2025-06-20 14:09:46.599980');
INSERT INTO `django_migrations` VALUES (322,'oauth2_provider','0008_alter_accesstoken_token','2025-06-20 14:09:47.910686');
INSERT INTO `django_migrations` VALUES (323,'oauth2_provider','0009_add_hash_client_secret','2025-06-20 14:09:47.953509');
INSERT INTO `django_migrations` VALUES (324,'oauth2_provider','0010_application_allowed_origins','2025-06-20 14:09:47.992382');
INSERT INTO `django_migrations` VALUES (325,'oauth2_provider','0011_refreshtoken_token_family','2025-06-20 14:09:48.248507');
INSERT INTO `django_migrations` VALUES (326,'oauth2_provider','0012_add_token_checksum','2025-06-20 14:09:49.043991');
INSERT INTO `django_migrations` VALUES (328,'taggit','0004_alter_taggeditem_content_type_alter_taggeditem_tag','2025-06-20 14:09:49.325032');
INSERT INTO `django_migrations` VALUES (329,'taggit','0005_auto_20220424_2025','2025-06-20 14:09:49.410045');
INSERT INTO `django_migrations` VALUES (330,'wagtailcore','0063_modellogentry','2025-06-20 14:09:49.579205');
INSERT INTO `django_migrations` VALUES (331,'wagtailcore','0064_log_timestamp_indexes','2025-06-20 14:09:49.899205');
INSERT INTO `django_migrations` VALUES (332,'wagtailcore','0065_log_entry_uuid','2025-06-20 14:09:49.991972');
INSERT INTO `django_migrations` VALUES (333,'wagtailcore','0066_collection_management_permissions','2025-06-20 14:09:50.082760');
INSERT INTO `django_migrations` VALUES (334,'wagtailcore','0067_alter_pagerevision_content_json','2025-06-20 14:09:50.201815');
INSERT INTO `django_migrations` VALUES (335,'wagtailcore','0068_log_entry_empty_object','2025-06-20 14:09:50.298473');
INSERT INTO `django_migrations` VALUES (336,'wagtailcore','0069_log_entry_jsonfield','2025-06-20 14:09:50.540644');
INSERT INTO `django_migrations` VALUES (337,'wagtailcore','0070_rename_pagerevision_revision','2025-06-20 14:09:51.553959');
INSERT INTO `django_migrations` VALUES (338,'wagtailcore','0071_populate_revision_content_type','2025-06-20 14:09:51.635486');
INSERT INTO `django_migrations` VALUES (339,'wagtailcore','0072_alter_revision_content_type_notnull','2025-06-20 14:09:51.929605');
INSERT INTO `django_migrations` VALUES (340,'wagtailcore','0073_page_latest_revision','2025-06-20 14:09:52.050696');
INSERT INTO `django_migrations` VALUES (341,'wagtailcore','0074_revision_object_str','2025-06-20 14:09:52.094384');
INSERT INTO `django_migrations` VALUES (342,'wagtailcore','0075_populate_latest_revision_and_revision_object_str','2025-06-20 14:09:52.495222');
INSERT INTO `django_migrations` VALUES (343,'wagtailcore','0076_modellogentry_revision','2025-06-20 14:09:52.584403');
INSERT INTO `django_migrations` VALUES (344,'wagtailcore','0077_alter_revision_user','2025-06-20 14:09:52.656197');
INSERT INTO `django_migrations` VALUES (345,'wagtailcore','0078_referenceindex','2025-06-20 14:09:52.840370');
INSERT INTO `django_migrations` VALUES (346,'wagtailcore','0079_rename_taskstate_page_revision','2025-06-20 14:09:52.936745');
INSERT INTO `django_migrations` VALUES (347,'wagtailcore','0080_generic_workflowstate','2025-06-20 14:09:53.748841');
INSERT INTO `django_migrations` VALUES (348,'wagtailcore','0081_populate_workflowstate_content_type','2025-06-20 14:09:53.830268');
INSERT INTO `django_migrations` VALUES (349,'wagtailcore','0082_alter_workflowstate_content_type_notnull','2025-06-20 14:09:54.128430');
INSERT INTO `django_migrations` VALUES (350,'wagtailcore','0083_workflowcontenttype','2025-06-20 14:09:54.264769');
INSERT INTO `django_migrations` VALUES (351,'wagtailcore','0084_add_default_page_permissions','2025-06-20 14:09:54.309021');
INSERT INTO `django_migrations` VALUES (352,'wagtailcore','0085_add_grouppagepermission_permission','2025-06-20 14:09:54.470012');
INSERT INTO `django_migrations` VALUES (353,'wagtailcore','0086_populate_grouppagepermission_permission','2025-06-20 14:09:54.917029');
INSERT INTO `django_migrations` VALUES (354,'wagtailcore','0087_alter_grouppagepermission_unique_together_and_more','2025-06-20 14:09:55.115242');
INSERT INTO `django_migrations` VALUES (355,'wagtailcore','0088_fix_log_entry_json_timestamps','2025-06-20 14:09:55.283188');
INSERT INTO `django_migrations` VALUES (356,'wagtailcore','0089_log_entry_data_json_null_to_object','2025-06-20 14:09:55.370347');
INSERT INTO `django_migrations` VALUES (357,'wagtailembeds','0009_embed_cache_until','2025-06-20 14:09:55.394645');
INSERT INTO `django_migrations` VALUES (358,'wagtailforms','0005_alter_formsubmission_form_data','2025-06-20 14:09:55.444736');
INSERT INTO `django_migrations` VALUES (359,'wagtailimages','0024_index_image_file_hash','2025-06-20 14:09:55.496813');
INSERT INTO `django_migrations` VALUES (360,'wagtailimages','0025_alter_image_file_alter_rendition_file','2025-06-20 14:09:55.540456');
INSERT INTO `django_migrations` VALUES (361,'wagtailredirects','0007_add_autocreate_fields','2025-06-20 14:09:55.633871');
INSERT INTO `django_migrations` VALUES (362,'wagtailredirects','0008_add_verbose_name_plural','2025-06-20 14:09:55.667612');
INSERT INTO `django_migrations` VALUES (363,'wagtailsearch','0005_create_indexentry','2025-06-20 14:09:55.844624');
INSERT INTO `django_migrations` VALUES (364,'wagtailsearch','0006_customise_indexentry','2025-06-20 14:09:56.065356');
INSERT INTO `django_migrations` VALUES (365,'wagtailsearch','0007_delete_editorspick','2025-06-20 14:09:56.079494');
INSERT INTO `django_migrations` VALUES (366,'wagtailusers','0011_userprofile_dismissibles','2025-06-20 14:09:56.370297');
INSERT INTO `django_migrations` VALUES (367,'wagtailusers','0012_userprofile_theme','2025-06-20 14:09:56.412410');
INSERT INTO `django_migrations` VALUES (368,'website','0001_initial','2025-06-20 14:09:56.543154');
INSERT INTO `django_migrations` VALUES (369,'website','0002_medienspiegel_url','2025-06-20 14:09:56.559102');
INSERT INTO `django_migrations` VALUES (370,'website','0003_auto_20200205_1148','2025-06-20 14:09:56.566533');
INSERT INTO `django_migrations` VALUES (371,'website','0004_auto_20201102_1614','2025-06-20 14:09:56.632856');
INSERT INTO `django_migrations` VALUES (372,'website','0005_websitepage','2025-06-20 14:09:56.743879');
INSERT INTO `django_migrations` VALUES (373,'website','0006_auto_20220811_1214','2025-06-20 14:09:56.763791');
INSERT INTO `django_migrations` VALUES (374,'website','0007_websitemainpage','2025-06-20 14:09:56.892729');
INSERT INTO `django_migrations` VALUES (375,'filer','0001_squashed_0016_alter_folder_index_together_remove_folder_level_and_more','2025-06-20 14:09:56.902938');
INSERT INTO `django_migrations` VALUES (379,'geno','0001_initial','2025-08-22 15:02:06.249970');
INSERT INTO `django_migrations` VALUES (380,'credit_accounting','0001_initial','2025-08-22 15:02:06.261586');
INSERT INTO `django_migrations` VALUES (381,'credit_accounting','0002_initial','2025-08-22 15:02:06.832547');
INSERT INTO `django_migrations` VALUES (382,'portal','0001_initial','2025-08-22 15:02:07.006540');
INSERT INTO `django_migrations` VALUES (383,'report','0001_initial','2025-08-22 15:02:07.033545');
INSERT INTO `django_migrations` VALUES (384,'reservation','0001_initial','2025-08-22 15:02:08.020918');
INSERT INTO `django_migrations` VALUES (385,'geno','0002_contenttemplateoptiontype','2025-08-23 09:02:54.989257');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djangosaml2idp_persistentid`
--

DROP TABLE IF EXISTS `djangosaml2idp_persistentid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `djangosaml2idp_persistentid` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `persistent_id` char(32) NOT NULL,
  `created` datetime(6) NOT NULL,
  `sp_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_ids_per_sp` (`sp_id`,`persistent_id`),
  UNIQUE KEY `unique_users_per_sp` (`sp_id`,`user_id`),
  KEY `djangosaml2idp_persistentid_user_id_b2f3e033_fk_auth_user_id` (`user_id`),
  CONSTRAINT `djangosaml2idp_persi_sp_id_83e91899_fk_djangosam` FOREIGN KEY (`sp_id`) REFERENCES `djangosaml2idp_serviceprovider` (`id`),
  CONSTRAINT `djangosaml2idp_persistentid_user_id_b2f3e033_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djangosaml2idp_persistentid`
--

LOCK TABLES `djangosaml2idp_persistentid` WRITE;
/*!40000 ALTER TABLE `djangosaml2idp_persistentid` DISABLE KEYS */;
/*!40000 ALTER TABLE `djangosaml2idp_persistentid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djangosaml2idp_serviceprovider`
--

DROP TABLE IF EXISTS `djangosaml2idp_serviceprovider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `djangosaml2idp_serviceprovider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt_created` datetime(6) NOT NULL,
  `dt_updated` datetime(6) DEFAULT NULL,
  `entity_id` varchar(255) NOT NULL,
  `pretty_name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `metadata_expiration_dt` datetime(6) NOT NULL,
  `remote_metadata_url` varchar(512) NOT NULL,
  `local_metadata` longtext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `_processor` varchar(256) NOT NULL,
  `_attribute_mapping` longtext NOT NULL,
  `_nameid_field` varchar(64) NOT NULL,
  `_sign_response` tinyint(1) DEFAULT NULL,
  `_sign_assertion` tinyint(1) DEFAULT NULL,
  `_signing_algorithm` varchar(256) DEFAULT NULL,
  `_digest_algorithm` varchar(256) DEFAULT NULL,
  `_encrypt_saml_responses` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entity_id` (`entity_id`),
  KEY `djangosaml2_entity__5fb9e3_idx` (`entity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djangosaml2idp_serviceprovider`
--

LOCK TABLES `djangosaml2idp_serviceprovider` WRITE;
/*!40000 ALTER TABLE `djangosaml2idp_serviceprovider` DISABLE KEYS */;
/*!40000 ALTER TABLE `djangosaml2idp_serviceprovider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `easy_thumbnails_source`
--

DROP TABLE IF EXISTS `easy_thumbnails_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `easy_thumbnails_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `storage_hash` varchar(40) NOT NULL,
  `name` varchar(255) NOT NULL,
  `modified` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `easy_thumbnails_source_storage_hash_name_481ce32d_uniq` (`storage_hash`,`name`),
  KEY `easy_thumbnails_source_storage_hash_946cbcc9` (`storage_hash`),
  KEY `easy_thumbnails_source_name_5fe0edc6` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `easy_thumbnails_source`
--

LOCK TABLES `easy_thumbnails_source` WRITE;
/*!40000 ALTER TABLE `easy_thumbnails_source` DISABLE KEYS */;
INSERT INTO `easy_thumbnails_source` VALUES (1,'607e709bca51931a31f854e2efe70821','ee/b5/eeb5be15-0ef2-4342-adf0-89ec426c28ab/cohiva-demo_rechnung_allgemein.odt','2024-11-06 16:32:41.676253');
INSERT INTO `easy_thumbnails_source` VALUES (2,'607e709bca51931a31f854e2efe70821','67/5e/675eee00-3298-4d50-8de8-38dd2851ad69/cohiva-demo_brief_bestatigung_mitgliedschaft.odt','2024-12-03 11:16:01.614550');
INSERT INTO `easy_thumbnails_source` VALUES (3,'607e709bca51931a31f854e2efe70821','6f/bb/6fbbaf6c-5e6f-4ef5-a611-63452a7d1fee/cohiva-demo_brief_bestatigung_mitgliedschaft.odt','2024-12-03 11:19:25.754820');
INSERT INTO `easy_thumbnails_source` VALUES (4,'607e709bca51931a31f854e2efe70821','5d/40/5d406747-3482-48c4-a393-b2750172e46b/cohiva-demo_kontoauszug.odt','2024-12-03 14:42:51.071468');
INSERT INTO `easy_thumbnails_source` VALUES (5,'607e709bca51931a31f854e2efe70821','b8/86/b886764b-45e2-461c-a72f-388b846ad7f6/cohiva-demo_einladunggv.pdf','2024-12-04 09:43:28.536500');
INSERT INTO `easy_thumbnails_source` VALUES (6,'607e709bca51931a31f854e2efe70821','57/b0/57b0885e-9848-43a9-bda3-2cadbb8ccfd3/cohiva-demo_formular_uberprufungbelegungsrichtlinien.odt','2024-12-04 10:01:04.680728');
INSERT INTO `easy_thumbnails_source` VALUES (7,'607e709bca51931a31f854e2efe70821','c1/42/c142333d-dffe-4dfd-80ab-b785e701fff1/cohiva-demo_formular_uberprufungbelegungsrichtlinien.odt','2024-12-04 10:05:19.887428');
INSERT INTO `easy_thumbnails_source` VALUES (8,'607e709bca51931a31f854e2efe70821','26/90/26905a0e-8173-4687-b341-531a76766fb2/cohiva-demo_brief_bestatigung_mitgliedschaft-1.odt','2025-09-03 13:06:42.463775');
/*!40000 ALTER TABLE `easy_thumbnails_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `easy_thumbnails_thumbnail`
--

DROP TABLE IF EXISTS `easy_thumbnails_thumbnail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `easy_thumbnails_thumbnail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `storage_hash` varchar(40) NOT NULL,
  `name` varchar(255) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `easy_thumbnails_thumbnai_storage_hash_name_source_fb375270_uniq` (`storage_hash`,`name`,`source_id`),
  KEY `easy_thumbnails_thum_source_id_5b57bc77_fk_easy_thum` (`source_id`),
  KEY `easy_thumbnails_thumbnail_storage_hash_f1435f49` (`storage_hash`),
  KEY `easy_thumbnails_thumbnail_name_b5882c31` (`name`),
  CONSTRAINT `easy_thumbnails_thum_source_id_5b57bc77_fk_easy_thum` FOREIGN KEY (`source_id`) REFERENCES `easy_thumbnails_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `easy_thumbnails_thumbnail`
--

LOCK TABLES `easy_thumbnails_thumbnail` WRITE;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnail` DISABLE KEYS */;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `easy_thumbnails_thumbnaildimensions`
--

DROP TABLE IF EXISTS `easy_thumbnails_thumbnaildimensions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `easy_thumbnails_thumbnaildimensions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thumbnail_id` int(11) NOT NULL,
  `width` int(10) unsigned DEFAULT NULL,
  `height` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `thumbnail_id` (`thumbnail_id`),
  CONSTRAINT `easy_thumbnails_thum_thumbnail_id_c3a0c549_fk_easy_thum` FOREIGN KEY (`thumbnail_id`) REFERENCES `easy_thumbnails_thumbnail` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `easy_thumbnails_thumbnaildimensions`
--

LOCK TABLES `easy_thumbnails_thumbnaildimensions` WRITE;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnaildimensions` DISABLE KEYS */;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnaildimensions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_clipboard`
--

DROP TABLE IF EXISTS `filer_clipboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_clipboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `filer_clipboard_user_id_b52ff0bc_fk_auth_user_id` (`user_id`),
  CONSTRAINT `filer_clipboard_user_id_b52ff0bc_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_clipboard`
--

LOCK TABLES `filer_clipboard` WRITE;
/*!40000 ALTER TABLE `filer_clipboard` DISABLE KEYS */;
INSERT INTO `filer_clipboard` VALUES (1,2);
/*!40000 ALTER TABLE `filer_clipboard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_clipboarditem`
--

DROP TABLE IF EXISTS `filer_clipboarditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_clipboarditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `clipboard_id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `filer_clipboarditem_clipboard_id_7a76518b_fk_filer_clipboard_id` (`clipboard_id`),
  KEY `filer_clipboarditem_file_id_06196f80_fk_filer_file_id` (`file_id`),
  CONSTRAINT `filer_clipboarditem_clipboard_id_7a76518b_fk_filer_clipboard_id` FOREIGN KEY (`clipboard_id`) REFERENCES `filer_clipboard` (`id`),
  CONSTRAINT `filer_clipboarditem_file_id_06196f80_fk_filer_file_id` FOREIGN KEY (`file_id`) REFERENCES `filer_file` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_clipboarditem`
--

LOCK TABLES `filer_clipboarditem` WRITE;
/*!40000 ALTER TABLE `filer_clipboarditem` DISABLE KEYS */;
/*!40000 ALTER TABLE `filer_clipboarditem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_file`
--

DROP TABLE IF EXISTS `filer_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file` varchar(255) DEFAULT NULL,
  `_file_size` bigint(20) DEFAULT NULL,
  `sha1` varchar(40) NOT NULL,
  `has_all_mandatory_data` tinyint(1) NOT NULL,
  `original_filename` varchar(255) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `modified_at` datetime(6) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  `folder_id` int(11) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `polymorphic_ctype_id` int(11) DEFAULT NULL,
  `mime_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `filer_file_folder_id_af803bbb_fk_filer_folder_id` (`folder_id`),
  KEY `filer_file_owner_id_b9e32671_fk_auth_user_id` (`owner_id`),
  KEY `filer_file_polymorphic_ctype_id_f44903c1_fk_django_co` (`polymorphic_ctype_id`),
  CONSTRAINT `filer_file_folder_id_af803bbb_fk_filer_folder_id` FOREIGN KEY (`folder_id`) REFERENCES `filer_folder` (`id`),
  CONSTRAINT `filer_file_owner_id_b9e32671_fk_auth_user_id` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `filer_file_polymorphic_ctype_id_f44903c1_fk_django_co` FOREIGN KEY (`polymorphic_ctype_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_file`
--

LOCK TABLES `filer_file` WRITE;
/*!40000 ALTER TABLE `filer_file` DISABLE KEYS */;
INSERT INTO `filer_file` VALUES (1,'ee/b5/eeb5be15-0ef2-4342-adf0-89ec426c28ab/cohiva-demo_rechnung_allgemein.odt',39862,'f42f09f0d1a7985e147283da1301f21c61ddf804',0,'Cohiva-Demo_Rechnung_Allgemein.odt','',NULL,'2024-11-06 16:32:41.695149','2024-11-06 16:32:41.695189',0,2,2,40,'application/vnd.oasis.opendocument.text');
INSERT INTO `filer_file` VALUES (2,'26/90/26905a0e-8173-4687-b341-531a76766fb2/cohiva-demo_brief_bestatigung_mitgliedschaft-1.odt',35123,'1a22558a5b0b453b0da0d05369631c113e9c5224',0,'Cohiva-Demo_Brief_Bestätigung_Mitgliedschaft.odt','','','2024-12-03 11:16:01.617940','2025-09-03 13:06:42.465975',0,3,2,40,'application/vnd.oasis.opendocument.text');
INSERT INTO `filer_file` VALUES (3,'5d/40/5d406747-3482-48c4-a393-b2750172e46b/cohiva-demo_kontoauszug.odt',48247,'8ffadfd1076178a24131cfa8337dc17df2851c9c',0,'Cohiva-Demo_Kontoauszug.odt','',NULL,'2024-12-03 14:42:51.074752','2024-12-03 14:42:51.074775',0,4,2,40,'application/vnd.oasis.opendocument.text');
INSERT INTO `filer_file` VALUES (4,'b8/86/b886764b-45e2-461c-a72f-388b846ad7f6/cohiva-demo_einladunggv.pdf',35095,'2653d412b5d1740e1e47e166d829b899e94cad20',0,'Cohiva-Demo_EinladungGV.pdf','',NULL,'2024-12-04 09:43:28.539910','2024-12-04 09:43:28.539936',0,5,2,40,'application/pdf');
INSERT INTO `filer_file` VALUES (5,'c1/42/c142333d-dffe-4dfd-80ab-b785e701fff1/cohiva-demo_formular_uberprufungbelegungsrichtlinien.odt',46208,'235338eb1c992de1a4e3f5ef15269510c142ce2c',0,'Cohiva-Demo_Formular_ÜberprüfungBelegungsrichtlinien.odt','','','2024-12-04 10:01:04.684580','2024-12-04 10:05:19.888855',0,6,2,40,'application/vnd.oasis.opendocument.text');
/*!40000 ALTER TABLE `filer_file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_folder`
--

DROP TABLE IF EXISTS `filer_folder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_folder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `modified_at` datetime(6) NOT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `filer_folder_parent_id_name_bc773258_uniq` (`parent_id`,`name`),
  KEY `filer_folder_owner_id_be530fb4_fk_auth_user_id` (`owner_id`),
  CONSTRAINT `filer_folder_owner_id_be530fb4_fk_auth_user_id` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `filer_folder_parent_id_308aecda_fk_filer_folder_id` FOREIGN KEY (`parent_id`) REFERENCES `filer_folder` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_folder`
--

LOCK TABLES `filer_folder` WRITE;
/*!40000 ALTER TABLE `filer_folder` DISABLE KEYS */;
INSERT INTO `filer_folder` VALUES (1,'Vorlagen','2024-11-06 16:31:45.780498','2024-11-06 16:31:45.780542','2024-11-06 16:31:45.780574',2,NULL);
INSERT INTO `filer_folder` VALUES (2,'Rechnungen','2024-11-06 16:32:18.412262','2024-11-06 16:32:18.412306','2024-11-06 16:32:18.412337',2,1);
INSERT INTO `filer_folder` VALUES (3,'Mitgliedschaft','2024-12-03 11:15:54.183745','2024-12-03 11:15:54.183784','2024-12-03 11:15:54.183803',2,1);
INSERT INTO `filer_folder` VALUES (4,'Beteiligungen','2024-12-03 14:42:44.124213','2024-12-03 14:42:44.124246','2024-12-03 14:42:44.124261',2,1);
INSERT INTO `filer_folder` VALUES (5,'Beilagen','2024-12-04 09:43:02.494354','2024-12-04 09:43:02.494389','2024-12-04 09:43:02.494405',2,1);
INSERT INTO `filer_folder` VALUES (6,'Vermietung','2024-12-04 10:00:56.707006','2024-12-04 10:00:56.707043','2024-12-04 10:00:56.707056',2,1);
/*!40000 ALTER TABLE `filer_folder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_folderpermission`
--

DROP TABLE IF EXISTS `filer_folderpermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_folderpermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` smallint(6) NOT NULL,
  `everybody` tinyint(1) NOT NULL,
  `can_edit` smallint(6) DEFAULT NULL,
  `can_read` smallint(6) DEFAULT NULL,
  `can_add_children` smallint(6) DEFAULT NULL,
  `folder_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `filer_folderpermission_folder_id_5d02f1da_fk_filer_folder_id` (`folder_id`),
  KEY `filer_folderpermission_group_id_8901bafa_fk_auth_group_id` (`group_id`),
  KEY `filer_folderpermission_user_id_7673d4b6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `filer_folderpermission_folder_id_5d02f1da_fk_filer_folder_id` FOREIGN KEY (`folder_id`) REFERENCES `filer_folder` (`id`),
  CONSTRAINT `filer_folderpermission_group_id_8901bafa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `filer_folderpermission_user_id_7673d4b6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_folderpermission`
--

LOCK TABLES `filer_folderpermission` WRITE;
/*!40000 ALTER TABLE `filer_folderpermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `filer_folderpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_image`
--

DROP TABLE IF EXISTS `filer_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_image` (
  `file_ptr_id` int(11) NOT NULL,
  `_height` double DEFAULT NULL,
  `_width` double DEFAULT NULL,
  `date_taken` datetime(6) DEFAULT NULL,
  `default_alt_text` varchar(255) DEFAULT NULL,
  `default_caption` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `must_always_publish_author_credit` tinyint(1) NOT NULL,
  `must_always_publish_copyright` tinyint(1) NOT NULL,
  `subject_location` varchar(64) NOT NULL,
  `_transparent` tinyint(1) NOT NULL,
  PRIMARY KEY (`file_ptr_id`),
  CONSTRAINT `filer_image_file_ptr_id_3e21d4f0_fk_filer_file_id` FOREIGN KEY (`file_ptr_id`) REFERENCES `filer_file` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_image`
--

LOCK TABLES `filer_image` WRITE;
/*!40000 ALTER TABLE `filer_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `filer_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filer_thumbnailoption`
--

DROP TABLE IF EXISTS `filer_thumbnailoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `filer_thumbnailoption` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `crop` tinyint(1) NOT NULL,
  `upscale` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filer_thumbnailoption`
--

LOCK TABLES `filer_thumbnailoption` WRITE;
/*!40000 ALTER TABLE `filer_thumbnailoption` DISABLE KEYS */;
/*!40000 ALTER TABLE `filer_thumbnailoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_address`
--

DROP TABLE IF EXISTS `geno_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_address` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `title` varchar(20) NOT NULL,
  `telephone` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `date_birth` date DEFAULT NULL,
  `hometown` varchar(50) NOT NULL,
  `occupation` varchar(150) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `formal` varchar(20) NOT NULL,
  `mobile` varchar(30) NOT NULL,
  `bankaccount` varchar(150) NOT NULL,
  `paymentslip` tinyint(1) NOT NULL,
  `organization` varchar(100) NOT NULL,
  `extra` varchar(100) NOT NULL,
  `interest_action` varchar(100) NOT NULL,
  `carddav_etag` varchar(255) NOT NULL,
  `carddav_href` varchar(255) NOT NULL,
  `carddav_syncts` datetime(6) DEFAULT NULL,
  `email2` varchar(254) NOT NULL,
  `gnucash_id` varchar(30) DEFAULT NULL,
  `emonitor_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `random_id` char(32) NOT NULL,
  `ignore_in_lists` tinyint(1) NOT NULL,
  `login_permission` tinyint(1) NOT NULL,
  `city_name` varchar(100) NOT NULL,
  `city_zipcode` varchar(30) NOT NULL,
  `po_box` tinyint(1) NOT NULL,
  `po_box_number` varchar(100) NOT NULL,
  `country` varchar(100) NOT NULL,
  `house_number` varchar(100) NOT NULL,
  `street_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `geno_address_random_id_8f43db71_uniq` (`random_id`),
  UNIQUE KEY `geno_address_organization_name_first_name_email_0b1f596c_uniq` (`organization`,`name`,`first_name`,`email`),
  UNIQUE KEY `gnucash_id` (`gnucash_id`),
  UNIQUE KEY `emonitor_id` (`emonitor_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `geno_address_active_5685d6b6` (`active`),
  CONSTRAINT `geno_address_user_id_20256b4c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_address`
--

LOCK TABLES `geno_address` WRITE;
/*!40000 ALTER TABLE `geno_address` DISABLE KEYS */;
INSERT INTO `geno_address` VALUES (2,'','2024-10-21 11:07:59.031177','2025-08-20 14:55:00.556755','Muster','Hans','Herr','','hans.muster@example.com','1967-08-06','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,3,'ac9a5f3ff5214c049541ff75e0e1a13a',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (3,'','2024-10-21 11:08:23.991398','2025-08-20 14:55:00.556289','Muster','Anna','Frau','','anna.muster@example.com','2003-12-28','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'358671a183bd4800b514505ca4d92582',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (4,'','2024-10-21 14:44:26.076587','2025-08-20 14:55:00.551305','Dupont','Jean','Herr','','jean.dupont@example.com','1950-03-03','','',1,'Sie','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'f8bc96d1bd694b5da589a4e37ced378b',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (5,'','2024-10-21 14:45:05.206735','2025-08-20 14:55:00.551826','Dupont','Marie','Frau','','marie.dupont@example.com','2010-04-18','','',1,'Sie','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'a6dc26f815894914b3bb60b7bb014e82',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (6,'','2024-10-21 14:45:21.591647','2025-08-20 14:55:00.552297','Dupont','Paul','Herr','','','2018-11-18','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'814d180bd4d44deead1d71fa5774d5b1',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (7,'','2024-10-21 14:48:38.945827','2025-08-20 14:55:00.557226','Pérez','Juan','Herr','','juan.perez@example.com','1979-08-31','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'44253db97cd342f09c3c07f8031d4f08',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (8,'','2024-10-21 14:49:51.291010','2025-08-20 14:55:00.554129','Marković','Marko','Herr','','marko.markovic@example.com','1947-10-21','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'50d9ff5d9e704711836e80feaf87ea00',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (9,'','2024-10-21 14:50:48.638289','2025-08-20 14:55:00.562926','Svensson','Kalle','Herr','','kalle.svenson@example.com','1991-11-08','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'34ebcd6d7bb54ec4ad2823d5a7b16100',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (10,'','2024-10-21 14:51:16.489997','2025-08-20 14:55:00.554734','Meier','Sarah','Frau','','sarah.meier@example.com','2001-08-22','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'17869afd321548388c7d3fb8291071cd',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (11,'','2024-10-21 14:53:13.846585','2025-08-20 14:55:00.563454','van der Merwe','Mary','Frau','','mary.van.der.merwe@example.com','1990-08-23','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'702333e2314447efa3b2689ec8bc81fa',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (12,'','2024-10-21 14:54:30.847848','2025-08-20 14:55:00.549637','Borg','Folana','Frau','','folana.borg@example.com','1985-10-20','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'b20465485b564bb886212e5748d9407a',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (13,'','2024-10-21 14:54:53.990203','2025-08-20 14:55:00.555803','Müller','Matthias','Herr','','matthias.mueller@example.com','1966-04-24','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'f0fbf65dd50c4e8eba4302da9200e44d',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (14,'','2024-10-21 14:57:57.088248','2025-08-20 14:55:00.560319','Schmid','Tobi','Herr','','tobi.schmid@example.com','1993-08-27','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'9cb6486f88b44331b29b680d0f9caabe',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (15,'','2024-10-21 14:59:21.868863','2025-08-20 14:55:00.553203','Jensen','Hugo','Herr','','hugo.jensen@example.com','1977-03-24','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'e3bd610536304dad8b78cd54ae8c692c',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (16,'','2024-10-21 14:59:48.902569','2025-08-20 14:55:00.553656','Klein','Anna','Frau','','anna.klein@example.com','1991-08-18','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'1e87580c504446d2a89acdb41a3eee0a',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (17,'','2024-10-21 15:00:31.092092','2025-08-20 14:55:00.563963','','','Org','','brot-gmbh@example.com','1964-08-09','','',1,'Sie','','',0,'Brot GmbH','','','','',NULL,'',NULL,NULL,NULL,'5733fe8465904ace8d8ebac20c01819c',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (18,'','2024-10-21 15:04:33.165575','2025-08-20 14:55:00.565015','','','Org','','kunterbunt@example.com','1979-03-30','','',1,'Du','','',0,'Verein WG Kunterbunt','','','','',NULL,'',NULL,NULL,NULL,'34423b7bb65247d5b229f95207ad389c',0,0,'Bern','3000',0,'','Schweiz','1','Musterweg');
INSERT INTO `geno_address` VALUES (19,'','2024-10-21 15:21:57.733371','2025-08-20 14:55:00.549081','Balmer','Brigitta','Frau','','brigitta.balmer@example.com','1978-06-08','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'a8cebfa455e34c1a92eef351a79f7700',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (20,'','2024-10-21 15:22:53.768666','2025-08-20 14:55:00.552753','Jäger','Marta','Frau','','marta.jaeger@example.com','2004-08-17','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'d7ceadbcee704f909ade70f5769271dd',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (21,'','2024-10-21 15:23:25.308910','2025-08-20 14:55:00.561218','Seel','Katja','Frau','','katja.seel@example.com','1990-12-03','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'fcce669338b241a386c2336cd13f42fb',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (22,'','2024-10-21 15:23:41.187965','2025-08-20 14:55:00.559340','Schalk','Barbara','Frau','','barbara.schalk@example.com','1963-12-24','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'acd185dc596040d8ade2315546a0f9d0',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (23,'','2024-10-21 15:27:48.690199','2025-08-20 14:55:00.550195','Deshar','Fatma','Frau','','fatma.deshar@example.com','1999-10-16','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'51e49e65daf74ae39a0e4df7f650a1c6',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (24,'','2024-10-21 15:28:12.100723','2025-08-20 14:55:00.557706','Rick','René','Herr','','rene.rick@example.com','1977-10-09','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'0771232c9ef9440eb5ee6bc461100d2b',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (25,'','2024-10-21 15:28:31.895552','2025-08-20 14:55:00.555254','Müller','Dieter','Herr','','dieter.mueller@example.com','1999-06-15','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'5b5b579e36744f618399c82fbb88ccfc',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (26,'','2024-10-21 15:28:49.106297','2025-08-20 14:55:00.550771','Dobler','Rudolf','Herr','','rudolf.dobler@example.com','1975-10-19','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'f4404b479c6f4c19bbfc6163593a4cb8',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (27,'','2024-10-21 15:29:23.712318','2025-08-20 14:55:00.547519','Alder','Mario','Herr','','mario.alder@example.com','1996-09-14','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'40b8d269e27b44a2adb269a9ac22bfec',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (28,'','2024-10-21 15:29:40.990205','2025-08-20 14:55:00.548419','Alder','Max','Herr','','','2016-03-02','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'296881e437de4faf8513d140db0ae127',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (29,'','2024-10-21 15:29:45.285359','2025-08-20 14:55:00.546514','Alder','Annika','Herr','','','2014-10-22','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'060014342eb8437ba301ea8237d958ec',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (30,'','2024-10-21 15:30:37.231578','2025-08-20 14:55:00.558717','Rossi','Mario','Herr','','mario.rossi@example.com','1977-02-22','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'2cbdbb4c151a455895c77825cf3584c6',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (31,'','2024-10-21 15:31:38.056846','2025-08-20 14:55:00.558203','Rossi','Bela','Herr','','bela.rossi@example.com','2009-01-09','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'46540bf40f914da5b23d800ee656af45',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (32,'','2024-10-22 14:26:21.694493','2025-08-20 14:55:00.559847','Schalk','Sophie','Frau','','','2019-11-13','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'0b31726cf53248c096f108dea1702cf8',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (33,'','2024-10-22 14:27:52.529667','2025-08-20 14:55:00.560777','Seel','Claire','Frau','','','2010-09-07','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'3b5b4261637b46f88feb060e1c77fbd9',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (34,'','2024-10-22 14:33:41.672473','2025-08-20 14:55:00.561703','Seel','Ronja','Frau','','','2016-02-17','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'5e8b15d4fdb14a7897b65b5cb099fec7',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (35,'','2024-10-22 14:36:35.592626','2025-08-20 14:55:00.562188','Seel','Vincent','Herr','','','2013-09-23','','',1,'Du','','',0,'','','','','',NULL,'',NULL,NULL,NULL,'c67d63547102418c8476e983ea0f1cbd',0,0,'Bern','3000',0,'','Schweiz','2','Musterweg');
INSERT INTO `geno_address` VALUES (36,'','2024-12-03 10:32:30.344165','2024-12-03 10:32:30.344193','','','Org','','',NULL,'','',1,'Sie','','',0,'Meinebank AG','','','','',NULL,'',NULL,NULL,NULL,'ba73f1f0fd4a450c96b80698baa37f38',0,0,'','',0,'','Schweiz','','');
INSERT INTO `geno_address` VALUES (37,'','2024-12-03 10:33:49.387889','2025-08-20 14:55:00.564521','Gönner','Hansruedi','Herr','','',NULL,'','',1,'Sie','','CH9999999999999999999',0,'Stiftung Weitsicht','','Bank','','',NULL,'',NULL,NULL,NULL,'19913e3b19a54a9ba8a952ff58155542',0,0,'Zürich','8001',0,'','Schweiz','1','Bahnhofplatz');
/*!40000 ALTER TABLE `geno_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_building`
--

DROP TABLE IF EXISTS `geno_building`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_building` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(200) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `team` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_building`
--

LOCK TABLES `geno_building` WRITE;
/*!40000 ALTER TABLE `geno_building` DISABLE KEYS */;
INSERT INTO `geno_building` VALUES (1,'','2024-10-16 15:32:11.347279','2024-10-16 15:32:11.347321','Musterweg 1','',1,'Musterweg1');
INSERT INTO `geno_building` VALUES (2,'','2024-10-16 15:32:24.251313','2024-10-16 15:32:24.251356','Musterweg 2','',1,'Musterweg2');
/*!40000 ALTER TABLE `geno_building` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_child`
--

DROP TABLE IF EXISTS `geno_child`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_child` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `presence` decimal(2,1) NOT NULL,
  `parents` varchar(200) NOT NULL,
  `notes` longtext NOT NULL,
  `name_id` int(11) NOT NULL,
  `emonitor_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_id` (`name_id`),
  UNIQUE KEY `emonitor_id` (`emonitor_id`),
  CONSTRAINT `geno_child_name_id_e87cbb26_fk_geno_address_id` FOREIGN KEY (`name_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_child`
--

LOCK TABLES `geno_child` WRITE;
/*!40000 ALTER TABLE `geno_child` DISABLE KEYS */;
INSERT INTO `geno_child` VALUES (1,'','2024-10-21 14:46:07.992236','2024-10-21 14:46:53.730326',7.0,'Jean Dupont, Marie Dupont','',6,NULL);
INSERT INTO `geno_child` VALUES (2,'','2024-10-22 14:19:46.605940','2024-10-22 14:19:46.605984',7.0,'Mario Alder, Brigitta Balmer','',29,NULL);
INSERT INTO `geno_child` VALUES (3,'','2024-10-22 14:19:59.029877','2024-10-22 14:19:59.029920',7.0,'Mario Alder, Brigitta Balmer','',28,NULL);
INSERT INTO `geno_child` VALUES (4,'','2024-10-22 14:26:52.523526','2024-10-22 14:26:52.523569',4.0,'Sophie Schalk, Bernhard Hipp','',32,NULL);
INSERT INTO `geno_child` VALUES (5,'','2024-10-22 14:28:36.565093','2024-10-22 14:35:45.829119',7.0,'Katja Seel, Mary van der Merwe','',33,NULL);
INSERT INTO `geno_child` VALUES (7,'','2024-10-22 14:35:52.991814','2024-10-22 14:36:45.261185',7.0,'Katja Seel, Mary van der Merwe','',34,NULL);
INSERT INTO `geno_child` VALUES (8,'','2024-10-22 14:36:49.501567','2024-10-22 14:36:49.501609',7.0,'Katja Seel, Mary van der Merwe','',35,NULL);
INSERT INTO `geno_child` VALUES (9,'','2024-10-22 14:37:55.268166','2024-10-22 14:37:55.268233',7.0,'Mario Rossi, Katharina Bossi','',31,NULL);
/*!40000 ALTER TABLE `geno_child` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contenttemplate`
--

DROP TABLE IF EXISTS `geno_contenttemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contenttemplate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `template_type` varchar(50) NOT NULL,
  `text` longtext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `file_id` int(11) DEFAULT NULL,
  `manual_creation_allowed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_contenttemplate_active_e48140f3` (`active`),
  KEY `geno_contenttemplate_file_id_3d163c4b` (`file_id`),
  CONSTRAINT `geno_contenttemplate_file_id_3d163c4b_fk_filer_file_id` FOREIGN KEY (`file_id`) REFERENCES `filer_file` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contenttemplate`
--

LOCK TABLES `geno_contenttemplate` WRITE;
/*!40000 ALTER TABLE `geno_contenttemplate` DISABLE KEYS */;
INSERT INTO `geno_contenttemplate` VALUES (1,'','2024-11-06 16:34:05.633764','2024-11-06 16:34:05.633817','Allgemeine QR-Rechnung','OpenDocument','',1,1,1);
INSERT INTO `geno_contenttemplate` VALUES (2,'','2024-12-03 11:16:22.084684','2024-12-03 11:19:30.429576','Brief Bestätigung Mitgliedschaft','OpenDocument','',1,2,1);
INSERT INTO `geno_contenttemplate` VALUES (3,'','2024-12-03 14:44:27.542384','2024-12-03 14:44:27.542420','Kontoauszug/Bestätigung Beteiligungen','OpenDocument','',1,3,1);
INSERT INTO `geno_contenttemplate` VALUES (4,'','2024-12-04 09:31:09.828472','2024-12-04 09:31:09.828507','Bestätigung Reservation Gästezimmer','Email','{{anrede}}\r\n\r\nDies ist eine automatische Bestätigung der folgenden Reservation:\r\n\r\nBezeichnung: {{reservation_object}}\r\nVon: {{reservation_from}}\r\nBis: {{reservation_to}}\r\nReservationsnummer: {{reservation_id}}\r\n\r\nDie wichtigsten Informationen zur Nutzung des Gästezimmers findest Du hier: https://www.musterweg.ch/gaestezimmer/\r\n\r\nIm Kalender der Musterweg-App ist ersichtlich wer vor oder nach dir reserviert hat. Du kannst dich direkt mit ihnen in Verbindung setzen, wenn es um die Rückgabe von Wäsche, Änderungen in letzter Minute, verspätete Abreise oder verfrühte Ankunft, verlorene Gegenstände, usw. geht. Du kannst ihn auch nutzen um Stornierungen zu beobachten und einen Überblick über die Verfügbarkeit zukünftiger Reservierungen zu erhalten.\r\n\r\nBei Fragen zur Reservation kannst du dich an die AG Gästezimmer wenden:\r\n\r\nEmail: gaestezimmer@musterweg.ch\r\n\r\nHerzliche Grüsse\r\nAG Gästezimmer',1,NULL,1);
INSERT INTO `geno_contenttemplate` VALUES (5,'','2024-12-04 09:31:50.979268','2024-12-04 09:31:50.979296','Jährlicher Kontoauszug','Email','{{anrede}}\r\n  \r\nAnbei {{erhältst}} {{du}} die Bestätigung {{deiner}} finanziellen Beteiligung an der Genossenschaft Musterweg per Ende {{year}}.\r\nDas Dokument dient zu {{deiner}} Information und auch als Bescheinigung für die Steuererklärung.\r\n\r\nFalls {{du}} noch Fragen dazu {{hast}}, stehen wir gerne zur Verfügung.\r\n\r\nHerzliche Grüsse\r\nGenossenschaft Musterweg',1,NULL,1);
INSERT INTO `geno_contenttemplate` VALUES (6,'','2024-12-04 09:33:43.864868','2024-12-04 09:33:43.864910','Email Allgemein','Email','{{anrede}}\r\n  \r\nAnbei {{erhältst}} {{du}} die im Betreff erwähnten Unterlagen.\r\n\r\nHerzliche Grüsse\r\nGenossenschaft Musterweg',1,NULL,1);
INSERT INTO `geno_contenttemplate` VALUES (7,'','2024-12-04 09:44:02.235073','2024-12-04 09:44:02.235104','Einladung GV','File','',1,4,1);
INSERT INTO `geno_contenttemplate` VALUES (8,'','2024-12-04 10:02:23.741334','2024-12-04 10:02:23.741368','Formular Überprüfung Belegungsrichtlinien','OpenDocument','',1,5,1);
/*!40000 ALTER TABLE `geno_contenttemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contenttemplate_template_context`
--

DROP TABLE IF EXISTS `geno_contenttemplate_template_context`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contenttemplate_template_context` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contenttemplate_id` int(11) NOT NULL,
  `contenttemplateoption_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `geno_contenttemplate_tem_contenttemplate_id_conte_0087d6e8_uniq` (`contenttemplate_id`,`contenttemplateoption_id`),
  KEY `geno_contenttemplate_contenttemplateoptio_cf92ed8b_fk_geno_cont` (`contenttemplateoption_id`),
  CONSTRAINT `geno_contenttemplate_contenttemplate_id_1ff6bc90_fk_geno_cont` FOREIGN KEY (`contenttemplate_id`) REFERENCES `geno_contenttemplate` (`id`),
  CONSTRAINT `geno_contenttemplate_contenttemplateoptio_cf92ed8b_fk_geno_cont` FOREIGN KEY (`contenttemplateoption_id`) REFERENCES `geno_contenttemplateoption` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contenttemplate_template_context`
--

LOCK TABLES `geno_contenttemplate_template_context` WRITE;
/*!40000 ALTER TABLE `geno_contenttemplate_template_context` DISABLE KEYS */;
INSERT INTO `geno_contenttemplate_template_context` VALUES (1,3,1);
/*!40000 ALTER TABLE `geno_contenttemplate_template_context` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contenttemplateoption`
--

DROP TABLE IF EXISTS `geno_contenttemplateoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contenttemplateoption` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `value` varchar(100) NOT NULL,
  `name_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_contenttemplate_name_id_0e0f18da_fk_geno_cont` (`name_id`),
  CONSTRAINT `geno_contenttemplate_name_id_0e0f18da_fk_geno_cont` FOREIGN KEY (`name_id`) REFERENCES `geno_contenttemplateoptiontype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contenttemplateoption`
--

LOCK TABLES `geno_contenttemplateoption` WRITE;
/*!40000 ALTER TABLE `geno_contenttemplateoption` DISABLE KEYS */;
INSERT INTO `geno_contenttemplateoption` VALUES (1,'','2024-12-03 14:44:22.214328','2025-08-23 09:02:54.872804','',1);
INSERT INTO `geno_contenttemplateoption` VALUES (2,'','2024-12-03 14:46:22.433182','2025-08-23 09:02:54.873744','',2);
INSERT INTO `geno_contenttemplateoption` VALUES (3,'','2024-12-03 16:22:45.212324','2025-08-23 09:02:54.874582','CH7730000001250094239',3);
INSERT INTO `geno_contenttemplateoption` VALUES (4,'','2024-12-03 16:23:15.103224','2025-08-23 09:02:54.875316','11',4);
INSERT INTO `geno_contenttemplateoption` VALUES (5,'','2024-12-03 16:23:41.318138','2025-08-23 09:02:54.876014','Beitrag Solifonds {{jahr}}',5);
INSERT INTO `geno_contenttemplateoption` VALUES (6,'','2024-12-03 16:23:48.285912','2025-08-23 09:02:54.876693','',6);
/*!40000 ALTER TABLE `geno_contenttemplateoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contenttemplateoptiontype`
--

DROP TABLE IF EXISTS `geno_contenttemplateoptiontype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contenttemplateoptiontype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contenttemplateoptiontype`
--

LOCK TABLES `geno_contenttemplateoptiontype` WRITE;
/*!40000 ALTER TABLE `geno_contenttemplateoptiontype` DISABLE KEYS */;
INSERT INTO `geno_contenttemplateoptiontype` VALUES (1,'','2025-08-23 09:02:54.775724','2025-08-23 09:02:54.775763','share_statement_context','Kontoauszug-Felder verwenden');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (2,'','2025-08-23 09:02:54.776591','2025-08-23 09:02:54.776616','billing_context','Rechnungsstellung-Felder verwenden');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (3,'','2025-08-23 09:02:54.776921','2025-08-23 09:02:54.776937','qrbill_account','IBAN für QR-Rechnung');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (4,'','2025-08-23 09:02:54.777178','2025-08-23 09:02:54.777191','qrbill_invoice_type_id','QR-Kategorie-Code für Ref.Nr.');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (5,'','2025-08-23 09:02:54.777407','2025-08-23 09:02:54.777419','qrbill_info','QR-Infotext');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (6,'','2025-08-23 09:02:54.777615','2025-08-23 09:02:54.777625','qrbill_rental_unit_in_extra_info','Mietobj. bei QR-Infotext anfügen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (7,'','2025-08-23 09:02:54.777813','2025-08-23 09:02:54.777823','bill_text_default','Standard-Rechnungstext');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (8,'','2025-08-23 09:02:54.778024','2025-08-23 09:02:54.778035','bill_amount_default','Standard-Rechnungsbetrag');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (9,'','2025-08-23 09:02:54.778230','2025-08-23 09:02:54.778240','bill_text_memberflag_01','Rechnungstext für Wohnen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (10,'','2025-08-23 09:02:54.778441','2025-08-23 09:02:54.778451','bill_amount_memberflag_01','Rechnungsbetrag für Wohnen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (11,'','2025-08-23 09:02:54.778643','2025-08-23 09:02:54.778653','bill_text_memberflag_02','Rechnungstext für Gewerbe/Arbeiten');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (12,'','2025-08-23 09:02:54.778824','2025-08-23 09:02:54.778834','bill_amount_memberflag_02','Rechnungsbetrag für Gewerbe/Arbeiten');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (13,'','2025-08-23 09:02:54.779004','2025-08-23 09:02:54.779014','bill_text_memberflag_03','Rechnungstext für Mitarbeit/Ideen umsetzen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (14,'','2025-08-23 09:02:54.779178','2025-08-23 09:02:54.779188','bill_amount_memberflag_03','Rechnungsbetrag für Mitarbeit/Ideen umsetzen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (15,'','2025-08-23 09:02:54.779356','2025-08-23 09:02:54.779367','bill_text_memberflag_04','Rechnungstext für Projekt unterstützen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (16,'','2025-08-23 09:02:54.779530','2025-08-23 09:02:54.779541','bill_amount_memberflag_04','Rechnungsbetrag für Projekt unterstützen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (17,'','2025-08-23 09:02:54.779703','2025-08-23 09:02:54.779713','bill_text_memberflag_05','Rechnungstext für Dranbleiben');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (18,'','2025-08-23 09:02:54.779876','2025-08-23 09:02:54.779887','bill_amount_memberflag_05','Rechnungsbetrag für Dranbleiben');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (19,'','2025-08-23 09:02:54.780059','2025-08-23 09:02:54.780069','share_count_context_var','Variablenname für Anz. Beteiligungen');
INSERT INTO `geno_contenttemplateoptiontype` VALUES (20,'','2025-08-23 09:02:54.780242','2025-08-23 09:02:54.780252','share_count_sharetype','Beteiligungstyp für Anz. Beteiligungen');
/*!40000 ALTER TABLE `geno_contenttemplateoptiontype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contract`
--

DROP TABLE IF EXISTS `geno_contract`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contract` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `state` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `date_end` date DEFAULT NULL,
  `note` varchar(200) NOT NULL,
  `emonitor_id` int(11) DEFAULT NULL,
  `children_old` varchar(200) NOT NULL,
  `main_contact_id` int(11) DEFAULT NULL,
  `rent_reduction` decimal(10,2) DEFAULT NULL,
  `share_reduction` decimal(10,2) DEFAULT NULL,
  `send_qrbill` varchar(50) NOT NULL,
  `billing_contract_id` int(11) DEFAULT NULL,
  `bankaccount` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `emonitor_id` (`emonitor_id`),
  KEY `geno_contract_main_contact_id_aaafcd4d_fk_geno_address_id` (`main_contact_id`),
  KEY `geno_contract_billing_contract_id_61e51e19_fk_geno_contract_id` (`billing_contract_id`),
  CONSTRAINT `geno_contract_billing_contract_id_61e51e19_fk_geno_contract_id` FOREIGN KEY (`billing_contract_id`) REFERENCES `geno_contract` (`id`),
  CONSTRAINT `geno_contract_main_contact_id_aaafcd4d_fk_geno_address_id` FOREIGN KEY (`main_contact_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contract`
--

LOCK TABLES `geno_contract` WRITE;
/*!40000 ALTER TABLE `geno_contract` DISABLE KEYS */;
INSERT INTO `geno_contract` VALUES (1,'','2024-10-21 11:09:39.971543','2024-11-19 16:09:56.889023','unterzeichnet','2022-06-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (3,'','2024-10-21 15:03:45.660024','2024-11-19 16:10:00.122786','unterzeichnet','2022-06-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (4,'','2024-10-21 15:06:26.433809','2024-11-19 16:10:03.086081','unterzeichnet','2022-06-01',NULL,'',NULL,'',18,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (5,'','2024-10-21 15:08:09.440110','2024-11-19 16:10:05.981983','unterzeichnet','2022-06-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (6,'','2024-10-21 15:08:35.245431','2024-11-19 16:10:08.856505','unterzeichnet','2022-06-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (7,'','2024-10-21 15:08:55.317159','2024-11-19 16:10:11.869275','unterzeichnet','2022-06-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (8,'','2024-10-22 14:19:02.723195','2024-11-19 16:34:45.244934','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (9,'','2024-10-22 14:43:36.473126','2024-11-19 16:34:48.378893','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (10,'','2024-10-22 14:45:06.885280','2024-11-19 16:34:51.724810','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (11,'','2024-10-22 14:45:48.612679','2024-11-19 16:34:54.870378','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (12,'','2024-10-22 14:46:35.257848','2024-11-19 16:34:57.882715','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (13,'','2024-10-22 14:46:42.219712','2024-11-19 16:35:01.283308','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (14,'','2024-10-22 14:54:01.313364','2024-11-19 16:35:04.229779','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
INSERT INTO `geno_contract` VALUES (15,'','2024-10-22 14:54:53.539376','2024-11-19 16:35:07.441472','unterzeichnet','2024-08-01',NULL,'',NULL,'',NULL,NULL,NULL,'none',NULL,'');
/*!40000 ALTER TABLE `geno_contract` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contract_children`
--

DROP TABLE IF EXISTS `geno_contract_children`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contract_children` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contract_id` int(11) NOT NULL,
  `child_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `geno_contract_children_contract_id_child_id_4acfa69d_uniq` (`contract_id`,`child_id`),
  KEY `geno_contract_children_child_id_d94c82b3_fk_geno_child_id` (`child_id`),
  CONSTRAINT `geno_contract_children_child_id_d94c82b3_fk_geno_child_id` FOREIGN KEY (`child_id`) REFERENCES `geno_child` (`id`),
  CONSTRAINT `geno_contract_children_contract_id_9e7ecea7_fk_geno_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `geno_contract` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contract_children`
--

LOCK TABLES `geno_contract_children` WRITE;
/*!40000 ALTER TABLE `geno_contract_children` DISABLE KEYS */;
INSERT INTO `geno_contract_children` VALUES (1,1,1);
INSERT INTO `geno_contract_children` VALUES (2,8,2);
INSERT INTO `geno_contract_children` VALUES (3,8,3);
INSERT INTO `geno_contract_children` VALUES (5,9,4);
INSERT INTO `geno_contract_children` VALUES (6,9,5);
INSERT INTO `geno_contract_children` VALUES (7,9,7);
INSERT INTO `geno_contract_children` VALUES (4,9,8);
INSERT INTO `geno_contract_children` VALUES (8,11,9);
INSERT INTO `geno_contract_children` VALUES (9,12,9);
/*!40000 ALTER TABLE `geno_contract_children` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contract_contractors`
--

DROP TABLE IF EXISTS `geno_contract_contractors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contract_contractors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contract_id` int(11) NOT NULL,
  `address_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `geno_contract_contractors_contract_id_address_id_bb75f41b_uniq` (`contract_id`,`address_id`),
  KEY `geno_contract_contractors_address_id_892f1d41_fk_geno_address_id` (`address_id`),
  CONSTRAINT `geno_contract_contra_contract_id_3786f391_fk_geno_cont` FOREIGN KEY (`contract_id`) REFERENCES `geno_contract` (`id`),
  CONSTRAINT `geno_contract_contractors_address_id_892f1d41_fk_geno_address_id` FOREIGN KEY (`address_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contract_contractors`
--

LOCK TABLES `geno_contract_contractors` WRITE;
/*!40000 ALTER TABLE `geno_contract_contractors` DISABLE KEYS */;
INSERT INTO `geno_contract_contractors` VALUES (5,1,4);
INSERT INTO `geno_contract_contractors` VALUES (6,1,5);
INSERT INTO `geno_contract_contractors` VALUES (7,3,2);
INSERT INTO `geno_contract_contractors` VALUES (8,3,3);
INSERT INTO `geno_contract_contractors` VALUES (9,4,7);
INSERT INTO `geno_contract_contractors` VALUES (10,4,8);
INSERT INTO `geno_contract_contractors` VALUES (11,4,9);
INSERT INTO `geno_contract_contractors` VALUES (12,4,10);
INSERT INTO `geno_contract_contractors` VALUES (13,4,11);
INSERT INTO `geno_contract_contractors` VALUES (14,4,12);
INSERT INTO `geno_contract_contractors` VALUES (15,4,13);
INSERT INTO `geno_contract_contractors` VALUES (16,4,14);
INSERT INTO `geno_contract_contractors` VALUES (17,4,18);
INSERT INTO `geno_contract_contractors` VALUES (18,5,16);
INSERT INTO `geno_contract_contractors` VALUES (19,6,15);
INSERT INTO `geno_contract_contractors` VALUES (20,7,17);
INSERT INTO `geno_contract_contractors` VALUES (21,8,19);
INSERT INTO `geno_contract_contractors` VALUES (22,8,27);
INSERT INTO `geno_contract_contractors` VALUES (23,9,11);
INSERT INTO `geno_contract_contractors` VALUES (24,9,21);
INSERT INTO `geno_contract_contractors` VALUES (25,9,22);
INSERT INTO `geno_contract_contractors` VALUES (31,9,26);
INSERT INTO `geno_contract_contractors` VALUES (32,10,23);
INSERT INTO `geno_contract_contractors` VALUES (28,11,30);
INSERT INTO `geno_contract_contractors` VALUES (29,12,30);
INSERT INTO `geno_contract_contractors` VALUES (34,13,20);
INSERT INTO `geno_contract_contractors` VALUES (33,13,24);
INSERT INTO `geno_contract_contractors` VALUES (35,14,17);
INSERT INTO `geno_contract_contractors` VALUES (37,15,20);
INSERT INTO `geno_contract_contractors` VALUES (36,15,24);
/*!40000 ALTER TABLE `geno_contract_contractors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_contract_rental_units`
--

DROP TABLE IF EXISTS `geno_contract_rental_units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_contract_rental_units` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contract_id` int(11) NOT NULL,
  `rentalunit_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `geno_contract_rental_uni_contract_id_rentalunit_i_0efcd93d_uniq` (`contract_id`,`rentalunit_id`),
  KEY `geno_contract_rental_rentalunit_id_28a16bb3_fk_geno_rent` (`rentalunit_id`),
  CONSTRAINT `geno_contract_rental_contract_id_f5736700_fk_geno_cont` FOREIGN KEY (`contract_id`) REFERENCES `geno_contract` (`id`),
  CONSTRAINT `geno_contract_rental_rentalunit_id_28a16bb3_fk_geno_rent` FOREIGN KEY (`rentalunit_id`) REFERENCES `geno_rentalunit` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_contract_rental_units`
--

LOCK TABLES `geno_contract_rental_units` WRITE;
/*!40000 ALTER TABLE `geno_contract_rental_units` DISABLE KEYS */;
INSERT INTO `geno_contract_rental_units` VALUES (5,1,8);
INSERT INTO `geno_contract_rental_units` VALUES (6,1,26);
INSERT INTO `geno_contract_rental_units` VALUES (8,3,7);
INSERT INTO `geno_contract_rental_units` VALUES (7,3,13);
INSERT INTO `geno_contract_rental_units` VALUES (33,3,24);
INSERT INTO `geno_contract_rental_units` VALUES (10,4,9);
INSERT INTO `geno_contract_rental_units` VALUES (9,4,14);
INSERT INTO `geno_contract_rental_units` VALUES (11,5,10);
INSERT INTO `geno_contract_rental_units` VALUES (12,5,15);
INSERT INTO `geno_contract_rental_units` VALUES (13,6,16);
INSERT INTO `geno_contract_rental_units` VALUES (14,7,2);
INSERT INTO `geno_contract_rental_units` VALUES (15,7,12);
INSERT INTO `geno_contract_rental_units` VALUES (16,8,20);
INSERT INTO `geno_contract_rental_units` VALUES (17,8,27);
INSERT INTO `geno_contract_rental_units` VALUES (26,9,3);
INSERT INTO `geno_contract_rental_units` VALUES (27,9,21);
INSERT INTO `geno_contract_rental_units` VALUES (20,10,4);
INSERT INTO `geno_contract_rental_units` VALUES (21,10,22);
INSERT INTO `geno_contract_rental_units` VALUES (22,11,5);
INSERT INTO `geno_contract_rental_units` VALUES (23,11,23);
INSERT INTO `geno_contract_rental_units` VALUES (24,12,17);
INSERT INTO `geno_contract_rental_units` VALUES (28,13,1);
INSERT INTO `geno_contract_rental_units` VALUES (29,13,19);
INSERT INTO `geno_contract_rental_units` VALUES (30,14,25);
INSERT INTO `geno_contract_rental_units` VALUES (31,15,25);
/*!40000 ALTER TABLE `geno_contract_rental_units` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_document`
--

DROP TABLE IF EXISTS `geno_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(250) NOT NULL,
  `data` longtext NOT NULL,
  `object_id` int(10) unsigned NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `doctype_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_document_content_type_id_85d9388c_fk_django_content_type_id` (`content_type_id`),
  KEY `geno_document_doctype_id_06bca4f4_fk_geno_documenttype_id` (`doctype_id`),
  CONSTRAINT `geno_document_content_type_id_85d9388c_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `geno_document_doctype_id_06bca4f4_fk_geno_documenttype_id` FOREIGN KEY (`doctype_id`) REFERENCES `geno_documenttype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_document`
--

LOCK TABLES `geno_document` WRITE;
/*!40000 ALTER TABLE `geno_document` DISABLE KEYS */;
INSERT INTO `geno_document` VALUES (83,'','2024-12-04 10:03:05.996624','2024-12-04 10:03:05.996661','Formular_Überprüfung_Belegung_Fahrzeuge_Alder_Mario.odt','{\"mietobjekt\": \"002 Wohnung (Musterweg 2), 9902 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"3\", \"bewohnende\": [{\"name\": \"Alder\", \"vorname\": \"Mario\"}, {\"name\": \"Balmer\", \"vorname\": \"Brigitta\"}, {\"name\": \"Alder\", \"vorname\": \"Annika\"}, {\"name\": \"Alder\", \"vorname\": \"Max\"}], \"organisation\": \"\", \"vorname\": \"Mario\", \"name\": \"Alder\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"mario.alder@example.com\", \"geburtsdatum\": \"14.09.1996\", \"uuid\": \"40b8d269-e27b-44a2-adb2-69a9ac22bfec\", \"anrede\": \"Lieber Mario\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',8,17,4);
INSERT INTO `geno_document` VALUES (84,'','2024-12-04 10:03:06.055650','2024-12-04 10:03:06.055757','Formular_Überprüfung_Belegung_Fahrzeuge_Dobler_Rudolf.odt','{\"mietobjekt\": \"101 Grosswohnung (Musterweg 2), 9903 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"8\", \"bewohnende\": [{\"name\": \"Dobler\", \"vorname\": \"Rudolf\"}, {\"name\": \"Schalk\", \"vorname\": \"Barbara\"}, {\"name\": \"Seel\", \"vorname\": \"Katja\"}, {\"name\": \"van der Merwe\", \"vorname\": \"Mary\"}, {\"name\": \"Schalk\", \"vorname\": \"Sophie\"}, {\"name\": \"Seel\", \"vorname\": \"Claire\"}, {\"name\": \"Seel\", \"vorname\": \"Ronja\"}, {\"name\": \"Seel\", \"vorname\": \"Vincent\"}], \"organisation\": \"\", \"vorname\": \"Rudolf\", \"name\": \"Dobler\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"rudolf.dobler@example.com\", \"geburtsdatum\": \"19.10.1975\", \"uuid\": \"f4404b47-9c6f-4c19-bbfc-6163593a4cb8\", \"anrede\": \"Lieber Rudolf\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',9,17,4);
INSERT INTO `geno_document` VALUES (85,'','2024-12-04 10:03:06.108299','2024-12-04 10:03:06.108332','Formular_Überprüfung_Belegung_Fahrzeuge_Deshar_Fatma.odt','{\"mietobjekt\": \"201 Wohnung (Musterweg 2), 9904 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Deshar\", \"vorname\": \"Fatma\"}], \"organisation\": \"\", \"vorname\": \"Fatma\", \"name\": \"Deshar\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"fatma.deshar@example.com\", \"geburtsdatum\": \"16.10.1999\", \"uuid\": \"51e49e65-daf7-4ae3-9a0e-4df7f650a1c6\", \"anrede\": \"Liebe Fatma\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',10,17,4);
INSERT INTO `geno_document` VALUES (86,'','2024-12-04 10:03:06.159859','2024-12-04 10:03:06.159892','Formular_Überprüfung_Belegung_Fahrzeuge_Rossi_Mario.odt','{\"mietobjekt\": \"202 Wohnung (Musterweg 2), 9905 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Rossi\", \"vorname\": \"Mario\"}, {\"name\": \"Rossi\", \"vorname\": \"Bela\"}], \"organisation\": \"\", \"vorname\": \"Mario\", \"name\": \"Rossi\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"mario.rossi@example.com\", \"geburtsdatum\": \"22.02.1977\", \"uuid\": \"2cbdbb4c-151a-4558-95c7-7825cf3584c6\", \"anrede\": \"Lieber Mario\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',11,17,4);
INSERT INTO `geno_document` VALUES (87,'','2024-12-04 10:03:06.208782','2024-12-04 10:03:06.208816','Formular_Überprüfung_Belegung_Fahrzeuge_Rossi_Mario_2.odt','{\"mietobjekt\": \"203 Jokerzimmer (Musterweg 2)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Rossi\", \"vorname\": \"Mario\"}, {\"name\": \"Rossi\", \"vorname\": \"Bela\"}], \"organisation\": \"\", \"vorname\": \"Mario\", \"name\": \"Rossi\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"mario.rossi@example.com\", \"geburtsdatum\": \"22.02.1977\", \"uuid\": \"2cbdbb4c-151a-4558-95c7-7825cf3584c6\", \"anrede\": \"Lieber Mario\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',12,17,4);
INSERT INTO `geno_document` VALUES (88,'','2024-12-04 10:03:06.257744','2024-12-04 10:03:06.257784','Formular_Überprüfung_Belegung_Fahrzeuge_Jäger_Marta.odt','{\"mietobjekt\": \"001 Wohnung (Musterweg 2), 9901 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"2\", \"bewohnende\": [{\"name\": \"J\\u00e4ger\", \"vorname\": \"Marta\"}, {\"name\": \"Rick\", \"vorname\": \"Ren\\u00e9\"}], \"organisation\": \"\", \"vorname\": \"Marta\", \"name\": \"J\\u00e4ger\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"marta.jaeger@example.com\", \"geburtsdatum\": \"17.08.2004\", \"uuid\": \"d7ceadbc-ee70-4f90-9ade-70f5769271dd\", \"anrede\": \"Liebe Marta\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',13,17,4);
INSERT INTO `geno_document` VALUES (89,'','2024-12-04 10:03:06.309708','2024-12-04 10:03:06.309749','Formular_Überprüfung_Belegung_Fahrzeuge_Dupont_Jean.odt','{\"mietobjekt\": \"002 Wohnung (Musterweg 1), 9902 Kellerabteil (Musterweg 1)\", \"mindestbelegung\": \"3\", \"bewohnende\": [{\"name\": \"Dupont\", \"vorname\": \"Jean\"}, {\"name\": \"Dupont\", \"vorname\": \"Marie\"}, {\"name\": \"Dupont\", \"vorname\": \"Paul\"}], \"organisation\": \"\", \"vorname\": \"Jean\", \"name\": \"Dupont\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"jean.dupont@example.com\", \"geburtsdatum\": \"03.03.1950\", \"uuid\": \"f8bc96d1-bd69-4b5d-a589-a4e37ced378b\", \"anrede\": \"Lieber Herr Dupont\", \"dir\": \"Ihnen\", \"dein\": \"Ihr\", \"Dein\": \"Ihr\", \"deine\": \"Ihre\", \"Deine\": \"Ihre\", \"deiner\": \"Ihrer\", \"deinen\": \"Ihren\", \"deinem\": \"Ihrem\", \"Deinem\": \"Ihrem\", \"deines\": \"Ihres\", \"dich\": \"Sie\", \"du\": \"Sie\", \"Du\": \"Sie\", \"eurem\": \"Ihrem\", \"euch\": \"Sie\", \"hast\": \"haben\", \"kannst\": \"k\\u00f6nnen\", \"leistest\": \"leisten\", \"w\\u00fcnschst\": \"w\\u00fcnschen\", \"findest\": \"finden\", \"erh\\u00e4ltst\": \"erhalten\", \"sende\": \"senden Sie\", \"verwende\": \"verwenden Sie\", \"beachte\": \"beachten Sie\", \"gew\\u00e4hrst\": \"gew\\u00e4hren\", \"planst\": \"planen\", \"wirst\": \"werden\", \"m\\u00f6chtest\": \"m\\u00f6chten\", \"f\\u00fclle\": \"f\\u00fcllen Sie\", \"bekommst\": \"bekommen\", \"wurdest\": \"wurden\", \"richte\": \"richten Sie\", \"richtet\": \"richten Sie\", \"Kontaktiere\": \"Kontaktieren Sie\", \"kontaktiere\": \"kontaktieren Sie\", \"Retourniere\": \"Retournieren Sie\", \"retourniere\": \"retournieren Sie\", \"brauchst\": \"brauchen\", \"bist\": \"sind\", \"leite\": \"leiten Sie\", \"weisst\": \"wissen\", \"einbezahlst\": \"einbezahlen\", \"einzahlst\": \"einzahlen\", \"zahle\": \"zahlen Sie\", \"Zahle\": \"Zahlen Sie\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',1,17,4);
INSERT INTO `geno_document` VALUES (90,'','2024-12-04 10:03:06.367046','2024-12-04 10:03:06.367088','Formular_Überprüfung_Belegung_Fahrzeuge_Muster_Anna.odt','{\"mietobjekt\": \"001 Wohnung (Musterweg 1), 9901 Kellerabteil (Musterweg 1), 9906 Hobby (Musterweg 2)\", \"mindestbelegung\": \"2\", \"bewohnende\": [{\"name\": \"Muster\", \"vorname\": \"Anna\"}, {\"name\": \"Muster\", \"vorname\": \"Hans\"}], \"organisation\": \"\", \"vorname\": \"Anna\", \"name\": \"Muster\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"anna.muster@example.com\", \"geburtsdatum\": \"28.12.2003\", \"uuid\": \"358671a1-83bd-4800-b514-505ca4d92582\", \"anrede\": \"Liebe Anna\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',3,17,4);
INSERT INTO `geno_document` VALUES (91,'','2024-12-04 10:03:06.419651','2024-12-04 10:03:06.419716','Formular_Überprüfung_Belegung_Fahrzeuge_VereinWGKunterbunt_.odt','{\"mietobjekt\": \"101 Grosswohnung (Musterweg 1), 9903 Kellerabteil (Musterweg 1)\", \"mindestbelegung\": \"8\", \"bewohnende\": [{\"name\": \"Borg\", \"vorname\": \"Folana\"}, {\"name\": \"Markovi\\u0107\", \"vorname\": \"Marko\"}, {\"name\": \"Meier\", \"vorname\": \"Sarah\"}, {\"name\": \"M\\u00fcller\", \"vorname\": \"Matthias\"}, {\"name\": \"P\\u00e9rez\", \"vorname\": \"Juan\"}, {\"name\": \"Schmid\", \"vorname\": \"Tobi\"}, {\"name\": \"Svensson\", \"vorname\": \"Kalle\"}, {\"name\": \"van der Merwe\", \"vorname\": \"Mary\"}, {\"name\": \"\", \"vorname\": \"\"}], \"organisation\": \"Verein WG Kunterbunt\", \"vorname\": \"\", \"name\": \"\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"kunterbunt@example.com\", \"geburtsdatum\": \"30.03.1979\", \"uuid\": \"34423b7b-b652-47d5-b229-f95207ad389c\", \"anrede\": \"Lieber Verein WG Kunterbunt\", \"dir\": \"euch\", \"dein\": \"euer\", \"Dein\": \"Euer\", \"deine\": \"eure\", \"Deine\": \"Eure\", \"deiner\": \"eurer\", \"deinen\": \"euren\", \"deinem\": \"eurem\", \"Deinem\": \"Eurem\", \"deines\": \"eures\", \"dich\": \"euch\", \"du\": \"ihr\", \"Du\": \"Ihr\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"habt\", \"kannst\": \"k\\u00f6nnt\", \"leistest\": \"leistet\", \"w\\u00fcnschst\": \"w\\u00fcnscht\", \"findest\": \"findet\", \"erh\\u00e4ltst\": \"erh\\u00e4lt\", \"sende\": \"sendet\", \"verwende\": \"verwendet\", \"beachte\": \"beachtet\", \"gew\\u00e4hrst\": \"gew\\u00e4hrt\", \"planst\": \"plant\", \"wirst\": \"werdet\", \"m\\u00f6chtest\": \"m\\u00f6chtet\", \"f\\u00fclle\": \"f\\u00fcllt\", \"bekommst\": \"bekommt\", \"wurdest\": \"wurdet\", \"richte\": \"richtet\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiert\", \"kontaktiere\": \"kontaktiert\", \"Retourniere\": \"Retourniert\", \"retourniere\": \"retourniert\", \"brauchst\": \"braucht\", \"bist\": \"seid\", \"leite\": \"leitet\", \"weisst\": \"wisst\", \"einbezahlst\": \"einbezahlt\", \"einzahlst\": \"einzahlt\", \"zahle\": \"zahlt\", \"Zahle\": \"Zahlt\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',4,17,4);
INSERT INTO `geno_document` VALUES (92,'','2024-12-04 10:03:06.467718','2024-12-04 10:03:06.467749','Formular_Überprüfung_Belegung_Fahrzeuge_Klein_Anna.odt','{\"mietobjekt\": \"201 Wohnung (Musterweg 1), 9904 Kellerabteil (Musterweg 1)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Klein\", \"vorname\": \"Anna\"}], \"organisation\": \"\", \"vorname\": \"Anna\", \"name\": \"Klein\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"anna.klein@example.com\", \"geburtsdatum\": \"18.08.1991\", \"uuid\": \"1e87580c-5044-46d2-a89a-cdb41a3eee0a\", \"anrede\": \"Liebe Anna\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',5,17,4);
INSERT INTO `geno_document` VALUES (93,'','2024-12-04 10:03:06.517146','2024-12-04 10:03:06.517178','Formular_Überprüfung_Belegung_Fahrzeuge_Jensen_Hugo.odt','{\"mietobjekt\": \"202 Wohnung (Musterweg 1)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Jensen\", \"vorname\": \"Hugo\"}], \"organisation\": \"\", \"vorname\": \"Hugo\", \"name\": \"Jensen\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"hugo.jensen@example.com\", \"geburtsdatum\": \"24.03.1977\", \"uuid\": \"e3bd6105-3630-4dad-8b78-cd54ae8c692c\", \"anrede\": \"Lieber Hugo\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',6,17,4);
INSERT INTO `geno_document` VALUES (94,'','2024-12-04 10:05:59.056509','2024-12-04 10:05:59.056546','Formular_Überprüfung_Belegung_Fahrzeuge_Alder_Mario.odt','{\"mietobjekt\": \"002 Wohnung (Musterweg 2), 9902 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"3\", \"bewohnende\": [{\"name\": \"Alder\", \"vorname\": \"Mario\"}, {\"name\": \"Balmer\", \"vorname\": \"Brigitta\"}, {\"name\": \"Alder\", \"vorname\": \"Annika\"}, {\"name\": \"Alder\", \"vorname\": \"Max\"}], \"organisation\": \"\", \"vorname\": \"Mario\", \"name\": \"Alder\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"mario.alder@example.com\", \"geburtsdatum\": \"14.09.1996\", \"uuid\": \"40b8d269-e27b-44a2-adb2-69a9ac22bfec\", \"anrede\": \"Lieber Mario\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',8,17,4);
INSERT INTO `geno_document` VALUES (95,'','2024-12-04 10:05:59.112084','2024-12-04 10:05:59.112118','Formular_Überprüfung_Belegung_Fahrzeuge_Dobler_Rudolf.odt','{\"mietobjekt\": \"101 Grosswohnung (Musterweg 2), 9903 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"8\", \"bewohnende\": [{\"name\": \"Dobler\", \"vorname\": \"Rudolf\"}, {\"name\": \"Schalk\", \"vorname\": \"Barbara\"}, {\"name\": \"Seel\", \"vorname\": \"Katja\"}, {\"name\": \"van der Merwe\", \"vorname\": \"Mary\"}, {\"name\": \"Schalk\", \"vorname\": \"Sophie\"}, {\"name\": \"Seel\", \"vorname\": \"Claire\"}, {\"name\": \"Seel\", \"vorname\": \"Ronja\"}, {\"name\": \"Seel\", \"vorname\": \"Vincent\"}], \"organisation\": \"\", \"vorname\": \"Rudolf\", \"name\": \"Dobler\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"rudolf.dobler@example.com\", \"geburtsdatum\": \"19.10.1975\", \"uuid\": \"f4404b47-9c6f-4c19-bbfc-6163593a4cb8\", \"anrede\": \"Lieber Rudolf\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',9,17,4);
INSERT INTO `geno_document` VALUES (96,'','2024-12-04 10:05:59.181888','2024-12-04 10:05:59.181936','Formular_Überprüfung_Belegung_Fahrzeuge_Deshar_Fatma.odt','{\"mietobjekt\": \"201 Wohnung (Musterweg 2), 9904 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Deshar\", \"vorname\": \"Fatma\"}], \"organisation\": \"\", \"vorname\": \"Fatma\", \"name\": \"Deshar\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"fatma.deshar@example.com\", \"geburtsdatum\": \"16.10.1999\", \"uuid\": \"51e49e65-daf7-4ae3-9a0e-4df7f650a1c6\", \"anrede\": \"Liebe Fatma\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',10,17,4);
INSERT INTO `geno_document` VALUES (97,'','2024-12-04 10:05:59.255992','2024-12-04 10:05:59.256032','Formular_Überprüfung_Belegung_Fahrzeuge_Rossi_Mario.odt','{\"mietobjekt\": \"202 Wohnung (Musterweg 2), 9905 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Rossi\", \"vorname\": \"Mario\"}, {\"name\": \"Rossi\", \"vorname\": \"Bela\"}], \"organisation\": \"\", \"vorname\": \"Mario\", \"name\": \"Rossi\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"mario.rossi@example.com\", \"geburtsdatum\": \"22.02.1977\", \"uuid\": \"2cbdbb4c-151a-4558-95c7-7825cf3584c6\", \"anrede\": \"Lieber Mario\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',11,17,4);
INSERT INTO `geno_document` VALUES (98,'','2024-12-04 10:05:59.315310','2024-12-04 10:05:59.315341','Formular_Überprüfung_Belegung_Fahrzeuge_Rossi_Mario_2.odt','{\"mietobjekt\": \"203 Jokerzimmer (Musterweg 2)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Rossi\", \"vorname\": \"Mario\"}, {\"name\": \"Rossi\", \"vorname\": \"Bela\"}], \"organisation\": \"\", \"vorname\": \"Mario\", \"name\": \"Rossi\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"mario.rossi@example.com\", \"geburtsdatum\": \"22.02.1977\", \"uuid\": \"2cbdbb4c-151a-4558-95c7-7825cf3584c6\", \"anrede\": \"Lieber Mario\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',12,17,4);
INSERT INTO `geno_document` VALUES (99,'','2024-12-04 10:05:59.376516','2024-12-04 10:05:59.376545','Formular_Überprüfung_Belegung_Fahrzeuge_Jäger_Marta.odt','{\"mietobjekt\": \"001 Wohnung (Musterweg 2), 9901 Kellerabteil (Musterweg 2)\", \"mindestbelegung\": \"2\", \"bewohnende\": [{\"name\": \"J\\u00e4ger\", \"vorname\": \"Marta\"}, {\"name\": \"Rick\", \"vorname\": \"Ren\\u00e9\"}], \"organisation\": \"\", \"vorname\": \"Marta\", \"name\": \"J\\u00e4ger\", \"strasse\": \"Musterweg 2\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"marta.jaeger@example.com\", \"geburtsdatum\": \"17.08.2004\", \"uuid\": \"d7ceadbc-ee70-4f90-9ade-70f5769271dd\", \"anrede\": \"Liebe Marta\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',13,17,4);
INSERT INTO `geno_document` VALUES (100,'','2024-12-04 10:05:59.446805','2024-12-04 10:05:59.446833','Formular_Überprüfung_Belegung_Fahrzeuge_Dupont_Jean.odt','{\"mietobjekt\": \"002 Wohnung (Musterweg 1), 9902 Kellerabteil (Musterweg 1)\", \"mindestbelegung\": \"3\", \"bewohnende\": [{\"name\": \"Dupont\", \"vorname\": \"Jean\"}, {\"name\": \"Dupont\", \"vorname\": \"Marie\"}, {\"name\": \"Dupont\", \"vorname\": \"Paul\"}], \"organisation\": \"\", \"vorname\": \"Jean\", \"name\": \"Dupont\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"jean.dupont@example.com\", \"geburtsdatum\": \"03.03.1950\", \"uuid\": \"f8bc96d1-bd69-4b5d-a589-a4e37ced378b\", \"anrede\": \"Lieber Herr Dupont\", \"dir\": \"Ihnen\", \"dein\": \"Ihr\", \"Dein\": \"Ihr\", \"deine\": \"Ihre\", \"Deine\": \"Ihre\", \"deiner\": \"Ihrer\", \"deinen\": \"Ihren\", \"deinem\": \"Ihrem\", \"Deinem\": \"Ihrem\", \"deines\": \"Ihres\", \"dich\": \"Sie\", \"du\": \"Sie\", \"Du\": \"Sie\", \"eurem\": \"Ihrem\", \"euch\": \"Sie\", \"hast\": \"haben\", \"kannst\": \"k\\u00f6nnen\", \"leistest\": \"leisten\", \"w\\u00fcnschst\": \"w\\u00fcnschen\", \"findest\": \"finden\", \"erh\\u00e4ltst\": \"erhalten\", \"sende\": \"senden Sie\", \"verwende\": \"verwenden Sie\", \"beachte\": \"beachten Sie\", \"gew\\u00e4hrst\": \"gew\\u00e4hren\", \"planst\": \"planen\", \"wirst\": \"werden\", \"m\\u00f6chtest\": \"m\\u00f6chten\", \"f\\u00fclle\": \"f\\u00fcllen Sie\", \"bekommst\": \"bekommen\", \"wurdest\": \"wurden\", \"richte\": \"richten Sie\", \"richtet\": \"richten Sie\", \"Kontaktiere\": \"Kontaktieren Sie\", \"kontaktiere\": \"kontaktieren Sie\", \"Retourniere\": \"Retournieren Sie\", \"retourniere\": \"retournieren Sie\", \"brauchst\": \"brauchen\", \"bist\": \"sind\", \"leite\": \"leiten Sie\", \"weisst\": \"wissen\", \"einbezahlst\": \"einbezahlen\", \"einzahlst\": \"einzahlen\", \"zahle\": \"zahlen Sie\", \"Zahle\": \"Zahlen Sie\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',1,17,4);
INSERT INTO `geno_document` VALUES (101,'','2024-12-04 10:05:59.514381','2024-12-04 10:05:59.514415','Formular_Überprüfung_Belegung_Fahrzeuge_Muster_Anna.odt','{\"mietobjekt\": \"001 Wohnung (Musterweg 1), 9901 Kellerabteil (Musterweg 1), 9906 Hobby (Musterweg 2)\", \"mindestbelegung\": \"2\", \"bewohnende\": [{\"name\": \"Muster\", \"vorname\": \"Anna\"}, {\"name\": \"Muster\", \"vorname\": \"Hans\"}], \"organisation\": \"\", \"vorname\": \"Anna\", \"name\": \"Muster\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"anna.muster@example.com\", \"geburtsdatum\": \"28.12.2003\", \"uuid\": \"358671a1-83bd-4800-b514-505ca4d92582\", \"anrede\": \"Liebe Anna\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',3,17,4);
INSERT INTO `geno_document` VALUES (102,'','2024-12-04 10:05:59.573282','2024-12-04 10:05:59.573317','Formular_Überprüfung_Belegung_Fahrzeuge_VereinWGKunterbunt_.odt','{\"mietobjekt\": \"101 Grosswohnung (Musterweg 1), 9903 Kellerabteil (Musterweg 1)\", \"mindestbelegung\": \"8\", \"bewohnende\": [{\"name\": \"Borg\", \"vorname\": \"Folana\"}, {\"name\": \"Markovi\\u0107\", \"vorname\": \"Marko\"}, {\"name\": \"Meier\", \"vorname\": \"Sarah\"}, {\"name\": \"M\\u00fcller\", \"vorname\": \"Matthias\"}, {\"name\": \"P\\u00e9rez\", \"vorname\": \"Juan\"}, {\"name\": \"Schmid\", \"vorname\": \"Tobi\"}, {\"name\": \"Svensson\", \"vorname\": \"Kalle\"}, {\"name\": \"van der Merwe\", \"vorname\": \"Mary\"}, {\"name\": \"\", \"vorname\": \"\"}], \"organisation\": \"Verein WG Kunterbunt\", \"vorname\": \"\", \"name\": \"\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"kunterbunt@example.com\", \"geburtsdatum\": \"30.03.1979\", \"uuid\": \"34423b7b-b652-47d5-b229-f95207ad389c\", \"anrede\": \"Lieber Verein WG Kunterbunt\", \"dir\": \"euch\", \"dein\": \"euer\", \"Dein\": \"Euer\", \"deine\": \"eure\", \"Deine\": \"Eure\", \"deiner\": \"eurer\", \"deinen\": \"euren\", \"deinem\": \"eurem\", \"Deinem\": \"Eurem\", \"deines\": \"eures\", \"dich\": \"euch\", \"du\": \"ihr\", \"Du\": \"Ihr\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"habt\", \"kannst\": \"k\\u00f6nnt\", \"leistest\": \"leistet\", \"w\\u00fcnschst\": \"w\\u00fcnscht\", \"findest\": \"findet\", \"erh\\u00e4ltst\": \"erh\\u00e4lt\", \"sende\": \"sendet\", \"verwende\": \"verwendet\", \"beachte\": \"beachtet\", \"gew\\u00e4hrst\": \"gew\\u00e4hrt\", \"planst\": \"plant\", \"wirst\": \"werdet\", \"m\\u00f6chtest\": \"m\\u00f6chtet\", \"f\\u00fclle\": \"f\\u00fcllt\", \"bekommst\": \"bekommt\", \"wurdest\": \"wurdet\", \"richte\": \"richtet\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiert\", \"kontaktiere\": \"kontaktiert\", \"Retourniere\": \"Retourniert\", \"retourniere\": \"retourniert\", \"brauchst\": \"braucht\", \"bist\": \"seid\", \"leite\": \"leitet\", \"weisst\": \"wisst\", \"einbezahlst\": \"einbezahlt\", \"einzahlst\": \"einzahlt\", \"zahle\": \"zahlt\", \"Zahle\": \"Zahlt\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',4,17,4);
INSERT INTO `geno_document` VALUES (103,'','2024-12-04 10:05:59.627168','2024-12-04 10:05:59.627203','Formular_Überprüfung_Belegung_Fahrzeuge_Klein_Anna.odt','{\"mietobjekt\": \"201 Wohnung (Musterweg 1), 9904 Kellerabteil (Musterweg 1)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Klein\", \"vorname\": \"Anna\"}], \"organisation\": \"\", \"vorname\": \"Anna\", \"name\": \"Klein\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"anna.klein@example.com\", \"geburtsdatum\": \"18.08.1991\", \"uuid\": \"1e87580c-5044-46d2-a89a-cdb41a3eee0a\", \"anrede\": \"Liebe Anna\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',5,17,4);
INSERT INTO `geno_document` VALUES (104,'','2024-12-04 10:05:59.677466','2024-12-04 10:05:59.677500','Formular_Überprüfung_Belegung_Fahrzeuge_Jensen_Hugo.odt','{\"mietobjekt\": \"202 Wohnung (Musterweg 1)\", \"mindestbelegung\": \"1\", \"bewohnende\": [{\"name\": \"Jensen\", \"vorname\": \"Hugo\"}], \"organisation\": \"\", \"vorname\": \"Hugo\", \"name\": \"Jensen\", \"strasse\": \"Musterweg 1\", \"roomnr\": \"\", \"wohnort\": \"3000 Bern\", \"telefon\": \"Keine Angabe\", \"email\": \"hugo.jensen@example.com\", \"geburtsdatum\": \"24.03.1977\", \"uuid\": \"e3bd6105-3630-4dad-8b78-cd54ae8c692c\", \"anrede\": \"Lieber Hugo\", \"dir\": \"dir\", \"dein\": \"dein\", \"Dein\": \"Dein\", \"deine\": \"deine\", \"Deine\": \"Deine\", \"deiner\": \"deiner\", \"deinen\": \"deinen\", \"deinem\": \"deinem\", \"Deinem\": \"Deinem\", \"deines\": \"deines\", \"dich\": \"dich\", \"du\": \"du\", \"Du\": \"Du\", \"eurem\": \"eurem\", \"euch\": \"euch\", \"hast\": \"hast\", \"kannst\": \"kannst\", \"leistest\": \"leistest\", \"w\\u00fcnschst\": \"w\\u00fcnschst\", \"findest\": \"findest\", \"erh\\u00e4ltst\": \"erh\\u00e4ltst\", \"sende\": \"sende\", \"verwende\": \"verwende\", \"beachte\": \"beachte\", \"gew\\u00e4hrst\": \"gew\\u00e4hrst\", \"planst\": \"planst\", \"wirst\": \"wirst\", \"m\\u00f6chtest\": \"m\\u00f6chtest\", \"f\\u00fclle\": \"f\\u00fclle\", \"bekommst\": \"bekommst\", \"wurdest\": \"wurdest\", \"richte\": \"richte\", \"richtet\": \"richtet\", \"Kontaktiere\": \"Kontaktiere\", \"kontaktiere\": \"kontaktiere\", \"Retourniere\": \"Retourniere\", \"retourniere\": \"retourniere\", \"brauchst\": \"brauchst\", \"bist\": \"bist\", \"leite\": \"leite\", \"weisst\": \"weisst\", \"einbezahlst\": \"einbezahlst\", \"einzahlst\": \"einzahlst\", \"zahle\": \"zahle\", \"Zahle\": \"Zahle\", \"datum\": \"04.12.2024\", \"monat\": \"Dezember\", \"jahr\": 2024, \"datum_plus30\": \"03.01.2025\", \"monat_plus30\": \"Januar\", \"jahr_plus30\": 2025, \"org_info\": {\"name\": \"Genossenschaft Musterweg\", \"street\": \"Musterweg 1\", \"city\": \"3000 Bern\", \"email\": \"info@cohiva.ch\", \"website\": \"www.cohiva.ch\"}}',6,17,4);
/*!40000 ALTER TABLE `geno_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_documenttype`
--

DROP TABLE IF EXISTS `geno_documenttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_documenttype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  `template_file` varchar(200) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `template_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `geno_documenttype_template_id_d3dc6efe_fk_geno_cont` (`template_id`),
  CONSTRAINT `geno_documenttype_template_id_d3dc6efe_fk_geno_cont` FOREIGN KEY (`template_id`) REFERENCES `geno_contenttemplate` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_documenttype`
--

LOCK TABLES `geno_documenttype` WRITE;
/*!40000 ALTER TABLE `geno_documenttype` DISABLE KEYS */;
INSERT INTO `geno_documenttype` VALUES (1,'','2024-11-06 16:14:02.624821','2024-11-06 16:34:23.447895','invoice','Standard QR-Rechnung','',1,1);
INSERT INTO `geno_documenttype` VALUES (2,'','2024-12-03 11:16:30.634245','2024-12-03 11:16:30.634284','memberletter','Bestätigung Mitgliedschaft','',1,2);
INSERT INTO `geno_documenttype` VALUES (3,'','2024-12-03 14:44:52.542905','2024-12-03 14:44:52.542933','statement','Kontoauszug Beteiligungen','',1,3);
INSERT INTO `geno_documenttype` VALUES (4,'','2024-12-04 10:02:51.800863','2024-12-04 10:02:51.800893','contract_check','Selbstdeklaration Belegungsrichtlinien','',1,8);
/*!40000 ALTER TABLE `geno_documenttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_genericattribute`
--

DROP TABLE IF EXISTS `geno_genericattribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_genericattribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(250) NOT NULL,
  `date` date DEFAULT NULL,
  `value` varchar(100) NOT NULL,
  `object_id` int(10) unsigned NOT NULL,
  `content_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_content_object_attribute_name` (`name`,`content_type_id`,`object_id`),
  KEY `geno_genericattribut_content_type_id_55577165_fk_django_co` (`content_type_id`),
  KEY `geno_genericattribute_name_d6a07af6` (`name`),
  CONSTRAINT `geno_genericattribut_content_type_id_55577165_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_genericattribute`
--

LOCK TABLES `geno_genericattribute` WRITE;
/*!40000 ALTER TABLE `geno_genericattribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `geno_genericattribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_invoice`
--

DROP TABLE IF EXISTS `geno_invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_invoice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(1000) NOT NULL,
  `year` int(11) DEFAULT NULL,
  `month` int(11) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `date` date NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `gnc_account_receivables` varchar(50) NOT NULL,
  `contract_id` int(11) DEFAULT NULL,
  `person_id` int(11) DEFAULT NULL,
  `gnc_account` varchar(50) NOT NULL,
  `gnc_transaction` varchar(1024) NOT NULL,
  `invoice_type` varchar(50) NOT NULL,
  `consolidated` tinyint(1) NOT NULL,
  `invoice_category_id` int(11) NOT NULL,
  `additional_info` varchar(255) NOT NULL,
  `reference_nr` varchar(50) NOT NULL,
  `transaction_id` varchar(150) NOT NULL,
  `is_additional_invoice` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_invoice_active_8ebbaac7` (`active`),
  KEY `geno_invoice_consolidated_a05ad12f` (`consolidated`),
  KEY `geno_invoice_invoice_category_id_356778e2_fk_geno_invo` (`invoice_category_id`),
  KEY `geno_invoice_invoice_type_efc8a8b4` (`invoice_type`),
  KEY `geno_invoice_month_d5014626` (`month`),
  KEY `geno_invoice_person_id_95aa339f_fk_geno_address_id` (`person_id`),
  KEY `geno_invoice_year_3885f085` (`year`),
  KEY `geno_invoice_reference_nr_475ab25a` (`reference_nr`),
  KEY `geno_invoice_transaction_id_889cda37` (`transaction_id`),
  KEY `geno_invoice_contract_id_cc312f9a_fk_geno_contract_id` (`contract_id`),
  KEY `geno_invoice_is_additional_invoice_f9eb8c27` (`is_additional_invoice`),
  CONSTRAINT `geno_invoice_contract_id_cc312f9a_fk_geno_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `geno_contract` (`id`),
  CONSTRAINT `geno_invoice_invoice_category_id_356778e2_fk_geno_invo` FOREIGN KEY (`invoice_category_id`) REFERENCES `geno_invoicecategory` (`id`),
  CONSTRAINT `geno_invoice_person_id_95aa339f_fk_geno_address_id` FOREIGN KEY (`person_id`) REFERENCES `geno_address` (`id`),
  CONSTRAINT `either_person_or_contract` CHECK (`person_id` is null and `contract_id` is not null or `person_id` is not null and `contract_id` is null)
) ENGINE=InnoDB AUTO_INCREMENT=681 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_invoice`
--

LOCK TABLES `geno_invoice` WRITE;
/*!40000 ALTER TABLE `geno_invoice` DISABLE KEYS */;
INSERT INTO `geno_invoice` VALUES (1,'','2024-11-19 16:09:54.028588','2024-12-18 15:30:01.138640','Nettomiete 06.2022 für 002/9902',2022,6,1,'2022-06-01',1950.00,'1102',1,NULL,'3000','a2407300e73347eab2399253999a1fec','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (2,'','2024-11-19 16:09:54.134410','2024-12-18 15:30:01.140637','Nebenkosten 06.2022 für 002/9902',2022,6,1,'2022-06-01',250.00,'1102',1,NULL,'2301','3bce492495b849c8b2ca68056c45c37b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (3,'','2024-11-19 16:09:56.965160','2024-12-18 15:32:44.402913','Nettomiete 06.2022 für 001/9901/9906',2022,6,1,'2022-06-01',1759.00,'1102',3,NULL,'3001','1db63f9232054a3f98b3e4aff130d079','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (4,'','2024-11-19 16:09:57.031646','2024-12-18 15:32:44.405012','Nebenkosten 06.2022 für 001/9901/9906',2022,6,1,'2022-06-01',208.00,'1102',3,NULL,'2301','4a695f833f2840369a475e3f4256c2b1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (5,'','2024-11-19 16:09:57.087354','2024-12-18 15:32:44.407014','Strompauschale 06.2022 für 001/9901/9906',2022,6,1,'2022-06-01',5.00,'1102',3,NULL,'2302','99e1dadc1cf94e11b3968980d47e65c5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (6,'','2024-11-19 16:10:00.189508','2024-12-18 15:30:01.383526','Nettomiete 06.2022 für 101/9903',2022,6,1,'2022-06-01',6690.00,'1102',4,NULL,'3000','f63c4f5e7a3d437f923baacc977ddf41','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (7,'','2024-11-19 16:10:00.244649','2024-12-18 15:30:01.385512','Nebenkosten 06.2022 für 101/9903',2022,6,1,'2022-06-01',635.00,'1102',4,NULL,'2301','92376f124a544111bca775463852e584','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (8,'','2024-11-19 16:10:03.157367','2025-04-23 08:44:57.012266','Nettomiete 06.2022 für 201/9904',2022,6,1,'2022-06-01',768.00,'1102',5,NULL,'3000','ea2ec8997c404f73a3737cd5582cf248','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (9,'','2024-11-19 16:10:03.416181','2025-04-23 08:44:57.014628','Nebenkosten 06.2022 für 201/9904',2022,6,1,'2022-06-01',82.00,'1102',5,NULL,'2301','923d3b5d08c5434b962bb990b534c45f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (10,'','2024-11-19 16:10:06.055865','2024-12-18 15:30:01.610042','Nettomiete 06.2022 für 202',2022,6,1,'2022-06-01',1125.00,'1102',6,NULL,'3000','b404be160b7a44f99f8c4bae05c1f02b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (11,'','2024-11-19 16:10:06.131520','2024-12-18 15:30:01.612128','Nebenkosten 06.2022 für 202',2022,6,1,'2022-06-01',195.00,'1102',6,NULL,'2301','1273cbd624244a4d9cc39ee6298a520f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (12,'','2024-11-19 16:10:08.927462','2024-12-18 15:32:44.692646','Nettomiete 06.2022 für 003/9906',2022,6,1,'2022-06-01',1265.00,'1102',7,NULL,'3001','4fb3a1bd7b354af5b393d5c1a0b41487','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (13,'','2024-11-19 16:10:08.974975','2024-12-18 15:32:44.694557','Nebenkosten 06.2022 für 003/9906',2022,6,1,'2022-06-01',187.00,'1102',7,NULL,'2301','ab7dada4202d40c89384a249461ca516','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (14,'','2024-11-19 16:10:09.030272','2024-12-18 15:32:44.696371','Strompauschale 06.2022 für 003/9906',2022,6,1,'2022-06-01',5.00,'1102',7,NULL,'2302','a88f694856534d5fa82cbd0521fed9cf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (15,'','2024-11-19 16:33:37.754659','2024-12-18 15:30:01.142433','Nettomiete 07.2022 für 002/9902',2022,7,1,'2022-07-01',1950.00,'1102',1,NULL,'3000','f88df88d7ce44d8aa1870245165e4b0e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (16,'','2024-11-19 16:33:37.821917','2024-12-18 15:30:01.144120','Nebenkosten 07.2022 für 002/9902',2022,7,1,'2022-07-01',250.00,'1102',1,NULL,'2301','d725aab485d24491acc1968b2c874f13','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (17,'','2024-11-19 16:33:37.896768','2024-12-18 15:32:44.409073','Nettomiete 07.2022 für 001/9901/9906',2022,7,1,'2022-07-01',1759.00,'1102',3,NULL,'3001','cbb6000f7663447889ee168df1c4bf22','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (18,'','2024-11-19 16:33:38.018991','2024-12-18 15:32:44.411148','Nebenkosten 07.2022 für 001/9901/9906',2022,7,1,'2022-07-01',208.00,'1102',3,NULL,'2301','13e19a4ee8e14bfbb41353ff6f0f3b61','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (19,'','2024-11-19 16:33:38.095804','2024-12-18 15:32:44.413059','Strompauschale 07.2022 für 001/9901/9906',2022,7,1,'2022-07-01',5.00,'1102',3,NULL,'2302','3358331de61b4db8bfc0371b0b3b4a93','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (20,'','2024-11-19 16:33:38.156089','2024-12-18 15:30:01.387545','Nettomiete 07.2022 für 101/9903',2022,7,1,'2022-07-01',6690.00,'1102',4,NULL,'3000','5f4848206feb40fe81bb869c8e9bf15d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (21,'','2024-11-19 16:33:38.206157','2024-12-18 15:30:01.389346','Nebenkosten 07.2022 für 101/9903',2022,7,1,'2022-07-01',635.00,'1102',4,NULL,'2301','1758dd8561d74d658e68937b4b21e970','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (22,'','2024-11-19 16:33:38.271652','2025-04-23 08:44:57.016817','Nettomiete 07.2022 für 201/9904',2022,7,1,'2022-07-01',768.00,'1102',5,NULL,'3000','2bdba522ecc84630879794a12a4e6fc5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (23,'','2024-11-19 16:33:38.338207','2025-04-23 08:44:57.018864','Nebenkosten 07.2022 für 201/9904',2022,7,1,'2022-07-01',82.00,'1102',5,NULL,'2301','a2fde21fae584886a5ee4b482208199c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (24,'','2024-11-19 16:33:38.405631','2024-12-18 15:30:01.614009','Nettomiete 07.2022 für 202',2022,7,1,'2022-07-01',1125.00,'1102',6,NULL,'3000','13417c76e5f541ddb99e416fc6fef7a9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (25,'','2024-11-19 16:33:38.464178','2024-12-18 15:30:01.615826','Nebenkosten 07.2022 für 202',2022,7,1,'2022-07-01',195.00,'1102',6,NULL,'2301','56f8baef442b4594901830238be4b9d9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (26,'','2024-11-19 16:33:38.541009','2024-12-18 15:32:44.697927','Nettomiete 07.2022 für 003/9906',2022,7,1,'2022-07-01',1265.00,'1102',7,NULL,'3001','582d0a386e4f46eda97edaee736fe226','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (27,'','2024-11-19 16:33:38.626340','2024-12-18 15:32:44.699818','Nebenkosten 07.2022 für 003/9906',2022,7,1,'2022-07-01',187.00,'1102',7,NULL,'2301','48f93bb5feb14790b4be5e8ce58e7397','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (28,'','2024-11-19 16:33:38.684524','2024-12-18 15:32:44.701346','Strompauschale 07.2022 für 003/9906',2022,7,1,'2022-07-01',5.00,'1102',7,NULL,'2302','465f2efda4704b09bf6e6bc14b355c52','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (29,'','2024-11-19 16:34:41.389012','2024-12-18 15:30:01.801868','Nettomiete 10.2024 für 002/9902',2024,10,1,'2024-10-01',1950.00,'1102',8,NULL,'3000','8941df99014a4ccc96c68d7a700393f3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (30,'','2024-11-19 16:34:41.479370','2024-12-18 15:30:01.803547','Nebenkosten 10.2024 für 002/9902',2024,10,1,'2024-10-01',250.00,'1102',8,NULL,'2301','0736b40b12954b95854bd37090e74fc0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (31,'','2024-11-19 16:34:45.308856','2024-12-18 15:30:01.798608','Nettomiete 09.2024 für 002/9902',2024,9,1,'2024-09-01',1950.00,'1102',8,NULL,'3000','426464303ca448fb929a3ec5ee28d89f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (32,'','2024-11-19 16:34:45.365002','2024-12-18 15:30:01.800266','Nebenkosten 09.2024 für 002/9902',2024,9,1,'2024-09-01',250.00,'1102',8,NULL,'2301','a8a8eddfb4454c8d92cc773a267e22f7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (33,'','2024-11-19 16:34:45.449310','2024-12-18 15:30:01.794974','Nettomiete 08.2024 für 002/9902',2024,8,1,'2024-08-01',1950.00,'1102',8,NULL,'3000','c489c9e49ffa4605a32d570b1ca550eb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (34,'','2024-11-19 16:34:45.554139','2024-12-18 15:30:01.796778','Nebenkosten 08.2024 für 002/9902',2024,8,1,'2024-08-01',250.00,'1102',8,NULL,'2301','2250762ad1fe49408f72e5e4437926d5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (35,'','2024-11-19 16:34:45.632074','2025-04-23 08:45:54.249344','Nettomiete 10.2024 für 101/9903',2024,10,1,'2024-10-01',6690.00,'1102',9,NULL,'3000','e5e604fba81d4b09b8d9303eee0d149d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (36,'','2024-11-19 16:34:45.697277','2025-04-23 08:45:54.251538','Nebenkosten 10.2024 für 101/9903',2024,10,1,'2024-10-01',635.00,'1102',9,NULL,'2301','c1a31beec53b4037877b3e5f188fdd52','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (37,'','2024-11-19 16:34:48.442991','2025-04-23 08:45:54.244811','Nettomiete 09.2024 für 101/9903',2024,9,1,'2024-09-01',6690.00,'1102',9,NULL,'3000','c40380f062ad4afaae13b022a05c91c7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (38,'','2024-11-19 16:34:48.504031','2025-04-23 08:45:54.247272','Nebenkosten 09.2024 für 101/9903',2024,9,1,'2024-09-01',635.00,'1102',9,NULL,'2301','7afc34d5b17048b6943bafad756c63fc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (39,'','2024-11-19 16:34:48.573901','2025-04-23 08:45:54.240075','Nettomiete 08.2024 für 101/9903',2024,8,1,'2024-08-01',6690.00,'1102',9,NULL,'3000','030c1151a7f440e6a680dd07abb4e0d7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (40,'','2024-11-19 16:34:48.632784','2025-04-23 08:45:54.242655','Nebenkosten 08.2024 für 101/9903',2024,8,1,'2024-08-01',635.00,'1102',9,NULL,'2301','5fde758fe1724a599bea9f545cc9d928','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (41,'','2024-11-19 16:34:48.712830','2025-04-23 08:42:37.947806','Nettomiete 10.2024 für 201/9904',2024,10,1,'2024-10-01',768.00,'1102',10,NULL,'3000','545915359ec5441486ec32057347815c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (42,'','2024-11-19 16:34:48.776374','2025-04-23 08:42:37.949659','Nebenkosten 10.2024 für 201/9904',2024,10,1,'2024-10-01',82.00,'1102',10,NULL,'2301','bf2a94a8008f441cadde4c8bd4137fb5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (43,'','2024-11-19 16:34:51.784507','2025-04-23 08:42:37.943637','Nettomiete 09.2024 für 201/9904',2024,9,1,'2024-09-01',768.00,'1102',10,NULL,'3000','920a9bc2223642df9e4e3a53ed386702','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (44,'','2024-11-19 16:34:51.844163','2025-04-23 08:42:37.945763','Nebenkosten 09.2024 für 201/9904',2024,9,1,'2024-09-01',82.00,'1102',10,NULL,'2301','162d3ed1d59a4148a550bc2a478469a6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (45,'','2024-11-19 16:34:51.909647','2025-04-23 08:42:37.939718','Nettomiete 08.2024 für 201/9904',2024,8,1,'2024-08-01',768.00,'1102',10,NULL,'3000','604cc21ecc1147dbbd6f3e0f3ca97fa0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (46,'','2024-11-19 16:34:52.027133','2025-04-23 08:42:37.941803','Nebenkosten 08.2024 für 201/9904',2024,8,1,'2024-08-01',82.00,'1102',10,NULL,'2301','cd42b187fe9e4c3aa669b4fe6bf2eb33','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (47,'','2024-11-19 16:34:52.112306','2024-12-18 15:32:44.878406','Nettomiete 10.2024 für 202/9905',2024,10,1,'2024-10-01',1125.00,'1102',11,NULL,'3000','bff1b8a1a43e4c298567f59eefa9e263','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (48,'','2024-11-19 16:34:52.174337','2024-12-18 15:32:44.880567','Nebenkosten 10.2024 für 202/9905',2024,10,1,'2024-10-01',195.00,'1102',11,NULL,'2301','ea43af5ae6ba4768a371db7a76b67949','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (49,'','2024-11-19 16:34:54.936868','2024-12-18 15:32:44.874369','Nettomiete 09.2024 für 202/9905',2024,9,1,'2024-09-01',1125.00,'1102',11,NULL,'3000','9d64eb58c7cc4b3b956302d9ddfa0f79','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (50,'','2024-11-19 16:34:55.001611','2024-12-18 15:32:44.876366','Nebenkosten 09.2024 für 202/9905',2024,9,1,'2024-09-01',195.00,'1102',11,NULL,'2301','ff681fc4193848d2ba870659bbc2cf97','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (51,'','2024-11-19 16:34:55.072019','2024-12-18 15:32:44.870430','Nettomiete 08.2024 für 202/9905',2024,8,1,'2024-08-01',1125.00,'1102',11,NULL,'3000','425a0f197ffa4f27b3780844fc5694af','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (52,'','2024-11-19 16:34:55.130667','2024-12-18 15:32:44.872467','Nebenkosten 08.2024 für 202/9905',2024,8,1,'2024-08-01',195.00,'1102',11,NULL,'2301','b1d05ed2b9624db7b938c8bd5d9ac1f5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (53,'','2024-11-19 16:34:55.228882','2024-12-18 15:30:01.850170','Nettomiete 10.2024 für 203',2024,10,1,'2024-10-01',445.00,'1102',12,NULL,'3000','111cb19624194056a0090375183e5c3a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (54,'','2024-11-19 16:34:55.313149','2024-12-18 15:30:01.852084','Nebenkosten 10.2024 für 203',2024,10,1,'2024-10-01',55.00,'1102',12,NULL,'2301','ac87a3553e4f4c26b48d9a4160e4f529','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (55,'','2024-11-19 16:34:57.945429','2024-12-18 15:30:01.846554','Nettomiete 09.2024 für 203',2024,9,1,'2024-09-01',445.00,'1102',12,NULL,'3000','6867a03400a247b590924adb3da5e509','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (56,'','2024-11-19 16:34:58.011118','2024-12-18 15:30:01.848445','Nebenkosten 09.2024 für 203',2024,9,1,'2024-09-01',55.00,'1102',12,NULL,'2301','0b43166078b94cd7a1eff222924ed3fd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (57,'','2024-11-19 16:34:58.074948','2024-12-18 15:30:01.842741','Nettomiete 08.2024 für 203',2024,8,1,'2024-08-01',445.00,'1102',12,NULL,'3000','6a25dae6cbb34a1cb999e6f957650236','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (58,'','2024-11-19 16:34:58.136044','2024-12-18 15:30:01.844822','Nebenkosten 08.2024 für 203',2024,8,1,'2024-08-01',55.00,'1102',12,NULL,'2301','fd811bbc922f4af295f7fc9c8bada006','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (59,'','2024-11-19 16:34:58.216793','2025-04-23 08:44:30.375040','Nettomiete 10.2024 für 001/9901',2024,10,1,'2024-10-01',1610.00,'1102',13,NULL,'3000','33459adf5c934d07a57099daecc284f0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (60,'','2024-11-19 16:34:58.276086','2025-04-23 08:44:30.377029','Nebenkosten 10.2024 für 001/9901',2024,10,1,'2024-10-01',180.00,'1102',13,NULL,'2301','88b5f0e48b874345b6154f05d160b1f4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (61,'','2024-11-19 16:35:01.346872','2025-04-23 08:44:30.370508','Nettomiete 09.2024 für 001/9901',2024,9,1,'2024-09-01',1610.00,'1102',13,NULL,'3000','aabf3f5c62864e6abb2749c8452bb36c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (62,'','2024-11-19 16:35:01.409989','2025-04-23 08:44:30.372805','Nebenkosten 09.2024 für 001/9901',2024,9,1,'2024-09-01',180.00,'1102',13,NULL,'2301','d94bfee9999847078eb5faf31f8ae28a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (63,'','2024-11-19 16:35:01.486788','2025-04-23 08:44:30.364674','Nettomiete 08.2024 für 001/9901',2024,8,1,'2024-08-01',1610.00,'1102',13,NULL,'3000','021ee4f6aec4459cadbffe548ecb48b6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (64,'','2024-11-19 16:35:01.545431','2025-04-23 08:44:30.368336','Nebenkosten 08.2024 für 001/9901',2024,8,1,'2024-08-01',180.00,'1102',13,NULL,'2301','307ceaca76e14adb8914e473c2983f0f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (65,'','2024-11-19 16:35:01.628918','2024-12-18 15:30:01.868970','Nettomiete 10.2024 für PP-01',2024,10,1,'2024-10-01',120.00,'1102',14,NULL,'3002','88e44b9b04bd43b1941eb438e92e0bdf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (66,'','2024-11-19 16:35:04.326295','2024-12-18 15:30:01.867275','Nettomiete 09.2024 für PP-01',2024,9,1,'2024-09-01',120.00,'1102',14,NULL,'3002','51b2baac0ce440b0b00221b124f8f1d6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (67,'','2024-11-19 16:35:04.402492','2024-12-18 15:30:01.865663','Nettomiete 08.2024 für PP-01',2024,8,1,'2024-08-01',120.00,'1102',14,NULL,'3002','6a1786f1af95498bb3c12004a88daa6a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (68,'','2024-11-19 16:35:04.512425','2024-12-18 15:32:44.898960','Nettomiete 10.2024 für PP-01',2024,10,1,'2024-10-01',120.00,'1102',15,NULL,'3002','3cbba95f0a9f402d8a60ed796bb50d71','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (69,'','2024-11-19 16:35:07.509876','2024-12-18 15:32:44.896153','Nettomiete 09.2024 für PP-01',2024,9,1,'2024-09-01',120.00,'1102',15,NULL,'3002','717325e258d44514965d308d1d4de38c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (70,'','2024-11-19 16:35:07.578795','2024-12-18 15:32:44.894179','Nettomiete 08.2024 für PP-01',2024,8,1,'2024-08-01',120.00,'1102',15,NULL,'3002','0be646c93ae6499dabb9ac5ed7824353','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (71,'','2024-11-19 16:35:07.665779','2024-12-18 15:30:01.243803','Nettomiete 10.2024 für 002/9902',2024,10,1,'2024-10-01',1950.00,'1102',1,NULL,'3000','d75207f6cf0e43fb8ba6b29367448a1b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (72,'','2024-11-19 16:35:07.730693','2024-12-18 15:30:01.245541','Nebenkosten 10.2024 für 002/9902',2024,10,1,'2024-10-01',250.00,'1102',1,NULL,'2301','52f6440e4e1a430a97fc3f4ba4478567','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (73,'','2024-11-19 16:35:07.803507','2024-12-18 15:30:01.240155','Nettomiete 09.2024 für 002/9902',2024,9,1,'2024-09-01',1950.00,'1102',1,NULL,'3000','a83c864a05ba4b99b1631d0d9799520e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (74,'','2024-11-19 16:35:07.862748','2024-12-18 15:30:01.241977','Nebenkosten 09.2024 für 002/9902',2024,9,1,'2024-09-01',250.00,'1102',1,NULL,'2301','9d5da22f459042b2bc0287a57cfc883b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (75,'','2024-11-19 16:35:07.930028','2024-12-18 15:30:01.236676','Nettomiete 08.2024 für 002/9902',2024,8,1,'2024-08-01',1950.00,'1102',1,NULL,'3000','7e1688e74eed4fe59389142bb269e4da','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (76,'','2024-11-19 16:35:08.009853','2024-12-18 15:30:01.238386','Nebenkosten 08.2024 für 002/9902',2024,8,1,'2024-08-01',250.00,'1102',1,NULL,'2301','b8ab2c9a18f640be875393da894008cf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (77,'','2024-11-19 16:35:08.078116','2024-12-18 15:30:01.231767','Nettomiete 07.2024 für 002/9902',2024,7,1,'2024-07-01',1950.00,'1102',1,NULL,'3000','10a2644a06fc401bbea4c7b3fe11ffdd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (78,'','2024-11-19 16:35:08.137423','2024-12-18 15:30:01.234682','Nebenkosten 07.2024 für 002/9902',2024,7,1,'2024-07-01',250.00,'1102',1,NULL,'2301','b47527c7a68246aa8a0a1e6e79ac2692','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (79,'','2024-11-19 16:35:08.266273','2024-12-18 15:30:01.228456','Nettomiete 06.2024 für 002/9902',2024,6,1,'2024-06-01',1950.00,'1102',1,NULL,'3000','80f9bc88c0c14daf860d6c8508e5cb5d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (80,'','2024-11-19 16:35:08.325648','2024-12-18 15:30:01.230181','Nebenkosten 06.2024 für 002/9902',2024,6,1,'2024-06-01',250.00,'1102',1,NULL,'2301','1ffcab4dcd9741b6bb7913694bd62a3d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (81,'','2024-11-19 16:35:08.427107','2024-12-18 15:30:01.224580','Nettomiete 05.2024 für 002/9902',2024,5,1,'2024-05-01',1950.00,'1102',1,NULL,'3000','ae03570f3e984c6597627340bd4b531b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (82,'','2024-11-19 16:35:08.484585','2024-12-18 15:30:01.226477','Nebenkosten 05.2024 für 002/9902',2024,5,1,'2024-05-01',250.00,'1102',1,NULL,'2301','419e9fe346454ee493a0f57c8c6b7058','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (83,'','2024-11-19 16:35:08.554329','2024-12-18 15:30:01.221127','Nettomiete 04.2024 für 002/9902',2024,4,1,'2024-04-01',1950.00,'1102',1,NULL,'3000','caa84faaf608439399c4bd802bc09775','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (84,'','2024-11-19 16:35:08.613666','2024-12-18 15:30:01.222742','Nebenkosten 04.2024 für 002/9902',2024,4,1,'2024-04-01',250.00,'1102',1,NULL,'2301','f01efd8f3e9e4224b104c40282b7ce7f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (85,'','2024-11-19 16:35:08.780280','2024-12-18 15:30:01.217406','Nettomiete 03.2024 für 002/9902',2024,3,1,'2024-03-01',1950.00,'1102',1,NULL,'3000','966cb0926190438cbdb31c42465dcbf6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (86,'','2024-11-19 16:35:08.838982','2024-12-18 15:30:01.219204','Nebenkosten 03.2024 für 002/9902',2024,3,1,'2024-03-01',250.00,'1102',1,NULL,'2301','fbb75c52c2d7494fa744004e6ecba631','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (87,'','2024-11-19 16:35:08.913403','2024-12-18 15:30:01.213736','Nettomiete 02.2024 für 002/9902',2024,2,1,'2024-02-01',1950.00,'1102',1,NULL,'3000','e63e7d07d0b34494a539d5f85dfc6cb4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (88,'','2024-11-19 16:35:08.973602','2024-12-18 15:30:01.215348','Nebenkosten 02.2024 für 002/9902',2024,2,1,'2024-02-01',250.00,'1102',1,NULL,'2301','d09d9f352db7481d8f7029f2e1117c66','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (89,'','2024-11-19 16:35:09.043572','2024-12-18 15:30:01.210381','Nettomiete 01.2024 für 002/9902',2024,1,1,'2024-01-01',1950.00,'1102',1,NULL,'3000','11e410da168e4b378a46e697412ccb1e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (90,'','2024-11-19 16:35:09.113395','2024-12-18 15:30:01.212109','Nebenkosten 01.2024 für 002/9902',2024,1,1,'2024-01-01',250.00,'1102',1,NULL,'2301','aaf4dc2ef26740a79504b714cabf87f2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (91,'','2024-11-19 16:35:09.180992','2024-12-18 15:30:01.203464','Nettomiete 12.2023 für 002/9902',2023,12,1,'2023-12-01',1950.00,'1102',1,NULL,'3000','1cc5cd65ef794ff79af83b6cd2c6f7f6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (92,'','2024-11-19 16:35:09.246852','2024-12-18 15:30:01.208038','Nebenkosten 12.2023 für 002/9902',2023,12,1,'2023-12-01',250.00,'1102',1,NULL,'2301','60eac00120ec48fcad7f48025cb69582','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (93,'','2024-11-19 16:35:09.320646','2024-12-18 15:30:01.199097','Nettomiete 11.2023 für 002/9902',2023,11,1,'2023-11-01',1950.00,'1102',1,NULL,'3000','10c6e3b1b00247dd90b240923ff03851','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (94,'','2024-11-19 16:35:09.378967','2024-12-18 15:30:01.201084','Nebenkosten 11.2023 für 002/9902',2023,11,1,'2023-11-01',250.00,'1102',1,NULL,'2301','08678d1b26bd443da70505f44de16f11','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (95,'','2024-11-19 16:35:09.446546','2024-12-18 15:30:01.195459','Nettomiete 10.2023 für 002/9902',2023,10,1,'2023-10-01',1950.00,'1102',1,NULL,'3000','b8b45a4cee5c4f7aaa209a8c420129e9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (96,'','2024-11-19 16:35:09.504505','2024-12-18 15:30:01.197170','Nebenkosten 10.2023 für 002/9902',2023,10,1,'2023-10-01',250.00,'1102',1,NULL,'2301','54fbc93da6794585ade3996766874969','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (97,'','2024-11-19 16:35:09.574664','2024-12-18 15:30:01.191953','Nettomiete 09.2023 für 002/9902',2023,9,1,'2023-09-01',1950.00,'1102',1,NULL,'3000','9c86e589858c4a92b82c2c641689d94b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (98,'','2024-11-19 16:35:09.653331','2024-12-18 15:30:01.193680','Nebenkosten 09.2023 für 002/9902',2023,9,1,'2023-09-01',250.00,'1102',1,NULL,'2301','e77bd92b4bdb4fedbfde3ea404bda8be','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (99,'','2024-11-19 16:35:09.722310','2024-12-18 15:30:01.188420','Nettomiete 08.2023 für 002/9902',2023,8,1,'2023-08-01',1950.00,'1102',1,NULL,'3000','0dcf7344ecea4121bb817a9ec6a2b9e0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (100,'','2024-11-19 16:35:09.809417','2024-12-18 15:30:01.190186','Nebenkosten 08.2023 für 002/9902',2023,8,1,'2023-08-01',250.00,'1102',1,NULL,'2301','7396a41ba9ad413fb9b131abf887203f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (101,'','2024-11-19 16:35:09.897524','2024-12-18 15:30:01.184898','Nettomiete 07.2023 für 002/9902',2023,7,1,'2023-07-01',1950.00,'1102',1,NULL,'3000','e1fc6bc2aad4481dbe3caf2b89ce2649','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (102,'','2024-11-19 16:35:09.957819','2024-12-18 15:30:01.186647','Nebenkosten 07.2023 für 002/9902',2023,7,1,'2023-07-01',250.00,'1102',1,NULL,'2301','5c6b7b4206ed448ca2a2a13308590b9a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (103,'','2024-11-19 16:35:10.026378','2024-12-18 15:30:01.181515','Nettomiete 06.2023 für 002/9902',2023,6,1,'2023-06-01',1950.00,'1102',1,NULL,'3000','6e77d6bd30234de6990acbf46ae5a6a9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (104,'','2024-11-19 16:35:10.086266','2024-12-18 15:30:01.183084','Nebenkosten 06.2023 für 002/9902',2023,6,1,'2023-06-01',250.00,'1102',1,NULL,'2301','f2aae5b89e914020b8038bcf6ed6967a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (105,'','2024-11-19 16:35:10.165525','2024-12-18 15:30:01.177919','Nettomiete 05.2023 für 002/9902',2023,5,1,'2023-05-01',1950.00,'1102',1,NULL,'3000','bedd79da6e1f469a8c83d1dafad49f7a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (106,'','2024-11-19 16:35:10.271942','2024-12-18 15:30:01.179875','Nebenkosten 05.2023 für 002/9902',2023,5,1,'2023-05-01',250.00,'1102',1,NULL,'2301','d31dd947df9b42aaa91e04310ac25a65','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (107,'','2024-11-19 16:35:10.336370','2024-12-18 15:30:01.174022','Nettomiete 04.2023 für 002/9902',2023,4,1,'2023-04-01',1950.00,'1102',1,NULL,'3000','419e6bac3bf2408ead200ecb7712d049','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (108,'','2024-11-19 16:35:10.514357','2024-12-18 15:30:01.175944','Nebenkosten 04.2023 für 002/9902',2023,4,1,'2023-04-01',250.00,'1102',1,NULL,'2301','442a24ba15194963969b86b400db1f3d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (109,'','2024-11-19 16:35:10.602598','2024-12-18 15:30:01.170673','Nettomiete 03.2023 für 002/9902',2023,3,1,'2023-03-01',1950.00,'1102',1,NULL,'3000','e403743d2a1943f386e9478d36f04aa1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (110,'','2024-11-19 16:35:10.746488','2024-12-18 15:30:01.172221','Nebenkosten 03.2023 für 002/9902',2023,3,1,'2023-03-01',250.00,'1102',1,NULL,'2301','f8c9aa655f574c899241d6c641be663b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (111,'','2024-11-19 16:35:10.815609','2024-12-18 15:30:01.167440','Nettomiete 02.2023 für 002/9902',2023,2,1,'2023-02-01',1950.00,'1102',1,NULL,'3000','cfddae151fdb4fd0987d96c105fcee31','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (112,'','2024-11-19 16:35:10.874860','2024-12-18 15:30:01.169053','Nebenkosten 02.2023 für 002/9902',2023,2,1,'2023-02-01',250.00,'1102',1,NULL,'2301','6ed50c67392e46ff827bd186c028e5db','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (113,'','2024-11-19 16:35:10.947474','2024-12-18 15:30:01.163912','Nettomiete 01.2023 für 002/9902',2023,1,1,'2023-01-01',1950.00,'1102',1,NULL,'3000','5d5bda4ba76047e0ab97b32ff44942ae','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (114,'','2024-11-19 16:35:11.059245','2024-12-18 15:30:01.165622','Nebenkosten 01.2023 für 002/9902',2023,1,1,'2023-01-01',250.00,'1102',1,NULL,'2301','c21c574d87584c55a1c0f8138c5ab629','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (115,'','2024-11-19 16:35:11.130112','2024-12-18 15:30:01.160109','Nettomiete 12.2022 für 002/9902',2022,12,1,'2022-12-01',1950.00,'1102',1,NULL,'3000','f35f54ebde1143788c7f7b19c9471fea','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (116,'','2024-11-19 16:35:11.188899','2024-12-18 15:30:01.161796','Nebenkosten 12.2022 für 002/9902',2022,12,1,'2022-12-01',250.00,'1102',1,NULL,'2301','2942b383aaad457ab4223e7c6fd6c93d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (117,'','2024-11-19 16:35:11.257671','2024-12-18 15:30:01.156658','Nettomiete 11.2022 für 002/9902',2022,11,1,'2022-11-01',1950.00,'1102',1,NULL,'3000','2816fdcfae3e4357bf60dfedc83d5bb7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (118,'','2024-11-19 16:35:11.317152','2024-12-18 15:30:01.158312','Nebenkosten 11.2022 für 002/9902',2022,11,1,'2022-11-01',250.00,'1102',1,NULL,'2301','39be5be51dee4015872fff33663277aa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (119,'','2024-11-19 16:35:11.401489','2024-12-18 15:30:01.152946','Nettomiete 10.2022 für 002/9902',2022,10,1,'2022-10-01',1950.00,'1102',1,NULL,'3000','7be6110983384afa9e1f39a3a27a8eb4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (120,'','2024-11-19 16:35:11.460615','2024-12-18 15:30:01.154771','Nebenkosten 10.2022 für 002/9902',2022,10,1,'2022-10-01',250.00,'1102',1,NULL,'2301','12bc53b875ec421ca968b807d57f431a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (121,'','2024-11-19 16:35:11.525644','2024-12-18 15:30:01.149503','Nettomiete 09.2022 für 002/9902',2022,9,1,'2022-09-01',1950.00,'1102',1,NULL,'3000','7bf8fc521b8f4e4c9ab7126708e86d27','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (122,'','2024-11-19 16:35:11.581636','2024-12-18 15:30:01.151095','Nebenkosten 09.2022 für 002/9902',2022,9,1,'2022-09-01',250.00,'1102',1,NULL,'2301','551a3d2c29c6473bac198d299e992f7d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (123,'','2024-11-19 16:35:11.667589','2024-12-18 15:30:01.145801','Nettomiete 08.2022 für 002/9902',2022,8,1,'2022-08-01',1950.00,'1102',1,NULL,'3000','88110ce0f9e047888a2042afdd4faee1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (124,'','2024-11-19 16:35:11.725472','2024-12-18 15:30:01.147806','Nebenkosten 08.2022 für 002/9902',2022,8,1,'2022-08-01',250.00,'1102',1,NULL,'2301','91a79f5f202947f482aea757a835a1aa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (125,'','2024-11-19 16:35:11.799859','2024-12-18 15:32:44.562671','Nettomiete 10.2024 für 001/9901/9906',2024,10,1,'2024-10-01',1759.00,'1102',3,NULL,'3001','2aeae20f663548babe574f3740b45ade','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (126,'','2024-11-19 16:35:11.858691','2024-12-18 15:32:44.564238','Nebenkosten 10.2024 für 001/9901/9906',2024,10,1,'2024-10-01',208.00,'1102',3,NULL,'2301','e904fe6218e143afad3c3b9d66d235da','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (127,'','2024-11-19 16:35:11.917488','2024-12-18 15:32:44.567181','Strompauschale 10.2024 für 001/9901/9906',2024,10,1,'2024-10-01',5.00,'1102',3,NULL,'2302','dd5d3959dc6a4c9b93b8b44e287f245a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (128,'','2024-11-19 16:35:11.992958','2024-12-18 15:32:44.556875','Nettomiete 09.2024 für 001/9901/9906',2024,9,1,'2024-09-01',1759.00,'1102',3,NULL,'3001','42a973512060490cb424dec6a6ba8ea6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (129,'','2024-11-19 16:35:12.050227','2024-12-18 15:32:44.559112','Nebenkosten 09.2024 für 001/9901/9906',2024,9,1,'2024-09-01',208.00,'1102',3,NULL,'2301','cd389c820ec0414b82d3e23ea2a73877','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (130,'','2024-11-19 16:35:12.105632','2024-12-18 15:32:44.560991','Strompauschale 09.2024 für 001/9901/9906',2024,9,1,'2024-09-01',5.00,'1102',3,NULL,'2302','d88b231f38e743efbaaecf7b2b8993c2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (131,'','2024-11-19 16:35:12.175114','2024-12-18 15:32:44.550029','Nettomiete 08.2024 für 001/9901/9906',2024,8,1,'2024-08-01',1759.00,'1102',3,NULL,'3001','68d6fbcca81947af88f0e3596db8efc7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (132,'','2024-11-19 16:35:12.235661','2024-12-18 15:32:44.552128','Nebenkosten 08.2024 für 001/9901/9906',2024,8,1,'2024-08-01',208.00,'1102',3,NULL,'2301','56b8f49e1d6841cea937c2f49f8a02ea','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (133,'','2024-11-19 16:35:12.294130','2024-12-18 15:32:44.554454','Strompauschale 08.2024 für 001/9901/9906',2024,8,1,'2024-08-01',5.00,'1102',3,NULL,'2302','efd1888238164f538b0074c624d82063','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (134,'','2024-11-19 16:35:12.370178','2024-12-18 15:32:44.544614','Nettomiete 07.2024 für 001/9901/9906',2024,7,1,'2024-07-01',1759.00,'1102',3,NULL,'3001','60ce46e93b8a46aaa874d741de024392','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (135,'','2024-11-19 16:35:12.426610','2024-12-18 15:32:44.546411','Nebenkosten 07.2024 für 001/9901/9906',2024,7,1,'2024-07-01',208.00,'1102',3,NULL,'2301','b543c761cf3d4755996b52df1b6f8a57','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (136,'','2024-11-19 16:35:12.483886','2024-12-18 15:32:44.548118','Strompauschale 07.2024 für 001/9901/9906',2024,7,1,'2024-07-01',5.00,'1102',3,NULL,'2302','234e136dc3334d798a71464402997e4b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (137,'','2024-11-19 16:35:12.560801','2024-12-18 15:32:44.539050','Nettomiete 06.2024 für 001/9901/9906',2024,6,1,'2024-06-01',1759.00,'1102',3,NULL,'3001','8b1ab0f698ef419fabf2ed3c774052c4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (138,'','2024-11-19 16:35:12.624527','2024-12-18 15:32:44.540774','Nebenkosten 06.2024 für 001/9901/9906',2024,6,1,'2024-06-01',208.00,'1102',3,NULL,'2301','f4a78febd7554009b2ff340edc7c14ce','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (139,'','2024-11-19 16:35:12.683620','2024-12-18 15:32:44.542574','Strompauschale 06.2024 für 001/9901/9906',2024,6,1,'2024-06-01',5.00,'1102',3,NULL,'2302','40550cdc680f4f9397f0dd0ae766d2ac','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (140,'','2024-11-19 16:35:12.760991','2024-12-18 15:32:44.533686','Nettomiete 05.2024 für 001/9901/9906',2024,5,1,'2024-05-01',1759.00,'1102',3,NULL,'3001','8087ce6a3df641f3a358c6155fe70a03','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (141,'','2024-11-19 16:35:12.827126','2024-12-18 15:32:44.535534','Nebenkosten 05.2024 für 001/9901/9906',2024,5,1,'2024-05-01',208.00,'1102',3,NULL,'2301','1c543f007a8a47d68b5b215459ada3dd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (142,'','2024-11-19 16:35:12.889403','2024-12-18 15:32:44.537320','Strompauschale 05.2024 für 001/9901/9906',2024,5,1,'2024-05-01',5.00,'1102',3,NULL,'2302','39d8892f168c44bdb0a531ecb9c54646','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (143,'','2024-11-19 16:35:12.963564','2024-12-18 15:32:44.528418','Nettomiete 04.2024 für 001/9901/9906',2024,4,1,'2024-04-01',1759.00,'1102',3,NULL,'3001','a4aa70bc422c433cb1129ebe17823d3d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (144,'','2024-11-19 16:35:13.022864','2024-12-18 15:32:44.530150','Nebenkosten 04.2024 für 001/9901/9906',2024,4,1,'2024-04-01',208.00,'1102',3,NULL,'2301','90edfb50694442449ebeae80bad7051b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (145,'','2024-11-19 16:35:13.083530','2024-12-18 15:32:44.531902','Strompauschale 04.2024 für 001/9901/9906',2024,4,1,'2024-04-01',5.00,'1102',3,NULL,'2302','3f18066cb87f4b598620d478118af1e0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (146,'','2024-11-19 16:35:13.159525','2024-12-18 15:32:44.522725','Nettomiete 03.2024 für 001/9901/9906',2024,3,1,'2024-03-01',1759.00,'1102',3,NULL,'3001','b3f76db66b6b4b5680f7b01661b50043','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (147,'','2024-11-19 16:35:13.221682','2024-12-18 15:32:44.524604','Nebenkosten 03.2024 für 001/9901/9906',2024,3,1,'2024-03-01',208.00,'1102',3,NULL,'2301','6800c8e147a44909800ee5aa98a9b2fe','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (148,'','2024-11-19 16:35:13.308761','2024-12-18 15:32:44.526531','Strompauschale 03.2024 für 001/9901/9906',2024,3,1,'2024-03-01',5.00,'1102',3,NULL,'2302','fcc947ec35e04b1c824fc19e8487d7c4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (149,'','2024-11-19 16:35:13.389120','2024-12-18 15:32:44.517592','Nettomiete 02.2024 für 001/9901/9906',2024,2,1,'2024-02-01',1759.00,'1102',3,NULL,'3001','5522d360c963473c8313d8f976d559af','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (150,'','2024-11-19 16:35:13.470733','2024-12-18 15:32:44.519263','Nebenkosten 02.2024 für 001/9901/9906',2024,2,1,'2024-02-01',208.00,'1102',3,NULL,'2301','93152a6dd20c46369c71daca5c375bbc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (151,'','2024-11-19 16:35:13.530139','2024-12-18 15:32:44.521045','Strompauschale 02.2024 für 001/9901/9906',2024,2,1,'2024-02-01',5.00,'1102',3,NULL,'2302','1c239485013f40e6b314153742366be7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (152,'','2024-11-19 16:35:13.599130','2024-12-18 15:32:44.512029','Nettomiete 01.2024 für 001/9901/9906',2024,1,1,'2024-01-01',1759.00,'1102',3,NULL,'3001','6818b78e555641a180274727ce10eb59','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (153,'','2024-11-19 16:35:13.656346','2024-12-18 15:32:44.514079','Nebenkosten 01.2024 für 001/9901/9906',2024,1,1,'2024-01-01',208.00,'1102',3,NULL,'2301','41ae9a1a8f3740ceb4ebba7b2867853a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (154,'','2024-11-19 16:35:13.718415','2024-12-18 15:32:44.515825','Strompauschale 01.2024 für 001/9901/9906',2024,1,1,'2024-01-01',5.00,'1102',3,NULL,'2302','5c4430422177460cbc2a12278ffdb59a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (155,'','2024-11-19 16:35:13.786967','2024-12-18 15:32:44.506462','Nettomiete 12.2023 für 001/9901/9906',2023,12,1,'2023-12-01',1759.00,'1102',3,NULL,'3001','1f52ca7373304f089e489e99887082a4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (156,'','2024-11-19 16:35:13.850757','2024-12-18 15:32:44.508324','Nebenkosten 12.2023 für 001/9901/9906',2023,12,1,'2023-12-01',208.00,'1102',3,NULL,'2301','adaaf0780ba64a0eb996b4f89a61ab2c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (157,'','2024-11-19 16:35:13.906529','2024-12-18 15:32:44.510084','Strompauschale 12.2023 für 001/9901/9906',2023,12,1,'2023-12-01',5.00,'1102',3,NULL,'2302','c7a7c553d46e4df69f3af2f039c4fd57','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (158,'','2024-11-19 16:35:13.975151','2024-12-18 15:32:44.500508','Nettomiete 11.2023 für 001/9901/9906',2023,11,1,'2023-11-01',1759.00,'1102',3,NULL,'3001','0eb5533dbc944f5ca782e90165b6324c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (159,'','2024-11-19 16:35:14.039667','2024-12-18 15:32:44.502481','Nebenkosten 11.2023 für 001/9901/9906',2023,11,1,'2023-11-01',208.00,'1102',3,NULL,'2301','1f8fe202f6a845569fcc98802f6da188','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (160,'','2024-11-19 16:35:14.098785','2024-12-18 15:32:44.504625','Strompauschale 11.2023 für 001/9901/9906',2023,11,1,'2023-11-01',5.00,'1102',3,NULL,'2302','57de9123978f42fd846539975f517752','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (161,'','2024-11-19 16:35:14.168327','2024-12-18 15:32:44.495015','Nettomiete 10.2023 für 001/9901/9906',2023,10,1,'2023-10-01',1759.00,'1102',3,NULL,'3001','fd3fc630321e4e168edec088a3986ae4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (162,'','2024-11-19 16:35:14.227827','2024-12-18 15:32:44.496893','Nebenkosten 10.2023 für 001/9901/9906',2023,10,1,'2023-10-01',208.00,'1102',3,NULL,'2301','ae55e46534474a81b32daee174d51c34','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (163,'','2024-11-19 16:35:14.292090','2024-12-18 15:32:44.498742','Strompauschale 10.2023 für 001/9901/9906',2023,10,1,'2023-10-01',5.00,'1102',3,NULL,'2302','9d37a18da8fc40768ab6ea1d92000bbb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (164,'','2024-11-19 16:35:14.366598','2024-12-18 15:32:44.489777','Nettomiete 09.2023 für 001/9901/9906',2023,9,1,'2023-09-01',1759.00,'1102',3,NULL,'3001','e72223c9b35448d49c652115978dcfee','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (165,'','2024-11-19 16:35:14.429111','2024-12-18 15:32:44.491603','Nebenkosten 09.2023 für 001/9901/9906',2023,9,1,'2023-09-01',208.00,'1102',3,NULL,'2301','3dd3420d92f04fe9b6eeeb52eef9454f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (166,'','2024-11-19 16:35:14.488646','2024-12-18 15:32:44.493343','Strompauschale 09.2023 für 001/9901/9906',2023,9,1,'2023-09-01',5.00,'1102',3,NULL,'2302','f205333b6f9c45c4967cca30390cff4a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (167,'','2024-11-19 16:35:14.649586','2024-12-18 15:32:44.481722','Nettomiete 08.2023 für 001/9901/9906',2023,8,1,'2023-08-01',1759.00,'1102',3,NULL,'3001','126d49f704a64cf1bdaf32a9142ffdd2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (168,'','2024-11-19 16:35:14.728374','2024-12-18 15:32:44.486021','Nebenkosten 08.2023 für 001/9901/9906',2023,8,1,'2023-08-01',208.00,'1102',3,NULL,'2301','7f74877ccfe748aa84afe029c7379b28','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (169,'','2024-11-19 16:35:14.794251','2024-12-18 15:32:44.488017','Strompauschale 08.2023 für 001/9901/9906',2023,8,1,'2023-08-01',5.00,'1102',3,NULL,'2302','c2e255a2179d4d8ab2beb54a455758b2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (170,'','2024-11-19 16:35:14.874858','2024-12-18 15:32:44.476351','Nettomiete 07.2023 für 001/9901/9906',2023,7,1,'2023-07-01',1759.00,'1102',3,NULL,'3001','4598540cc24046259f13be2255cd0c64','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (171,'','2024-11-19 16:35:14.938487','2024-12-18 15:32:44.478166','Nebenkosten 07.2023 für 001/9901/9906',2023,7,1,'2023-07-01',208.00,'1102',3,NULL,'2301','66eef93c649f4b649a729473bcc6ffed','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (172,'','2024-11-19 16:35:15.007580','2024-12-18 15:32:44.479906','Strompauschale 07.2023 für 001/9901/9906',2023,7,1,'2023-07-01',5.00,'1102',3,NULL,'2302','6dadd72f95b64503add1f9129ab6db11','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (173,'','2024-11-19 16:35:15.083218','2024-12-18 15:32:44.470763','Nettomiete 06.2023 für 001/9901/9906',2023,6,1,'2023-06-01',1759.00,'1102',3,NULL,'3001','fae1e35b31c046158c7120d389e5c668','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (174,'','2024-11-19 16:35:15.140057','2024-12-18 15:32:44.472775','Nebenkosten 06.2023 für 001/9901/9906',2023,6,1,'2023-06-01',208.00,'1102',3,NULL,'2301','d7e51761d53d49ccb9ecbf1efdbc46a0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (175,'','2024-11-19 16:35:15.203190','2024-12-18 15:32:44.474591','Strompauschale 06.2023 für 001/9901/9906',2023,6,1,'2023-06-01',5.00,'1102',3,NULL,'2302','47609c4a4270406da2fc046389e9d0bd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (176,'','2024-11-19 16:35:15.275179','2024-12-18 15:32:44.465413','Nettomiete 05.2023 für 001/9901/9906',2023,5,1,'2023-05-01',1759.00,'1102',3,NULL,'3001','41d1647ab9454b02b660c9d065d9cdc1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (177,'','2024-11-19 16:35:15.540513','2024-12-18 15:32:44.467211','Nebenkosten 05.2023 für 001/9901/9906',2023,5,1,'2023-05-01',208.00,'1102',3,NULL,'2301','07a6142d4c404af5884538362935fd8c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (178,'','2024-11-19 16:35:15.601462','2024-12-18 15:32:44.468982','Strompauschale 05.2023 für 001/9901/9906',2023,5,1,'2023-05-01',5.00,'1102',3,NULL,'2302','bd81379278d54db3a5f46e78935787e4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (179,'','2024-11-19 16:35:15.674026','2024-12-18 15:32:44.460036','Nettomiete 04.2023 für 001/9901/9906',2023,4,1,'2023-04-01',1759.00,'1102',3,NULL,'3001','55c74c7097524561bb1f3b5c019acfa0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (180,'','2024-11-19 16:35:15.749466','2024-12-18 15:32:44.461729','Nebenkosten 04.2023 für 001/9901/9906',2023,4,1,'2023-04-01',208.00,'1102',3,NULL,'2301','82a2eb1bafd146faa766e48fe1bdea69','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (181,'','2024-11-19 16:35:15.881996','2024-12-18 15:32:44.463459','Strompauschale 04.2023 für 001/9901/9906',2023,4,1,'2023-04-01',5.00,'1102',3,NULL,'2302','aba83e742b914b83ac6541bc1c4dfd37','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (182,'','2024-11-19 16:35:15.975277','2024-12-18 15:32:44.454450','Nettomiete 03.2023 für 001/9901/9906',2023,3,1,'2023-03-01',1759.00,'1102',3,NULL,'3001','a0b99622382041faa9b7213a06b29a39','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (183,'','2024-11-19 16:35:16.038735','2024-12-18 15:32:44.456341','Nebenkosten 03.2023 für 001/9901/9906',2023,3,1,'2023-03-01',208.00,'1102',3,NULL,'2301','c3742e639e0e4cd1afe6100f07632834','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (184,'','2024-11-19 16:35:16.100376','2024-12-18 15:32:44.458273','Strompauschale 03.2023 für 001/9901/9906',2023,3,1,'2023-03-01',5.00,'1102',3,NULL,'2302','5c98ca1173a24e28b4658806a9c37ffa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (185,'','2024-11-19 16:35:16.175702','2024-12-18 15:32:44.449122','Nettomiete 02.2023 für 001/9901/9906',2023,2,1,'2023-02-01',1759.00,'1102',3,NULL,'3001','c296a19997744bdfb44a2c953ae44fd3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (186,'','2024-11-19 16:35:16.233857','2024-12-18 15:32:44.450816','Nebenkosten 02.2023 für 001/9901/9906',2023,2,1,'2023-02-01',208.00,'1102',3,NULL,'2301','964a24ffd171473e9364a8e3ecb37b39','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (187,'','2024-11-19 16:35:16.293248','2024-12-18 15:32:44.452619','Strompauschale 02.2023 für 001/9901/9906',2023,2,1,'2023-02-01',5.00,'1102',3,NULL,'2302','7d012dc393da4cfba25a093cba11d7ea','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (188,'','2024-11-19 16:35:16.369655','2024-12-18 15:32:44.443464','Nettomiete 01.2023 für 001/9901/9906',2023,1,1,'2023-01-01',1759.00,'1102',3,NULL,'3001','e7182330475d49ca849dc12abd1c48ea','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (189,'','2024-11-19 16:35:16.472446','2024-12-18 15:32:44.445587','Nebenkosten 01.2023 für 001/9901/9906',2023,1,1,'2023-01-01',208.00,'1102',3,NULL,'2301','c5f2ca1473194ed89191b39e00621a72','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (190,'','2024-11-19 16:35:16.578602','2024-12-18 15:32:44.447317','Strompauschale 01.2023 für 001/9901/9906',2023,1,1,'2023-01-01',5.00,'1102',3,NULL,'2302','5ed1d2b7b4e84abd9eede9f8187037f4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (191,'','2024-11-19 16:35:16.711728','2024-12-18 15:32:44.438026','Nettomiete 12.2022 für 001/9901/9906',2022,12,1,'2022-12-01',1759.00,'1102',3,NULL,'3001','830bfe3d18fe41649f2aa7094a879571','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (192,'','2024-11-19 16:35:16.821032','2024-12-18 15:32:44.439921','Nebenkosten 12.2022 für 001/9901/9906',2022,12,1,'2022-12-01',208.00,'1102',3,NULL,'2301','6d856645d6df4acb9eacb60491bfcb2e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (193,'','2024-11-19 16:35:16.953340','2024-12-18 15:32:44.441677','Strompauschale 12.2022 für 001/9901/9906',2022,12,1,'2022-12-01',5.00,'1102',3,NULL,'2302','205a9d4ffe074574804485118aaea3e7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (194,'','2024-11-19 16:35:17.088469','2024-12-18 15:32:44.432612','Nettomiete 11.2022 für 001/9901/9906',2022,11,1,'2022-11-01',1759.00,'1102',3,NULL,'3001','c58440ce388346b89e54fc68995e53e0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (195,'','2024-11-19 16:35:17.162392','2024-12-18 15:32:44.434357','Nebenkosten 11.2022 für 001/9901/9906',2022,11,1,'2022-11-01',208.00,'1102',3,NULL,'2301','9f5be63f4490402c919c7365de7b94a3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (196,'','2024-11-19 16:35:17.292509','2024-12-18 15:32:44.436110','Strompauschale 11.2022 für 001/9901/9906',2022,11,1,'2022-11-01',5.00,'1102',3,NULL,'2302','7874ef49cf6547abac305f971385cbae','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (197,'','2024-11-19 16:35:17.376087','2024-12-18 15:32:44.427275','Nettomiete 10.2022 für 001/9901/9906',2022,10,1,'2022-10-01',1759.00,'1102',3,NULL,'3001','c5e7b878eddd46b3a0cc077dbff901d2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (198,'','2024-11-19 16:35:17.483639','2024-12-18 15:32:44.429086','Nebenkosten 10.2022 für 001/9901/9906',2022,10,1,'2022-10-01',208.00,'1102',3,NULL,'2301','37e422f4d8274f5682297e2a6b2ce78d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (199,'','2024-11-19 16:35:17.605075','2024-12-18 15:32:44.430856','Strompauschale 10.2022 für 001/9901/9906',2022,10,1,'2022-10-01',5.00,'1102',3,NULL,'2302','0b24dffb3b094dd1aa4cd770ecaa999e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (200,'','2024-11-19 16:35:17.711966','2024-12-18 15:32:44.420236','Nettomiete 09.2022 für 001/9901/9906',2022,9,1,'2022-09-01',1759.00,'1102',3,NULL,'3001','0d613ba4e66a48abb76131b4e0a4c811','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (201,'','2024-11-19 16:35:17.851162','2024-12-18 15:32:44.422054','Nebenkosten 09.2022 für 001/9901/9906',2022,9,1,'2022-09-01',208.00,'1102',3,NULL,'2301','ccedf761885d41be80b90d60332564b5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (202,'','2024-11-19 16:35:17.983906','2024-12-18 15:32:44.425295','Strompauschale 09.2022 für 001/9901/9906',2022,9,1,'2022-09-01',5.00,'1102',3,NULL,'2302','1ffd1c577c324bd5a0d528d0c9aa6ce5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (203,'','2024-11-19 16:35:18.119284','2024-12-18 15:32:44.414886','Nettomiete 08.2022 für 001/9901/9906',2022,8,1,'2022-08-01',1759.00,'1102',3,NULL,'3001','2880f8263d8140afb13e627eba00eb1e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (204,'','2024-11-19 16:35:18.226368','2024-12-18 15:32:44.416669','Nebenkosten 08.2022 für 001/9901/9906',2022,8,1,'2022-08-01',208.00,'1102',3,NULL,'2301','6c0462c4a84a46dca064717e3c409438','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (205,'','2024-11-19 16:35:18.347598','2024-12-18 15:32:44.418401','Strompauschale 08.2022 für 001/9901/9906',2022,8,1,'2022-08-01',5.00,'1102',3,NULL,'2302','50850ed6abd147ccb4d12d2ac4c18d77','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (206,'','2024-11-19 16:35:18.477200','2024-12-18 15:30:01.489858','Nettomiete 10.2024 für 101/9903',2024,10,1,'2024-10-01',6690.00,'1102',4,NULL,'3000','814137438d57488295edc20dbeb0bdb7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (207,'','2024-11-19 16:35:18.539410','2024-12-18 15:30:01.492018','Nebenkosten 10.2024 für 101/9903',2024,10,1,'2024-10-01',635.00,'1102',4,NULL,'2301','f70606478daa4739b0008b80dd18796a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (208,'','2024-11-19 16:35:18.664610','2024-12-18 15:30:01.486401','Nettomiete 09.2024 für 101/9903',2024,9,1,'2024-09-01',6690.00,'1102',4,NULL,'3000','682259d8fc644e0ea98f253df141698d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (209,'','2024-11-19 16:35:18.727431','2024-12-18 15:30:01.488209','Nebenkosten 09.2024 für 101/9903',2024,9,1,'2024-09-01',635.00,'1102',4,NULL,'2301','b2fca3411c9c4ad6ba676186a37cfaaa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (210,'','2024-11-19 16:35:18.812488','2024-12-18 15:30:01.482921','Nettomiete 08.2024 für 101/9903',2024,8,1,'2024-08-01',6690.00,'1102',4,NULL,'3000','184376a0b6544653840a303194f857e6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (211,'','2024-11-19 16:35:18.893658','2024-12-18 15:30:01.484652','Nebenkosten 08.2024 für 101/9903',2024,8,1,'2024-08-01',635.00,'1102',4,NULL,'2301','08ff8c34bf504a87aff08ad526711a26','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (212,'','2024-11-19 16:35:18.967964','2024-12-18 15:30:01.478696','Nettomiete 07.2024 für 101/9903',2024,7,1,'2024-07-01',6690.00,'1102',4,NULL,'3000','e48d8891d5ad4cd0a5eb4a673397186d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (213,'','2024-11-19 16:35:19.048557','2024-12-18 15:30:01.480839','Nebenkosten 07.2024 für 101/9903',2024,7,1,'2024-07-01',635.00,'1102',4,NULL,'2301','b732e308736845e8a4e047fa39195ea7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (214,'','2024-11-19 16:35:19.133762','2024-12-18 15:30:01.475135','Nettomiete 06.2024 für 101/9903',2024,6,1,'2024-06-01',6690.00,'1102',4,NULL,'3000','9d20af82e4794614960c7b780de839d3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (215,'','2024-11-19 16:35:19.214493','2024-12-18 15:30:01.476987','Nebenkosten 06.2024 für 101/9903',2024,6,1,'2024-06-01',635.00,'1102',4,NULL,'2301','e2a134d9e9ad4b97a97ab9b06ea1781a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (216,'','2024-11-19 16:35:19.373467','2024-12-18 15:30:01.471343','Nettomiete 05.2024 für 101/9903',2024,5,1,'2024-05-01',6690.00,'1102',4,NULL,'3000','a55426ef019f45dcbccd9d5b95623970','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (217,'','2024-11-19 16:35:19.472335','2024-12-18 15:30:01.473337','Nebenkosten 05.2024 für 101/9903',2024,5,1,'2024-05-01',635.00,'1102',4,NULL,'2301','bf45b33124074aa592832d2080ce4f25','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (218,'','2024-11-19 16:35:19.639338','2024-12-18 15:30:01.467730','Nettomiete 04.2024 für 101/9903',2024,4,1,'2024-04-01',6690.00,'1102',4,NULL,'3000','4648813d63714e5caea658ed2a9bea39','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (219,'','2024-11-19 16:35:19.737457','2024-12-18 15:30:01.469550','Nebenkosten 04.2024 für 101/9903',2024,4,1,'2024-04-01',635.00,'1102',4,NULL,'2301','44e9487ebd0a4500bbd4e85575f7045d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (220,'','2024-11-19 16:35:19.854529','2024-12-18 15:30:01.464173','Nettomiete 03.2024 für 101/9903',2024,3,1,'2024-03-01',6690.00,'1102',4,NULL,'3000','c0eb1ae1dbee4133b0ebb8855df78f8f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (221,'','2024-11-19 16:35:19.968019','2024-12-18 15:30:01.465897','Nebenkosten 03.2024 für 101/9903',2024,3,1,'2024-03-01',635.00,'1102',4,NULL,'2301','65a3222fcb424267ba6c56b7514637da','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (222,'','2024-11-19 16:35:20.086795','2024-12-18 15:30:01.460787','Nettomiete 02.2024 für 101/9903',2024,2,1,'2024-02-01',6690.00,'1102',4,NULL,'3000','23f4dd09f5d84d109c29fa14c88beb81','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (223,'','2024-11-19 16:35:20.156002','2024-12-18 15:30:01.462478','Nebenkosten 02.2024 für 101/9903',2024,2,1,'2024-02-01',635.00,'1102',4,NULL,'2301','38cecf802bfb44baaf0a5adfd58a3ffb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (224,'','2024-11-19 16:35:20.274359','2024-12-18 15:30:01.457198','Nettomiete 01.2024 für 101/9903',2024,1,1,'2024-01-01',6690.00,'1102',4,NULL,'3000','0e9e4b1076534a33affcf7322f7dcf0f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (225,'','2024-11-19 16:35:20.388520','2024-12-18 15:30:01.458930','Nebenkosten 01.2024 für 101/9903',2024,1,1,'2024-01-01',635.00,'1102',4,NULL,'2301','e163d1fae700475ea5a19a165bbb4ecd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (226,'','2024-11-19 16:35:20.474055','2024-12-18 15:30:01.453348','Nettomiete 12.2023 für 101/9903',2023,12,1,'2023-12-01',6690.00,'1102',4,NULL,'3000','b1b2f4f4155e4b08b627a4d6936a00e2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (227,'','2024-11-19 16:35:20.554812','2024-12-18 15:30:01.455106','Nebenkosten 12.2023 für 101/9903',2023,12,1,'2023-12-01',635.00,'1102',4,NULL,'2301','57ba847c63b6440ab4c2d7cd4dbb80c3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (228,'','2024-11-19 16:35:20.673421','2024-12-18 15:30:01.449628','Nettomiete 11.2023 für 101/9903',2023,11,1,'2023-11-01',6690.00,'1102',4,NULL,'3000','f85a43bc412f415794c1551200419a5b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (229,'','2024-11-19 16:35:20.788899','2024-12-18 15:30:01.451471','Nebenkosten 11.2023 für 101/9903',2023,11,1,'2023-11-01',635.00,'1102',4,NULL,'2301','21a38d4a1f39448b86555ced74c70582','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (230,'','2024-11-19 16:35:20.909451','2024-12-18 15:30:01.445954','Nettomiete 10.2023 für 101/9903',2023,10,1,'2023-10-01',6690.00,'1102',4,NULL,'3000','48a0007a0ec54d80a4dfa1f20afdd89b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (231,'','2024-11-19 16:35:21.032648','2024-12-18 15:30:01.447885','Nebenkosten 10.2023 für 101/9903',2023,10,1,'2023-10-01',635.00,'1102',4,NULL,'2301','4d43abd656074c7d8c6201942c8b1cf2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (232,'','2024-11-19 16:35:21.151823','2024-12-18 15:30:01.441894','Nettomiete 09.2023 für 101/9903',2023,9,1,'2023-09-01',6690.00,'1102',4,NULL,'3000','f7f01b7e741e4a11ac25d7cc5156af38','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (233,'','2024-11-19 16:35:21.253753','2024-12-18 15:30:01.444065','Nebenkosten 09.2023 für 101/9903',2023,9,1,'2023-09-01',635.00,'1102',4,NULL,'2301','e5c3b0a9fd85418287894d4e200fac8c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (234,'','2024-11-19 16:35:21.371356','2024-12-18 15:30:01.437997','Nettomiete 08.2023 für 101/9903',2023,8,1,'2023-08-01',6690.00,'1102',4,NULL,'3000','f61c7989fc024f6c82c16ccffd5dabfb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (235,'','2024-11-19 16:35:21.462400','2024-12-18 15:30:01.439848','Nebenkosten 08.2023 für 101/9903',2023,8,1,'2023-08-01',635.00,'1102',4,NULL,'2301','2913de5874554eacb05e21c4f13d90d7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (236,'','2024-11-19 16:35:21.547135','2024-12-18 15:30:01.434189','Nettomiete 07.2023 für 101/9903',2023,7,1,'2023-07-01',6690.00,'1102',4,NULL,'3000','0c55478d5bbe42489cb7bf305913b663','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (237,'','2024-11-19 16:35:21.627844','2024-12-18 15:30:01.436061','Nebenkosten 07.2023 für 101/9903',2023,7,1,'2023-07-01',635.00,'1102',4,NULL,'2301','5f1db950518c47e5a719f9a7801ac6d2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (238,'','2024-11-19 16:35:21.764247','2024-12-18 15:30:01.430179','Nettomiete 06.2023 für 101/9903',2023,6,1,'2023-06-01',6690.00,'1102',4,NULL,'3000','b29574f420b540d2a4bee3c3ad1528dd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (239,'','2024-11-19 16:35:21.827292','2024-12-18 15:30:01.432109','Nebenkosten 06.2023 für 101/9903',2023,6,1,'2023-06-01',635.00,'1102',4,NULL,'2301','38497cb3b15b4da0904a390b4338eed5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (240,'','2024-11-19 16:35:21.912577','2024-12-18 15:30:01.426261','Nettomiete 05.2023 für 101/9903',2023,5,1,'2023-05-01',6690.00,'1102',4,NULL,'3000','80abaa44312e4b70949880efa6aae446','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (241,'','2024-11-19 16:35:21.993505','2024-12-18 15:30:01.428082','Nebenkosten 05.2023 für 101/9903',2023,5,1,'2023-05-01',635.00,'1102',4,NULL,'2301','d7c80fa57b204b31af33567ced540b4f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (242,'','2024-11-19 16:35:22.078347','2024-12-18 15:30:01.421657','Nettomiete 04.2023 für 101/9903',2023,4,1,'2023-04-01',6690.00,'1102',4,NULL,'3000','a9d761eada734f17a18158fbc7e7b8bb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (243,'','2024-11-19 16:35:22.181653','2024-12-18 15:30:01.424190','Nebenkosten 04.2023 für 101/9903',2023,4,1,'2023-04-01',635.00,'1102',4,NULL,'2301','12b08dbc14ea463abd516e00baf372cc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (244,'','2024-11-19 16:35:22.266780','2024-12-18 15:30:01.417902','Nettomiete 03.2023 für 101/9903',2023,3,1,'2023-03-01',6690.00,'1102',4,NULL,'3000','036f415418714607932758713628831a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (245,'','2024-11-19 16:35:22.382092','2024-12-18 15:30:01.419958','Nebenkosten 03.2023 für 101/9903',2023,3,1,'2023-03-01',635.00,'1102',4,NULL,'2301','e35072fa8a844de79040b1e0a3af32f0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (246,'','2024-11-19 16:35:22.480031','2024-12-18 15:30:01.413936','Nettomiete 02.2023 für 101/9903',2023,2,1,'2023-02-01',6690.00,'1102',4,NULL,'3000','24001543ee9c4ecf80c694783d1f72b1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (247,'','2024-11-19 16:35:22.592537','2024-12-18 15:30:01.415931','Nebenkosten 02.2023 für 101/9903',2023,2,1,'2023-02-01',635.00,'1102',4,NULL,'2301','4589afba66ba44ecaffb27fade7a3253','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (248,'','2024-11-19 16:35:22.711911','2024-12-18 15:30:01.409904','Nettomiete 01.2023 für 101/9903',2023,1,1,'2023-01-01',6690.00,'1102',4,NULL,'3000','2892e44bd99c4048ba006bdc8c0e2492','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (249,'','2024-11-19 16:35:22.871040','2024-12-18 15:30:01.411983','Nebenkosten 01.2023 für 101/9903',2023,1,1,'2023-01-01',635.00,'1102',4,NULL,'2301','6c5ffffaa8d14e1a959530f40388f61d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (250,'','2024-11-19 16:35:22.943189','2024-12-18 15:30:01.406195','Nettomiete 12.2022 für 101/9903',2022,12,1,'2022-12-01',6690.00,'1102',4,NULL,'3000','0858d855157a4aa08a5299961ad3d7f3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (251,'','2024-11-19 16:35:23.023382','2024-12-18 15:30:01.408026','Nebenkosten 12.2022 für 101/9903',2022,12,1,'2022-12-01',635.00,'1102',4,NULL,'2301','7ff31cead59d4202b859fe0fae8e9c09','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (252,'','2024-11-19 16:35:23.108501','2024-12-18 15:30:01.402498','Nettomiete 11.2022 für 101/9903',2022,11,1,'2022-11-01',6690.00,'1102',4,NULL,'3000','7811433960f4410cb13b701bb6274ac2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (253,'','2024-11-19 16:35:23.189505','2024-12-18 15:30:01.404293','Nebenkosten 11.2022 für 101/9903',2022,11,1,'2022-11-01',635.00,'1102',4,NULL,'2301','3ca41b5b80ca4bc29919902083a6e3cb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (254,'','2024-11-19 16:35:23.390860','2024-12-18 15:30:01.398665','Nettomiete 10.2022 für 101/9903',2022,10,1,'2022-10-01',6690.00,'1102',4,NULL,'3000','29b84ff733b546fa888e4c80a8646e91','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (255,'','2024-11-19 16:35:23.455590','2024-12-18 15:30:01.400699','Nebenkosten 10.2022 für 101/9903',2022,10,1,'2022-10-01',635.00,'1102',4,NULL,'2301','83a4f2bb89c7460bb6c91d7fd21353e3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (256,'','2024-11-19 16:35:23.540533','2024-12-18 15:30:01.394905','Nettomiete 09.2022 für 101/9903',2022,9,1,'2022-09-01',6690.00,'1102',4,NULL,'3000','7ac7b6d5b9dc49a7bd46c7124e0f5500','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (257,'','2024-11-19 16:35:23.621017','2024-12-18 15:30:01.396861','Nebenkosten 09.2022 für 101/9903',2022,9,1,'2022-09-01',635.00,'1102',4,NULL,'2301','17b6aa68d03c462ca58be20805cfc96d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (258,'','2024-11-19 16:35:23.706245','2024-12-18 15:30:01.391147','Nettomiete 08.2022 für 101/9903',2022,8,1,'2022-08-01',6690.00,'1102',4,NULL,'3000','cb444963ef244401b74dfe4bddfad2ea','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (259,'','2024-11-19 16:35:23.787069','2024-12-18 15:30:01.393025','Nebenkosten 08.2022 für 101/9903',2022,8,1,'2022-08-01',635.00,'1102',4,NULL,'2301','08deb729650c4fe48e3efd37372ab595','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (260,'','2024-11-19 16:35:23.883902','2025-04-23 08:44:57.141481','Nettomiete 10.2024 für 201/9904',2024,10,1,'2024-10-01',768.00,'1102',5,NULL,'3000','ccc007637e4a4326886ac74ac62119f7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (261,'','2024-11-19 16:35:23.995426','2025-04-23 08:44:57.143598','Nebenkosten 10.2024 für 201/9904',2024,10,1,'2024-10-01',82.00,'1102',5,NULL,'2301','ef9ed4d45f154f689bd57f94c7c8f438','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (262,'','2024-11-19 16:35:24.137745','2025-04-23 08:44:57.137303','Nettomiete 09.2024 für 201/9904',2024,9,1,'2024-09-01',768.00,'1102',5,NULL,'3000','35d8ead5e5d947bb8d0f790d49784b3a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (263,'','2024-11-19 16:35:24.250346','2025-04-23 08:44:57.139257','Nebenkosten 09.2024 für 201/9904',2024,9,1,'2024-09-01',82.00,'1102',5,NULL,'2301','3e02a942ad264271b366f2ed0a372c11','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (264,'','2024-11-19 16:35:24.380140','2025-04-23 08:44:57.133255','Nettomiete 08.2024 für 201/9904',2024,8,1,'2024-08-01',768.00,'1102',5,NULL,'3000','26eecd62d0f04b13a4e4d587cdea3825','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (265,'','2024-11-19 16:35:24.492958','2025-04-23 08:44:57.135275','Nebenkosten 08.2024 für 201/9904',2024,8,1,'2024-08-01',82.00,'1102',5,NULL,'2301','bf2a1756404f4d709182718742d9bc38','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (266,'','2024-11-19 16:35:24.587498','2025-04-23 08:44:57.129201','Nettomiete 07.2024 für 201/9904',2024,7,1,'2024-07-01',768.00,'1102',5,NULL,'3000','0531a1371a69403a9fcf0631616e3920','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (267,'','2024-11-19 16:35:24.702542','2025-04-23 08:44:57.131296','Nebenkosten 07.2024 für 201/9904',2024,7,1,'2024-07-01',82.00,'1102',5,NULL,'2301','4e65369949594972b61f1475b49c7c2e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (268,'','2024-11-19 16:35:24.830504','2025-04-23 08:44:57.125216','Nettomiete 06.2024 für 201/9904',2024,6,1,'2024-06-01',768.00,'1102',5,NULL,'3000','effe213d48114b4b94d532023dacc0f5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (269,'','2024-11-19 16:35:24.935113','2025-04-23 08:44:57.127211','Nebenkosten 06.2024 für 201/9904',2024,6,1,'2024-06-01',82.00,'1102',5,NULL,'2301','b27a6502af1e4131a8aac298af4b7b6d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (270,'','2024-11-19 16:35:25.031070','2025-04-23 08:44:57.121137','Nettomiete 05.2024 für 201/9904',2024,5,1,'2024-05-01',768.00,'1102',5,NULL,'3000','2d8b04420ce741d8a7d104e31221cac8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (271,'','2024-11-19 16:35:25.123432','2025-04-23 08:44:57.123184','Nebenkosten 05.2024 für 201/9904',2024,5,1,'2024-05-01',82.00,'1102',5,NULL,'2301','67069f323d404e97b8c9af5b24af569e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (272,'','2024-11-19 16:35:25.218501','2025-04-23 08:44:57.116789','Nettomiete 04.2024 für 201/9904',2024,4,1,'2024-04-01',768.00,'1102',5,NULL,'3000','9894513a13494e0f82584221accc47c0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (273,'','2024-11-19 16:35:25.300414','2025-04-23 08:44:57.119062','Nebenkosten 04.2024 für 201/9904',2024,4,1,'2024-04-01',82.00,'1102',5,NULL,'2301','a070ea7810144074a266e3e5fdf88ca6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (274,'','2024-11-19 16:35:25.395496','2025-04-23 08:44:57.112814','Nettomiete 03.2024 für 201/9904',2024,3,1,'2024-03-01',768.00,'1102',5,NULL,'3000','c32959a9e16e4212ab2801ef8603d1f0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (275,'','2024-11-19 16:35:25.512764','2025-04-23 08:44:57.114807','Nebenkosten 03.2024 für 201/9904',2024,3,1,'2024-03-01',82.00,'1102',5,NULL,'2301','f41354242b024786a77194e2e776e35f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (276,'','2024-11-19 16:35:25.642422','2025-04-23 08:44:57.107669','Nettomiete 02.2024 für 201/9904',2024,2,1,'2024-02-01',768.00,'1102',5,NULL,'3000','08c25d5d492b474db7fbc290c0d8a422','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (277,'','2024-11-19 16:35:25.756044','2025-04-23 08:44:57.110686','Nebenkosten 02.2024 für 201/9904',2024,2,1,'2024-02-01',82.00,'1102',5,NULL,'2301','1a493cc92c3f40ca912e38ea7ba06c34','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (278,'','2024-11-19 16:35:25.885833','2025-04-23 08:44:57.096304','Nettomiete 01.2024 für 201/9904',2024,1,1,'2024-01-01',768.00,'1102',5,NULL,'3000','dbdc976f3f3e4190ae7b9ef0c2a9c2ee','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (279,'','2024-11-19 16:35:26.000342','2025-04-23 08:44:57.103581','Nebenkosten 01.2024 für 201/9904',2024,1,1,'2024-01-01',82.00,'1102',5,NULL,'2301','c9fcbc8a3806484e90278d7c1f984c84','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (280,'','2024-11-19 16:35:26.127413','2025-04-23 08:44:57.091644','Nettomiete 12.2023 für 201/9904',2023,12,1,'2023-12-01',768.00,'1102',5,NULL,'3000','5be991f6fbad43e68ad2070689d93871','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (281,'','2024-11-19 16:35:26.441416','2025-04-23 08:44:57.094043','Nebenkosten 12.2023 für 201/9904',2023,12,1,'2023-12-01',82.00,'1102',5,NULL,'2301','4ea5438d3f4b43debfd2c0123f76e48a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (282,'','2024-11-19 16:35:26.547697','2025-04-23 08:44:57.086684','Nettomiete 11.2023 für 201/9904',2023,11,1,'2023-11-01',768.00,'1102',5,NULL,'3000','d710cb8954f94d77b26389e6c60ee9f9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (283,'','2024-11-19 16:35:26.629458','2025-04-23 08:44:57.089348','Nebenkosten 11.2023 für 201/9904',2023,11,1,'2023-11-01',82.00,'1102',5,NULL,'2301','40674b6547894b8689a2eb22db4c98e2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (284,'','2024-11-19 16:35:26.724731','2025-04-23 08:44:57.081721','Nettomiete 10.2023 für 201/9904',2023,10,1,'2023-10-01',768.00,'1102',5,NULL,'3000','a78d4e8e62214702aafad78ab33d88a7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (285,'','2024-11-19 16:35:26.806334','2025-04-23 08:44:57.083797','Nebenkosten 10.2023 für 201/9904',2023,10,1,'2023-10-01',82.00,'1102',5,NULL,'2301','15726188ba904181a2c27e869530d869','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (286,'','2024-11-19 16:35:26.901304','2025-04-23 08:44:57.077638','Nettomiete 09.2023 für 201/9904',2023,9,1,'2023-09-01',768.00,'1102',5,NULL,'3000','14aa0b1764e44e8392b451205350fe1e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (287,'','2024-11-19 16:35:26.985018','2025-04-23 08:44:57.079664','Nebenkosten 09.2023 für 201/9904',2023,9,1,'2023-09-01',82.00,'1102',5,NULL,'2301','00fdfb85162846f0a2938c98b5ceb5a1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (288,'','2024-11-19 16:35:27.115496','2025-04-23 08:44:57.073227','Nettomiete 08.2023 für 201/9904',2023,8,1,'2023-08-01',768.00,'1102',5,NULL,'3000','5dbfb9332e314833bacd65b7144b4a7c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (289,'','2024-11-19 16:35:27.251178','2025-04-23 08:44:57.075502','Nebenkosten 08.2023 für 201/9904',2023,8,1,'2023-08-01',82.00,'1102',5,NULL,'2301','bcdce478ca8a41b39ff0ba77f231dd50','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (290,'','2024-11-19 16:35:27.380377','2025-04-23 08:44:57.069177','Nettomiete 07.2023 für 201/9904',2023,7,1,'2023-07-01',768.00,'1102',5,NULL,'3000','06a19d1f85f246b2bc4f72a69a766943','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (291,'','2024-11-19 16:35:27.495425','2025-04-23 08:44:57.071175','Nebenkosten 07.2023 für 201/9904',2023,7,1,'2023-07-01',82.00,'1102',5,NULL,'2301','e540697f296a4b62852470734aeb3c40','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (292,'','2024-11-19 16:35:27.600144','2025-04-23 08:44:57.065141','Nettomiete 06.2023 für 201/9904',2023,6,1,'2023-06-01',768.00,'1102',5,NULL,'3000','212e778aa1fc43cabc7ef1a96db45b15','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (293,'','2024-11-19 16:35:27.681558','2025-04-23 08:44:57.067183','Nebenkosten 06.2023 für 201/9904',2023,6,1,'2023-06-01',82.00,'1102',5,NULL,'2301','7466a3c9515340b6b232636dcf5e7f71','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (294,'','2024-11-19 16:35:27.820952','2025-04-23 08:44:57.059300','Nettomiete 05.2023 für 201/9904',2023,5,1,'2023-05-01',768.00,'1102',5,NULL,'3000','e3565ab030d94836964723e1904174a6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (295,'','2024-11-19 16:35:27.935741','2025-04-23 08:44:57.063073','Nebenkosten 05.2023 für 201/9904',2023,5,1,'2023-05-01',82.00,'1102',5,NULL,'2301','06694d5bf51f482c863481b44f047d24','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (296,'','2024-11-19 16:35:28.232615','2025-04-23 08:44:57.055168','Nettomiete 04.2023 für 201/9904',2023,4,1,'2023-04-01',768.00,'1102',5,NULL,'3000','3d62cc1b9a8143cdb85d8d0ac943adb0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (297,'','2024-11-19 16:35:28.345880','2025-04-23 08:44:57.057289','Nebenkosten 04.2023 für 201/9904',2023,4,1,'2023-04-01',82.00,'1102',5,NULL,'2301','c82d0b79e1e24ce0b6b6f6452f55ae11','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (298,'','2024-11-19 16:35:28.440944','2025-04-23 08:44:57.050586','Nettomiete 03.2023 für 201/9904',2023,3,1,'2023-03-01',768.00,'1102',5,NULL,'3000','1f8d48c6c6bd4986968c954bfccb1ff0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (299,'','2024-11-19 16:35:28.526801','2025-04-23 08:44:57.052805','Nebenkosten 03.2023 für 201/9904',2023,3,1,'2023-03-01',82.00,'1102',5,NULL,'2301','0b7d1c062e294d948e5a218f6c4a4442','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (300,'','2024-11-19 16:35:28.653326','2025-04-23 08:44:57.046055','Nettomiete 02.2023 für 201/9904',2023,2,1,'2023-02-01',768.00,'1102',5,NULL,'3000','521d32d1e4394988bb26cbd0b5859139','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (301,'','2024-11-19 16:35:28.768287','2025-04-23 08:44:57.048033','Nebenkosten 02.2023 für 201/9904',2023,2,1,'2023-02-01',82.00,'1102',5,NULL,'2301','9060d2b52a4c4ddeb0721624a2a386de','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (302,'','2024-11-19 16:35:28.896327','2025-04-23 08:44:57.041950','Nettomiete 01.2023 für 201/9904',2023,1,1,'2023-01-01',768.00,'1102',5,NULL,'3000','53bf1659562642b6ab84c96383a9047b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (303,'','2024-11-19 16:35:28.980317','2025-04-23 08:44:57.044018','Nebenkosten 01.2023 für 201/9904',2023,1,1,'2023-01-01',82.00,'1102',5,NULL,'2301','11ad42691df04227ae11093e7e0d3588','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (304,'','2024-11-19 16:35:29.106432','2025-04-23 08:44:57.037864','Nettomiete 12.2022 für 201/9904',2022,12,1,'2022-12-01',768.00,'1102',5,NULL,'3000','2bcb1784a0624b5bafe9c1f576e56e27','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (305,'','2024-11-19 16:35:29.209584','2025-04-23 08:44:57.039900','Nebenkosten 12.2022 für 201/9904',2022,12,1,'2022-12-01',82.00,'1102',5,NULL,'2301','7ed0517180a54a84978e4b0701715be1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (306,'','2024-11-19 16:35:29.349392','2025-04-23 08:44:57.033654','Nettomiete 11.2022 für 201/9904',2022,11,1,'2022-11-01',768.00,'1102',5,NULL,'3000','b0034c6119e841e0a08be55c78e648d3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (307,'','2024-11-19 16:35:29.535109','2025-04-23 08:44:57.035727','Nebenkosten 11.2022 für 201/9904',2022,11,1,'2022-11-01',82.00,'1102',5,NULL,'2301','467c1f719ea54176959322d8f97703c0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (308,'','2024-11-19 16:35:29.670404','2025-04-23 08:44:57.029608','Nettomiete 10.2022 für 201/9904',2022,10,1,'2022-10-01',768.00,'1102',5,NULL,'3000','0a5b56cd43b5419f83ba6d42f6523d62','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (309,'','2024-11-19 16:35:29.785589','2025-04-23 08:44:57.031601','Nebenkosten 10.2022 für 201/9904',2022,10,1,'2022-10-01',82.00,'1102',5,NULL,'2301','36bbccece5b14f03867c2849cc3c3f42','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (310,'','2024-11-19 16:35:29.896174','2025-04-23 08:44:57.025185','Nettomiete 09.2022 für 201/9904',2022,9,1,'2022-09-01',768.00,'1102',5,NULL,'3000','bfd9e4248b14463dba24acb914b4f498','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (311,'','2024-11-19 16:35:30.006888','2025-04-23 08:44:57.027484','Nebenkosten 09.2022 für 201/9904',2022,9,1,'2022-09-01',82.00,'1102',5,NULL,'2301','4959d5a3c5bf4374b5e7be895d1cb663','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (312,'','2024-11-19 16:35:30.137952','2025-04-23 08:44:57.020963','Nettomiete 08.2022 für 201/9904',2022,8,1,'2022-08-01',768.00,'1102',5,NULL,'3000','7cd201f2da0f4b94b0082ca12d775148','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (313,'','2024-11-19 16:35:30.253493','2025-04-23 08:44:57.023070','Nebenkosten 08.2022 für 201/9904',2022,8,1,'2022-08-01',82.00,'1102',5,NULL,'2301','c9d81feece0346ef8094cbe5efcaa1d2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (314,'','2024-11-19 16:35:30.395008','2024-12-18 15:30:01.708900','Nettomiete 10.2024 für 202',2024,10,1,'2024-10-01',1125.00,'1102',6,NULL,'3000','5b01385ba37647f8b45a59c67daeb8cb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (315,'','2024-11-19 16:35:30.508804','2024-12-18 15:30:01.710498','Nebenkosten 10.2024 für 202',2024,10,1,'2024-10-01',195.00,'1102',6,NULL,'2301','80ac602e23224ce382b6e2a8a7bcd77f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (316,'','2024-11-19 16:35:30.635446','2024-12-18 15:30:01.705657','Nettomiete 09.2024 für 202',2024,9,1,'2024-09-01',1125.00,'1102',6,NULL,'3000','66e95849fe7e45ce953253d8225216ec','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (317,'','2024-11-19 16:35:30.749245','2024-12-18 15:30:01.707153','Nebenkosten 09.2024 für 202',2024,9,1,'2024-09-01',195.00,'1102',6,NULL,'2301','b909c75787ca42ed919ce6339c7c042b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (318,'','2024-11-19 16:35:30.875858','2024-12-18 15:30:01.702531','Nettomiete 08.2024 für 202',2024,8,1,'2024-08-01',1125.00,'1102',6,NULL,'3000','08e6966c0aa64525948773174823e98a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (319,'','2024-11-19 16:35:30.992291','2024-12-18 15:30:01.704116','Nebenkosten 08.2024 für 202',2024,8,1,'2024-08-01',195.00,'1102',6,NULL,'2301','1e466273184044d09229abd627f93c00','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (320,'','2024-11-19 16:35:31.119650','2024-12-18 15:30:01.699320','Nettomiete 07.2024 für 202',2024,7,1,'2024-07-01',1125.00,'1102',6,NULL,'3000','b4df16ecad4d4577865d47743eb9fd76','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (321,'','2024-11-19 16:35:31.235921','2024-12-18 15:30:01.701034','Nebenkosten 07.2024 für 202',2024,7,1,'2024-07-01',195.00,'1102',6,NULL,'2301','00739c0d1f0d4f42bc86c3e8dac1b8bd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (322,'','2024-11-19 16:35:31.362933','2024-12-18 15:30:01.696241','Nettomiete 06.2024 für 202',2024,6,1,'2024-06-01',1125.00,'1102',6,NULL,'3000','2f8c5c87df464d38824acfb07263d8de','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (323,'','2024-11-19 16:35:31.479484','2024-12-18 15:30:01.697825','Nebenkosten 06.2024 für 202',2024,6,1,'2024-06-01',195.00,'1102',6,NULL,'2301','62e20312211942abade8808b9a5890f5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (324,'','2024-11-19 16:35:31.607072','2024-12-18 15:30:01.693047','Nettomiete 05.2024 für 202',2024,5,1,'2024-05-01',1125.00,'1102',6,NULL,'3000','762ed7a96afc4351ae24d86d0a5e7cdc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (325,'','2024-11-19 16:35:31.812511','2024-12-18 15:30:01.694516','Nebenkosten 05.2024 für 202',2024,5,1,'2024-05-01',195.00,'1102',6,NULL,'2301','45f89bd6efe94f39829655b20ddb7543','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (326,'','2024-11-19 16:35:31.931249','2024-12-18 15:30:01.689782','Nettomiete 04.2024 für 202',2024,4,1,'2024-04-01',1125.00,'1102',6,NULL,'3000','a652698e12944e2d9a8a6c3b57c67b28','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (327,'','2024-11-19 16:35:32.082440','2024-12-18 15:30:01.691386','Nebenkosten 04.2024 für 202',2024,4,1,'2024-04-01',195.00,'1102',6,NULL,'2301','2b3d81c6c960424db2430af3566ec436','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (328,'','2024-11-19 16:35:32.182933','2024-12-18 15:30:01.686540','Nettomiete 03.2024 für 202',2024,3,1,'2024-03-01',1125.00,'1102',6,NULL,'3000','902d3d310a3641babbc0746144dc4293','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (329,'','2024-11-19 16:35:32.298575','2024-12-18 15:30:01.688228','Nebenkosten 03.2024 für 202',2024,3,1,'2024-03-01',195.00,'1102',6,NULL,'2301','0a74724d182a4a8389bc839e6bd2d0fb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (330,'','2024-11-19 16:35:32.486178','2024-12-18 15:30:01.683272','Nettomiete 02.2024 für 202',2024,2,1,'2024-02-01',1125.00,'1102',6,NULL,'3000','b38a949716144457a29859e7a6d103b8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (331,'','2024-11-19 16:35:32.620309','2024-12-18 15:30:01.684943','Nebenkosten 02.2024 für 202',2024,2,1,'2024-02-01',195.00,'1102',6,NULL,'2301','f21b6c303e8244b29b56a88be2e969ce','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (332,'','2024-11-19 16:35:32.747175','2024-12-18 15:30:01.679919','Nettomiete 01.2024 für 202',2024,1,1,'2024-01-01',1125.00,'1102',6,NULL,'3000','22f841c10bda46888924ba30a545bd70','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (333,'','2024-11-19 16:35:32.875104','2024-12-18 15:30:01.681750','Nebenkosten 01.2024 für 202',2024,1,1,'2024-01-01',195.00,'1102',6,NULL,'2301','6ecc53bccc3c4cacbf48ec6ccac5b568','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (334,'','2024-11-19 16:35:33.001826','2024-12-18 15:30:01.676807','Nettomiete 12.2023 für 202',2023,12,1,'2023-12-01',1125.00,'1102',6,NULL,'3000','d1118d2974e04f12b00f5d97c7f9aa30','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (335,'','2024-11-19 16:35:33.118513','2024-12-18 15:30:01.678359','Nebenkosten 12.2023 für 202',2023,12,1,'2023-12-01',195.00,'1102',6,NULL,'2301','6486028232fe4255880e4c2d5119c587','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (336,'','2024-11-19 16:35:33.247724','2024-12-18 15:30:01.673635','Nettomiete 11.2023 für 202',2023,11,1,'2023-11-01',1125.00,'1102',6,NULL,'3000','9d64080d65e3472ca71d2c6cd122bba2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (337,'','2024-11-19 16:35:33.363876','2024-12-18 15:30:01.675153','Nebenkosten 11.2023 für 202',2023,11,1,'2023-11-01',195.00,'1102',6,NULL,'2301','1b2968ed48e746149bf540b0a4388ac6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (338,'','2024-11-19 16:35:33.481060','2024-12-18 15:30:01.670288','Nettomiete 10.2023 für 202',2023,10,1,'2023-10-01',1125.00,'1102',6,NULL,'3000','36e6d97a61b74504b3615ca020d450c9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (339,'','2024-11-19 16:35:33.655342','2024-12-18 15:30:01.672087','Nebenkosten 10.2023 für 202',2023,10,1,'2023-10-01',195.00,'1102',6,NULL,'2301','0355128daf294ac18f1795105fdcc35d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (340,'','2024-11-19 16:35:33.766402','2024-12-18 15:30:01.666721','Nettomiete 09.2023 für 202',2023,9,1,'2023-09-01',1125.00,'1102',6,NULL,'3000','c3bdebdb8284463eb98f4ffb4d161336','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (341,'','2024-11-19 16:35:33.852782','2024-12-18 15:30:01.668720','Nebenkosten 09.2023 für 202',2023,9,1,'2023-09-01',195.00,'1102',6,NULL,'2301','4e3a84d9d5d54a6f81671b59994503af','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (342,'','2024-11-19 16:35:33.968802','2024-12-18 15:30:01.663167','Nettomiete 08.2023 für 202',2023,8,1,'2023-08-01',1125.00,'1102',6,NULL,'3000','ba55a9456e684700b056de3cb83912b6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (343,'','2024-11-19 16:35:34.081224','2024-12-18 15:30:01.665085','Nebenkosten 08.2023 für 202',2023,8,1,'2023-08-01',195.00,'1102',6,NULL,'2301','83df179bcb00421985684f8d0b0c5fa6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (344,'','2024-11-19 16:35:34.208432','2024-12-18 15:30:01.659594','Nettomiete 07.2023 für 202',2023,7,1,'2023-07-01',1125.00,'1102',6,NULL,'3000','7d18ea0a102e4fa4958386170049c660','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (345,'','2024-11-19 16:35:34.325019','2024-12-18 15:30:01.661376','Nebenkosten 07.2023 für 202',2023,7,1,'2023-07-01',195.00,'1102',6,NULL,'2301','e6a6959f99d14fe8bc355527687250a0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (346,'','2024-11-19 16:35:34.518671','2024-12-18 15:30:01.656200','Nettomiete 06.2023 für 202',2023,6,1,'2023-06-01',1125.00,'1102',6,NULL,'3000','387d3042fb504284abc6b158bd59874d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (347,'','2024-11-19 16:35:34.634753','2024-12-18 15:30:01.657725','Nebenkosten 06.2023 für 202',2023,6,1,'2023-06-01',195.00,'1102',6,NULL,'2301','b263fdfc5ed847b481651598057d3362','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (348,'','2024-11-19 16:35:34.764581','2024-12-18 15:30:01.653081','Nettomiete 05.2023 für 202',2023,5,1,'2023-05-01',1125.00,'1102',6,NULL,'3000','8e58a65ee9fa4322b3a15c66358a4839','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (349,'','2024-11-19 16:35:34.880239','2024-12-18 15:30:01.654623','Nebenkosten 05.2023 für 202',2023,5,1,'2023-05-01',195.00,'1102',6,NULL,'2301','9e09140eeb07464c9150434d0aca2c4c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (350,'','2024-11-19 16:35:35.008349','2024-12-18 15:30:01.649961','Nettomiete 04.2023 für 202',2023,4,1,'2023-04-01',1125.00,'1102',6,NULL,'3000','a62787df738d4e03a9458747ccf56f12','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (351,'','2024-11-19 16:35:35.145250','2024-12-18 15:30:01.651552','Nebenkosten 04.2023 für 202',2023,4,1,'2023-04-01',195.00,'1102',6,NULL,'2301','df4b2fa54bd84678b24bf72be814b028','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (352,'','2024-11-19 16:35:35.272405','2024-12-18 15:30:01.646702','Nettomiete 03.2023 für 202',2023,3,1,'2023-03-01',1125.00,'1102',6,NULL,'3000','dc935a58ddc24f11864ec0a25c82f57e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (353,'','2024-11-19 16:35:35.387470','2024-12-18 15:30:01.648375','Nebenkosten 03.2023 für 202',2023,3,1,'2023-03-01',195.00,'1102',6,NULL,'2301','a370a6cd0e9f4ec492e551a46e92a6da','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (354,'','2024-11-19 16:35:35.630459','2024-12-18 15:30:01.643320','Nettomiete 02.2023 für 202',2023,2,1,'2023-02-01',1125.00,'1102',6,NULL,'3000','44fc2a2f7e184697b3c3555be79bdaa7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (355,'','2024-11-19 16:35:35.731287','2024-12-18 15:30:01.645092','Nebenkosten 02.2023 für 202',2023,2,1,'2023-02-01',195.00,'1102',6,NULL,'2301','e65dea5b40464ab6adcabdaab940e940','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (356,'','2024-11-19 16:35:35.891752','2024-12-18 15:30:01.639264','Nettomiete 01.2023 für 202',2023,1,1,'2023-01-01',1125.00,'1102',6,NULL,'3000','4799c036a15746778d2d34390827bf43','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (357,'','2024-11-19 16:35:35.966751','2024-12-18 15:30:01.641582','Nebenkosten 01.2023 für 202',2023,1,1,'2023-01-01',195.00,'1102',6,NULL,'2301','8c8da3b5bf774568bfa76534e935c2c2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (358,'','2024-11-19 16:35:36.056978','2024-12-18 15:30:01.635305','Nettomiete 12.2022 für 202',2022,12,1,'2022-12-01',1125.00,'1102',6,NULL,'3000','312c0ab69a5a4d4cb3ec332f438b897c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (359,'','2024-11-19 16:35:36.139644','2024-12-18 15:30:01.637167','Nebenkosten 12.2022 für 202',2022,12,1,'2022-12-01',195.00,'1102',6,NULL,'2301','e42dc40ef39d4fd2a51d0f4d0528f799','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (360,'','2024-11-19 16:35:36.238735','2024-12-18 15:30:01.631831','Nettomiete 11.2022 für 202',2022,11,1,'2022-11-01',1125.00,'1102',6,NULL,'3000','64336af058a74ea9a32479be2ec5e345','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (361,'','2024-11-19 16:35:36.352561','2024-12-18 15:30:01.633510','Nebenkosten 11.2022 für 202',2022,11,1,'2022-11-01',195.00,'1102',6,NULL,'2301','512b5a9e2da04d44ba8dccaca23954da','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (362,'','2024-11-19 16:35:36.520791','2024-12-18 15:30:01.627841','Nettomiete 10.2022 für 202',2022,10,1,'2022-10-01',1125.00,'1102',6,NULL,'3000','0ccf55804f774049b162195d2134f450','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (363,'','2024-11-19 16:35:36.629982','2024-12-18 15:30:01.630087','Nebenkosten 10.2022 für 202',2022,10,1,'2022-10-01',195.00,'1102',6,NULL,'2301','8d16610e7c2f428ab807706d4c89dd5a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (364,'','2024-11-19 16:35:36.757490','2024-12-18 15:30:01.621478','Nettomiete 09.2022 für 202',2022,9,1,'2022-09-01',1125.00,'1102',6,NULL,'3000','0c91e9adbda44cff8bbca91931919de9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (365,'','2024-11-19 16:35:36.870994','2024-12-18 15:30:01.624024','Nebenkosten 09.2022 für 202',2022,9,1,'2022-09-01',195.00,'1102',6,NULL,'2301','e50656cf4cbc41df9794300950dcd5fd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (366,'','2024-11-19 16:35:37.062642','2024-12-18 15:30:01.617575','Nettomiete 08.2022 für 202',2022,8,1,'2022-08-01',1125.00,'1102',6,NULL,'3000','da8082dd0cb947b78ffe444e2865207d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (367,'','2024-11-19 16:35:37.170082','2024-12-18 15:30:01.619396','Nebenkosten 08.2022 für 202',2022,8,1,'2022-08-01',195.00,'1102',6,NULL,'2301','41221cbc5b8343b7b2c858e8d15a9560','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (368,'','2024-11-19 16:35:37.306083','2024-12-18 15:32:44.846087','Nettomiete 10.2024 für 003/9906',2024,10,1,'2024-10-01',1265.00,'1102',7,NULL,'3001','34edd035caa54cfbbdaf14e9c3c57ed1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (369,'','2024-11-19 16:35:37.413529','2024-12-18 15:32:44.848052','Nebenkosten 10.2024 für 003/9906',2024,10,1,'2024-10-01',187.00,'1102',7,NULL,'2301','f0100d2434844092adcab853c2d462fd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (370,'','2024-11-19 16:35:37.501717','2024-12-18 15:32:44.850252','Strompauschale 10.2024 für 003/9906',2024,10,1,'2024-10-01',5.00,'1102',7,NULL,'2302','5a40ad8e27104119ac39f706a6ce1b07','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (371,'','2024-11-19 16:35:37.691315','2024-12-18 15:32:44.839955','Nettomiete 09.2024 für 003/9906',2024,9,1,'2024-09-01',1265.00,'1102',7,NULL,'3001','48c5ac761fe24171ae4c30924138edb5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (372,'','2024-11-19 16:35:37.806811','2024-12-18 15:32:44.841897','Nebenkosten 09.2024 für 003/9906',2024,9,1,'2024-09-01',187.00,'1102',7,NULL,'2301','1883425b2abd42b7988ed4d4b30426f3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (373,'','2024-11-19 16:35:37.935413','2024-12-18 15:32:44.843832','Strompauschale 09.2024 für 003/9906',2024,9,1,'2024-09-01',5.00,'1102',7,NULL,'2302','406ddb4349d74fb0a7fb8c0887b7eb5c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (374,'','2024-11-19 16:35:38.049047','2024-12-18 15:32:44.832736','Nettomiete 08.2024 für 003/9906',2024,8,1,'2024-08-01',1265.00,'1102',7,NULL,'3001','a0e07b05b8f74f4d8cdaa560ecab2f55','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (375,'','2024-11-19 16:35:38.158427','2024-12-18 15:32:44.836065','Nebenkosten 08.2024 für 003/9906',2024,8,1,'2024-08-01',187.00,'1102',7,NULL,'2301','e2bfbe97876e4085a36bba3535307c30','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (376,'','2024-11-19 16:35:38.279746','2024-12-18 15:32:44.837939','Strompauschale 08.2024 für 003/9906',2024,8,1,'2024-08-01',5.00,'1102',7,NULL,'2302','94ddc6d184cb4dba858c28a69f27e0f0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (377,'','2024-11-19 16:35:38.458139','2024-12-18 15:32:44.826522','Nettomiete 07.2024 für 003/9906',2024,7,1,'2024-07-01',1265.00,'1102',7,NULL,'3001','0223cb101ae14f39b5c64b3225d8dc97','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (378,'','2024-11-19 16:35:38.566659','2024-12-18 15:32:44.828760','Nebenkosten 07.2024 für 003/9906',2024,7,1,'2024-07-01',187.00,'1102',7,NULL,'2301','998cfa3b18b64bada2a701cd4082fd78','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (379,'','2024-11-19 16:35:38.688183','2024-12-18 15:32:44.830784','Strompauschale 07.2024 für 003/9906',2024,7,1,'2024-07-01',5.00,'1102',7,NULL,'2302','9971eae823254be480589d2bd8d91602','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (380,'','2024-11-19 16:35:38.823216','2024-12-18 15:32:44.820867','Nettomiete 06.2024 für 003/9906',2024,6,1,'2024-06-01',1265.00,'1102',7,NULL,'3001','38230701ddf342958c89eef487df4bc0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (381,'','2024-11-19 16:35:38.932133','2024-12-18 15:32:44.822670','Nebenkosten 06.2024 für 003/9906',2024,6,1,'2024-06-01',187.00,'1102',7,NULL,'2301','0d774ac4a85842419050068a817693fe','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (382,'','2024-11-19 16:35:39.054794','2024-12-18 15:32:44.824649','Strompauschale 06.2024 für 003/9906',2024,6,1,'2024-06-01',5.00,'1102',7,NULL,'2302','3f2edb79d27e40c18b69f148e714df29','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (383,'','2024-11-19 16:35:39.165651','2024-12-18 15:32:44.814406','Nettomiete 05.2024 für 003/9906',2024,5,1,'2024-05-01',1265.00,'1102',7,NULL,'3001','0ebc9c94ab564a3ea91435b8a1ae7f43','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (384,'','2024-11-19 16:35:39.274916','2024-12-18 15:32:44.816123','Nebenkosten 05.2024 für 003/9906',2024,5,1,'2024-05-01',187.00,'1102',7,NULL,'2301','3adf6df9418646769ac01acdd76bf93d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (385,'','2024-11-19 16:35:39.414914','2024-12-18 15:32:44.818881','Strompauschale 05.2024 für 003/9906',2024,5,1,'2024-05-01',5.00,'1102',7,NULL,'2302','89ba376079b946fc9e02974b04d726f6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (386,'','2024-11-19 16:35:39.555643','2024-12-18 15:32:44.809443','Nettomiete 04.2024 für 003/9906',2024,4,1,'2024-04-01',1265.00,'1102',7,NULL,'3001','fda73d408eb349e288ef589ec55a49fa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (387,'','2024-11-19 16:35:39.665654','2024-12-18 15:32:44.811105','Nebenkosten 04.2024 für 003/9906',2024,4,1,'2024-04-01',187.00,'1102',7,NULL,'2301','418fb0865b8141f78c8d82e3a4c8702a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (388,'','2024-11-19 16:35:39.787247','2024-12-18 15:32:44.812836','Strompauschale 04.2024 für 003/9906',2024,4,1,'2024-04-01',5.00,'1102',7,NULL,'2302','661ca5fb96464466a3edd41e0ebedf02','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (389,'','2024-11-19 16:35:39.952067','2024-12-18 15:32:44.801943','Nettomiete 03.2024 für 003/9906',2024,3,1,'2024-03-01',1265.00,'1102',7,NULL,'3001','b70b2386d09f4a0abc76ddf1fa31490f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (390,'','2024-11-19 16:35:40.085864','2024-12-18 15:32:44.805837','Nebenkosten 03.2024 für 003/9906',2024,3,1,'2024-03-01',187.00,'1102',7,NULL,'2301','06180b8e20a645478ea696625e4c2f08','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (391,'','2024-11-19 16:35:40.384773','2024-12-18 15:32:44.807701','Strompauschale 03.2024 für 003/9906',2024,3,1,'2024-03-01',5.00,'1102',7,NULL,'2302','6c8f1992477e4a268f03463ccf897de5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (392,'','2024-11-19 16:35:40.505226','2024-12-18 15:32:44.796733','Nettomiete 02.2024 für 003/9906',2024,2,1,'2024-02-01',1265.00,'1102',7,NULL,'3001','5e5571beefbc4250a7e8d5aab8da84bb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (393,'','2024-11-19 16:35:40.614989','2024-12-18 15:32:44.798393','Nebenkosten 02.2024 für 003/9906',2024,2,1,'2024-02-01',187.00,'1102',7,NULL,'2301','01809d7711bc4407b7781ef74246d8c5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (394,'','2024-11-19 16:35:40.736734','2024-12-18 15:32:44.800180','Strompauschale 02.2024 für 003/9906',2024,2,1,'2024-02-01',5.00,'1102',7,NULL,'2302','47cc17e56e2b44c2ac6d503155ebb389','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (395,'','2024-11-19 16:35:40.837227','2024-12-18 15:32:44.791517','Nettomiete 01.2024 für 003/9906',2024,1,1,'2024-01-01',1265.00,'1102',7,NULL,'3001','86b3690f10304101a951fd098b58231a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (396,'','2024-11-19 16:35:40.952236','2024-12-18 15:32:44.793208','Nebenkosten 01.2024 für 003/9906',2024,1,1,'2024-01-01',187.00,'1102',7,NULL,'2301','dc492315f55d42718e7433b759d6691f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (397,'','2024-11-19 16:35:41.069952','2024-12-18 15:32:44.794908','Strompauschale 01.2024 für 003/9906',2024,1,1,'2024-01-01',5.00,'1102',7,NULL,'2302','d7e60a836ed044739be8a515a2f0c982','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (398,'','2024-11-19 16:35:41.204781','2024-12-18 15:32:44.786348','Nettomiete 12.2023 für 003/9906',2023,12,1,'2023-12-01',1265.00,'1102',7,NULL,'3001','ac52043c54b04d628376dea724668ce3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (399,'','2024-11-19 16:35:41.337200','2024-12-18 15:32:44.788040','Nebenkosten 12.2023 für 003/9906',2023,12,1,'2023-12-01',187.00,'1102',7,NULL,'2301','3d8237379d0f48df85ba371132a66680','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (400,'','2024-11-19 16:35:41.491918','2024-12-18 15:32:44.789813','Strompauschale 12.2023 für 003/9906',2023,12,1,'2023-12-01',5.00,'1102',7,NULL,'2302','0b74716a54864be5a08dd999f1eaade8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (401,'','2024-11-19 16:35:41.612676','2024-12-18 15:32:44.781253','Nettomiete 11.2023 für 003/9906',2023,11,1,'2023-11-01',1265.00,'1102',7,NULL,'3001','682755b70b13475cb90bd5dce8e058fa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (402,'','2024-11-19 16:35:41.722360','2024-12-18 15:32:44.782964','Nebenkosten 11.2023 für 003/9906',2023,11,1,'2023-11-01',187.00,'1102',7,NULL,'2301','04235850f8bb4f288e7f4b4f36964fe7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (403,'','2024-11-19 16:35:41.855713','2024-12-18 15:32:44.784679','Strompauschale 11.2023 für 003/9906',2023,11,1,'2023-11-01',5.00,'1102',7,NULL,'2302','269a1e36567240c1a4b6463a05a3bd8c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (404,'','2024-11-19 16:35:42.044942','2024-12-18 15:32:44.776097','Nettomiete 10.2023 für 003/9906',2023,10,1,'2023-10-01',1265.00,'1102',7,NULL,'3001','b0722697435d4690811f1b3df6ae7d7e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (405,'','2024-11-19 16:35:42.144358','2024-12-18 15:32:44.777784','Nebenkosten 10.2023 für 003/9906',2023,10,1,'2023-10-01',187.00,'1102',7,NULL,'2301','04c184eaed1e46c58ac8e1af4b39978b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (406,'','2024-11-19 16:35:42.230474','2024-12-18 15:32:44.779620','Strompauschale 10.2023 für 003/9906',2023,10,1,'2023-10-01',5.00,'1102',7,NULL,'2302','0368991529c14099b64cf1f663449b59','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (407,'','2024-11-19 16:35:42.330983','2024-12-18 15:32:44.770794','Nettomiete 09.2023 für 003/9906',2023,9,1,'2023-09-01',1265.00,'1102',7,NULL,'3001','2022fc15ab274b438e62b7b6d518e4ca','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (408,'','2024-11-19 16:35:42.419170','2024-12-18 15:32:44.772604','Nebenkosten 09.2023 für 003/9906',2023,9,1,'2023-09-01',187.00,'1102',7,NULL,'2301','e2740eb6e77f447da4dc00592452aaea','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (409,'','2024-11-19 16:35:42.513273','2024-12-18 15:32:44.774313','Strompauschale 09.2023 für 003/9906',2023,9,1,'2023-09-01',5.00,'1102',7,NULL,'2302','b0e0c9ac9b334893bc47210da310017c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (410,'','2024-11-19 16:35:42.645601','2024-12-18 15:32:44.765081','Nettomiete 08.2023 für 003/9906',2023,8,1,'2023-08-01',1265.00,'1102',7,NULL,'3001','752d2b0d826a45c9b3a89c0ef1133110','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (411,'','2024-11-19 16:35:42.952397','2024-12-18 15:32:44.766956','Nebenkosten 08.2023 für 003/9906',2023,8,1,'2023-08-01',187.00,'1102',7,NULL,'2301','58a8085df350457eae518941681ca7a1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (412,'','2024-11-19 16:35:43.086059','2024-12-18 15:32:44.768942','Strompauschale 08.2023 für 003/9906',2023,8,1,'2023-08-01',5.00,'1102',7,NULL,'2302','266090d70a8a478a90a72e21731e6c2d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (413,'','2024-11-19 16:35:43.233314','2024-12-18 15:32:44.759052','Nettomiete 07.2023 für 003/9906',2023,7,1,'2023-07-01',1265.00,'1102',7,NULL,'3001','e323ce51d9f140b28a73f320c2fc81d0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (414,'','2024-11-19 16:35:43.396863','2024-12-18 15:32:44.760845','Nebenkosten 07.2023 für 003/9906',2023,7,1,'2023-07-01',187.00,'1102',7,NULL,'2301','76552f425515475d80d558fa05d80387','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (415,'','2024-11-19 16:35:43.505165','2024-12-18 15:32:44.762777','Strompauschale 07.2023 für 003/9906',2023,7,1,'2023-07-01',5.00,'1102',7,NULL,'2302','4343b252c92342568af3946289525cbf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (416,'','2024-11-19 16:35:43.605720','2024-12-18 15:32:44.753772','Nettomiete 06.2023 für 003/9906',2023,6,1,'2023-06-01',1265.00,'1102',7,NULL,'3001','20ad0f36f74e474b9920b20ef96213aa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (417,'','2024-11-19 16:35:43.714783','2024-12-18 15:32:44.755538','Nebenkosten 06.2023 für 003/9906',2023,6,1,'2023-06-01',187.00,'1102',7,NULL,'2301','4bdf05235c0a466ebfb32b53d70faf53','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (418,'','2024-11-19 16:35:43.803355','2024-12-18 15:32:44.757369','Strompauschale 06.2023 für 003/9906',2023,6,1,'2023-06-01',5.00,'1102',7,NULL,'2302','3eb482dea61c4abab63471297ae7f2e4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (419,'','2024-11-19 16:35:43.937962','2024-12-18 15:32:44.747856','Nettomiete 05.2023 für 003/9906',2023,5,1,'2023-05-01',1265.00,'1102',7,NULL,'3001','7ded0d3d5745477f85c9080369c77573','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (420,'','2024-11-19 16:35:44.047777','2024-12-18 15:32:44.750025','Nebenkosten 05.2023 für 003/9906',2023,5,1,'2023-05-01',187.00,'1102',7,NULL,'2301','baf1f19f672a4d75b8c66c3a4ed43dd2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (421,'','2024-11-19 16:35:44.170605','2024-12-18 15:32:44.751990','Strompauschale 05.2023 für 003/9906',2023,5,1,'2023-05-01',5.00,'1102',7,NULL,'2302','f6decb523cc548f08d3ea94b89d44b7d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (422,'','2024-11-19 16:35:44.276259','2024-12-18 15:32:44.742586','Nettomiete 04.2023 für 003/9906',2023,4,1,'2023-04-01',1265.00,'1102',7,NULL,'3001','867ba3f6596349f3b77acb56a37c09c0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (423,'','2024-11-19 16:35:44.415026','2024-12-18 15:32:44.744219','Nebenkosten 04.2023 für 003/9906',2023,4,1,'2023-04-01',187.00,'1102',7,NULL,'2301','7db359425fd940619d6996693afdc381','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (424,'','2024-11-19 16:35:44.535663','2024-12-18 15:32:44.746090','Strompauschale 04.2023 für 003/9906',2023,4,1,'2023-04-01',5.00,'1102',7,NULL,'2302','2ae9986cf27e4fb1a76f32dc50adf15f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (425,'','2024-11-19 16:35:44.670508','2024-12-18 15:32:44.737547','Nettomiete 03.2023 für 003/9906',2023,3,1,'2023-03-01',1265.00,'1102',7,NULL,'3001','5f4b8dd6a30a4d6bb74ca4a319c5d042','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (426,'','2024-11-19 16:35:44.779837','2024-12-18 15:32:44.739129','Nebenkosten 03.2023 für 003/9906',2023,3,1,'2023-03-01',187.00,'1102',7,NULL,'2301','6213d32aae1343b999162f3ba4d6a0f4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (427,'','2024-11-19 16:35:44.911190','2024-12-18 15:32:44.740935','Strompauschale 03.2023 für 003/9906',2023,3,1,'2023-03-01',5.00,'1102',7,NULL,'2302','1c4f9877c85146df97977f0a656cbcf3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (428,'','2024-11-19 16:35:45.011429','2024-12-18 15:32:44.732612','Nettomiete 02.2023 für 003/9906',2023,2,1,'2023-02-01',1265.00,'1102',7,NULL,'3001','990b32d0529a4b21a3a96e3e05c7cc15','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (429,'','2024-11-19 16:35:45.121734','2024-12-18 15:32:44.734254','Nebenkosten 02.2023 für 003/9906',2023,2,1,'2023-02-01',187.00,'1102',7,NULL,'2301','d49f55dc9a77404fb9db14b8777a35b7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (430,'','2024-11-19 16:35:45.210056','2024-12-18 15:32:44.735947','Strompauschale 02.2023 für 003/9906',2023,2,1,'2023-02-01',5.00,'1102',7,NULL,'2302','ecb5e5e502a04a1c9e26d52d95f51836','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (431,'','2024-11-19 16:35:45.344021','2024-12-18 15:32:44.727234','Nettomiete 01.2023 für 003/9906',2023,1,1,'2023-01-01',1265.00,'1102',7,NULL,'3001','a03015ca34aa4e41ac34c129e6207e42','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (432,'','2024-11-19 16:35:45.454709','2024-12-18 15:32:44.729035','Nebenkosten 01.2023 für 003/9906',2023,1,1,'2023-01-01',187.00,'1102',7,NULL,'2301','182f03e047994544b050c7c1f9ccf366','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (433,'','2024-11-19 16:35:45.575865','2024-12-18 15:32:44.730719','Strompauschale 01.2023 für 003/9906',2023,1,1,'2023-01-01',5.00,'1102',7,NULL,'2302','d8a304ed505147e793cd46c0db2753d9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (434,'','2024-11-19 16:35:45.710408','2024-12-18 15:32:44.722518','Nettomiete 12.2022 für 003/9906',2022,12,1,'2022-12-01',1265.00,'1102',7,NULL,'3001','824443bb051d4bd791bc534e8a6fd383','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (435,'','2024-11-19 16:35:45.876309','2024-12-18 15:32:44.724118','Nebenkosten 12.2022 für 003/9906',2022,12,1,'2022-12-01',187.00,'1102',7,NULL,'2301','8eabb255dead46979c49e1eec3b98580','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (436,'','2024-11-19 16:35:45.976370','2024-12-18 15:32:44.725708','Strompauschale 12.2022 für 003/9906',2022,12,1,'2022-12-01',5.00,'1102',7,NULL,'2302','bf27790f667344288f0675a71a3c4455','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (437,'','2024-11-19 16:35:46.110420','2024-12-18 15:32:44.717438','Nettomiete 11.2022 für 003/9906',2022,11,1,'2022-11-01',1265.00,'1102',7,NULL,'3001','a03a28b6d96d43a6bf872016a027ba9a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (438,'','2024-11-19 16:35:46.219533','2024-12-18 15:32:44.719096','Nebenkosten 11.2022 für 003/9906',2022,11,1,'2022-11-01',187.00,'1102',7,NULL,'2301','34b70c8412594031b1fc126e2d205045','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (439,'','2024-11-19 16:35:46.340557','2024-12-18 15:32:44.720954','Strompauschale 11.2022 für 003/9906',2022,11,1,'2022-11-01',5.00,'1102',7,NULL,'2302','d214521f211b43e6b278c977f4eb4bab','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (440,'','2024-11-19 16:35:46.496493','2024-12-18 15:32:44.712629','Nettomiete 10.2022 für 003/9906',2022,10,1,'2022-10-01',1265.00,'1102',7,NULL,'3001','f3645b89efa945c88b584e51b76944b1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (441,'','2024-11-19 16:35:46.605263','2024-12-18 15:32:44.714352','Nebenkosten 10.2022 für 003/9906',2022,10,1,'2022-10-01',187.00,'1102',7,NULL,'2301','63a40a1564354468b6395a964a15560e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (442,'','2024-11-19 16:35:46.705187','2024-12-18 15:32:44.715938','Strompauschale 10.2022 für 003/9906',2022,10,1,'2022-10-01',5.00,'1102',7,NULL,'2302','81c9aeb78c314a2f93f78a0e00a9f4db','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (443,'','2024-11-19 16:35:46.806224','2024-12-18 15:32:44.707890','Nettomiete 09.2022 für 003/9906',2022,9,1,'2022-09-01',1265.00,'1102',7,NULL,'3001','33478c7d94e54753a8c536781f4d878e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (444,'','2024-11-19 16:35:46.882256','2024-12-18 15:32:44.709433','Nebenkosten 09.2022 für 003/9906',2022,9,1,'2022-09-01',187.00,'1102',7,NULL,'2301','7c64fab56a6a4b23a0fba33a51f88734','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (445,'','2024-11-19 16:35:46.970140','2024-12-18 15:32:44.711052','Strompauschale 09.2022 für 003/9906',2022,9,1,'2022-09-01',5.00,'1102',7,NULL,'2302','d3fff4fb1df14db0931a1cc47564fb72','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (446,'','2024-11-19 16:35:47.103358','2024-12-18 15:32:44.703255','Nettomiete 08.2022 für 003/9906',2022,8,1,'2022-08-01',1265.00,'1102',7,NULL,'3001','c7078a8902384d7bb5ea9a8c84a2bdae','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (447,'','2024-11-19 16:35:47.225814','2024-12-18 15:32:44.704817','Nebenkosten 08.2022 für 003/9906',2022,8,1,'2022-08-01',187.00,'1102',7,NULL,'2301','24f32fb1631143878d12575aa973f606','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (448,'','2024-11-19 16:35:47.382711','2024-12-18 15:32:44.706306','Strompauschale 08.2022 für 003/9906',2022,8,1,'2022-08-01',5.00,'1102',7,NULL,'2302','85793b375dd8478c83e0415bddee8447','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (449,'Miete Gästezimmer 100, 2 Nächte CHF 100.00','2024-12-18 12:36:01.842762','2024-12-18 15:30:01.885950','Miete Gästezimmer',NULL,NULL,1,'2024-12-18',100.00,'1100',NULL,30,'3520','f968d27f689c41168f5e377a5d08a320','Invoice',1,7,'','','',0);
INSERT INTO `geno_invoice` VALUES (450,'','2024-12-18 15:24:37.875101','2024-12-18 15:30:01.135987','Einzahlung Mietzins wiederkehrend 002/9902',NULL,NULL,1,'2024-12-18',63800.00,'1102',1,NULL,'1020.1','a79bb240009f44c2bd6373c28b82fe34','Payment',1,2,'DEMO Einzahlung/Dupont, Jean','100000000000000000000100005','_DEMO_100000000000000000000100005_20241218162405_',0);
INSERT INTO `geno_invoice` VALUES (452,'','2024-12-18 15:29:14.175563','2024-12-18 15:30:01.380947','Einzahlung Mietzins wiederkehrend 101/9903',NULL,NULL,1,'2024-12-18',212425.00,'1102',4,NULL,'1020.1','936204158f5b496890dfb13ba74bcfdf','Payment',1,2,'DEMO Einzahlung/Borg, Folana','100000000000000000000400008','_DEMO_100000000000000000000400008_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (453,'','2024-12-18 15:29:14.409647','2024-12-18 15:30:01.607246','Einzahlung Mietzins wiederkehrend 202',NULL,NULL,1,'2024-12-18',38280.00,'1102',6,NULL,'1020.1','07f827e727c24387bfa4e9d45317df26','Payment',1,2,'DEMO Einzahlung/Jensen, Hugo','100000000000000000000600001','_DEMO_100000000000000000000600001_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (454,'','2024-12-18 15:29:14.449147','2024-12-18 15:30:01.792780','Einzahlung Mietzins wiederkehrend 002/9902',NULL,NULL,1,'2024-12-18',6600.00,'1102',8,NULL,'1020.1','182f5d318c01484b9ac0d9a7f6522641','Payment',1,2,'DEMO Einzahlung/Alder, Mario','100000000000000000000800000','_DEMO_100000000000000000000800000_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (455,'','2024-12-18 15:29:14.486490','2025-04-23 08:42:37.937491','Einzahlung Mietzins wiederkehrend 201/9904',NULL,NULL,1,'2024-12-18',2550.00,'1102',10,NULL,'1020.1','68f1282d744941dca17843cbd3af8c9a','Payment',1,2,'DEMO Einzahlung/Deshar, Fatma','100000000000000000001000006','_DEMO_100000000000000000001000006_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (456,'','2024-12-18 15:29:14.523371','2024-12-18 15:30:01.840670','Einzahlung Mietzins wiederkehrend 203',NULL,NULL,1,'2024-12-18',1500.00,'1102',12,NULL,'1020.1','45c0b924d706492099949754ab7a7790','Payment',1,2,'DEMO Einzahlung/Rossi, Mario','100000000000000000001200007','_DEMO_100000000000000000001200007_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (457,'','2024-12-18 15:29:14.558924','2024-12-18 15:30:01.863823','Einzahlung Mietzins wiederkehrend PP-01',NULL,NULL,1,'2024-12-18',360.00,'1102',14,NULL,'1020.1','36647850e65c469d87e5c7d0f589efb9','Payment',1,2,'DEMO Einzahlung/Brot GmbH,  ','100000000000000000001400002','_DEMO_100000000000000000001400002_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (458,'','2024-12-18 15:29:14.582359','2024-12-18 15:30:01.884078','Einzahlung Miete Gästezimmer/0000000449',NULL,NULL,1,'2024-12-18',100.00,'1100',NULL,30,'1020.1','98f0dea84d3640b1a117e73e877cfe7b','Payment',1,7,'DEMO Einzahlung/Rossi, Mario','310000000449000000003000000','_DEMO_310000000449000000003000000_20241218162900_',0);
INSERT INTO `geno_invoice` VALUES (459,'','2024-12-18 15:31:39.101575','2024-12-18 15:32:44.399574','Einzahlung Mietzins wiederkehrend 001/9901/9906',NULL,NULL,1,'2024-12-18',57188.00,'1102',3,NULL,'1020.1','6adc90bdccd94e62b851001906c9e9bd','Payment',1,2,'DEMO Einzahlung/Muster, Anna','100000000000000000000300004','_DEMO_100000000000000000000300004_20241218163115_',0);
INSERT INTO `geno_invoice` VALUES (460,'','2024-12-18 15:31:39.141877','2024-12-18 15:32:44.690364','Einzahlung Mietzins wiederkehrend 003/9906',NULL,NULL,1,'2024-12-18',42253.00,'1102',7,NULL,'1020.1','5feda0dcd5eb4919bdc1c996f453ab50','Payment',1,2,'DEMO Einzahlung/Brot GmbH,  ','100000000000000000000700007','_DEMO_100000000000000000000700007_20241218163115_',0);
INSERT INTO `geno_invoice` VALUES (461,'','2024-12-18 15:31:39.177330','2024-12-18 15:32:44.868282','Einzahlung Mietzins wiederkehrend 202/9905',NULL,NULL,1,'2024-12-18',3960.00,'1102',11,NULL,'1020.1','824c0629c93c499da2cf231924993d49','Payment',1,2,'DEMO Einzahlung/Rossi, Mario','100000000000000000001100001','_DEMO_100000000000000000001100001_20241218163115_',0);
INSERT INTO `geno_invoice` VALUES (462,'','2024-12-18 15:31:39.211242','2024-12-18 15:32:44.892157','Einzahlung Mietzins wiederkehrend PP-01',NULL,NULL,1,'2024-12-18',360.00,'1102',15,NULL,'1020.1','757d7d22508c497690fd83c82a81d0ad','Payment',1,2,'DEMO Einzahlung/Jäger, Marta','100000000000000000001500003','_DEMO_100000000000000000001500003_20241218163115_',0);
INSERT INTO `geno_invoice` VALUES (463,'','2025-04-23 08:40:21.962524','2025-04-23 09:37:00.149609','Nettomiete 03.2025 für 002/9902',2025,3,1,'2025-03-01',1950.00,'1102',8,NULL,'3000','3d6744df151f49938f3167d236678967','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (464,'','2025-04-23 08:40:21.996399','2025-04-23 09:37:00.151630','Nebenkosten 03.2025 für 002/9902',2025,3,1,'2025-03-01',250.00,'1102',8,NULL,'2301','91effb9d00dc4db4a470350e446c64cf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (465,'','2025-04-23 08:40:22.036428','2025-04-23 09:37:00.145440','Nettomiete 02.2025 für 002/9902',2025,2,1,'2025-02-01',1950.00,'1102',8,NULL,'3000','d188d07b447c4295abbba4db2f75623a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (466,'','2025-04-23 08:40:22.066513','2025-04-23 09:37:00.147583','Nebenkosten 02.2025 für 002/9902',2025,2,1,'2025-02-01',250.00,'1102',8,NULL,'2301','c3273b8efa8d465cad9d6859e5aa81c9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (467,'','2025-04-23 08:40:22.103066','2025-04-23 09:37:00.141063','Nettomiete 01.2025 für 002/9902',2025,1,1,'2025-01-01',1950.00,'1102',8,NULL,'3000','7cefd79130444efb860c13c87bc3184b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (468,'','2025-04-23 08:40:22.133821','2025-04-23 09:37:00.143344','Nebenkosten 01.2025 für 002/9902',2025,1,1,'2025-01-01',250.00,'1102',8,NULL,'2301','04725cd6ea5345f9978f0035aba78cf7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (469,'','2025-04-23 08:40:22.168387','2025-04-23 09:37:00.136266','Nettomiete 12.2024 für 002/9902',2024,12,1,'2024-12-01',1950.00,'1102',8,NULL,'3000','d258f97caa3c4d9185322dfe449a62cb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (470,'','2025-04-23 08:40:22.197036','2025-04-23 09:37:00.138529','Nebenkosten 12.2024 für 002/9902',2024,12,1,'2024-12-01',250.00,'1102',8,NULL,'2301','590f08e06dfa443f9ba883fbb57bc270','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (471,'','2025-04-23 08:40:22.234273','2025-04-23 09:37:00.131833','Nettomiete 11.2024 für 002/9902',2024,11,1,'2024-11-01',1950.00,'1102',8,NULL,'3000','0ee178c9cae94766879da17d07c89ec8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (472,'','2025-04-23 08:40:22.264052','2025-04-23 09:37:00.134088','Nebenkosten 11.2024 für 002/9902',2024,11,1,'2024-11-01',250.00,'1102',8,NULL,'2301','445457bc2a9c4f5db8a9c5e369264b1e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (473,'','2025-04-23 08:40:22.305935','2025-04-23 08:45:54.269563','Nettomiete 03.2025 für 101/9903',2025,3,1,'2025-03-01',6690.00,'1102',9,NULL,'3000','6ee361e6b39149b58b0ea47380a1d66b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (474,'','2025-04-23 08:40:22.344805','2025-04-23 08:45:54.271530','Nebenkosten 03.2025 für 101/9903',2025,3,1,'2025-03-01',635.00,'1102',9,NULL,'2301','14fa4b80cfe842e48e21c3c0fa435ad7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (475,'','2025-04-23 08:40:22.384342','2025-04-23 08:45:54.265633','Nettomiete 02.2025 für 101/9903',2025,2,1,'2025-02-01',6690.00,'1102',9,NULL,'3000','c2e192094c01467cb4a5789eddfcc3db','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (476,'','2025-04-23 08:40:22.412942','2025-04-23 08:45:54.267632','Nebenkosten 02.2025 für 101/9903',2025,2,1,'2025-02-01',635.00,'1102',9,NULL,'2301','9a6bf2b09f5949288472a5ba5d21a51f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (477,'','2025-04-23 08:40:22.446580','2025-04-23 08:45:54.261805','Nettomiete 01.2025 für 101/9903',2025,1,1,'2025-01-01',6690.00,'1102',9,NULL,'3000','7057e1f21c324a64b410c131cda494c9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (478,'','2025-04-23 08:40:22.476725','2025-04-23 08:45:54.263694','Nebenkosten 01.2025 für 101/9903',2025,1,1,'2025-01-01',635.00,'1102',9,NULL,'2301','f1dbcac25f0747cab210e0ed897a890f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (479,'','2025-04-23 08:40:22.509499','2025-04-23 08:45:54.257699','Nettomiete 12.2024 für 101/9903',2024,12,1,'2024-12-01',6690.00,'1102',9,NULL,'3000','57ea73d89eeb42b2aebf07f81d394e6c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (480,'','2025-04-23 08:40:22.539526','2025-04-23 08:45:54.259825','Nebenkosten 12.2024 für 101/9903',2024,12,1,'2024-12-01',635.00,'1102',9,NULL,'2301','305446acf7a34820bff525059f40e3b3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (481,'','2025-04-23 08:40:22.574452','2025-04-23 08:45:54.253544','Nettomiete 11.2024 für 101/9903',2024,11,1,'2024-11-01',6690.00,'1102',9,NULL,'3000','f3f6d94479a9425e875d4abb4053031a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (482,'','2025-04-23 08:40:22.603108','2025-04-23 08:45:54.255644','Nebenkosten 11.2024 für 101/9903',2024,11,1,'2024-11-01',635.00,'1102',9,NULL,'2301','fd44b76978fc4675b9c9f6ce407dc0bd','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (483,'','2025-04-23 08:40:22.639394','2025-04-23 08:42:37.975936','Nettomiete 03.2025 für 201/9904',2025,3,1,'2025-03-01',768.00,'1102',10,NULL,'3000','495483f9d65b4f5b837d5c54dd57712d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (484,'','2025-04-23 08:40:22.668103','2025-04-23 08:42:37.978953','Nebenkosten 03.2025 für 201/9904',2025,3,1,'2025-03-01',82.00,'1102',10,NULL,'2301','8448a435cd314052afd795ede491a931','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (485,'','2025-04-23 08:40:22.702462','2025-04-23 08:42:37.971046','Nettomiete 02.2025 für 201/9904',2025,2,1,'2025-02-01',768.00,'1102',10,NULL,'3000','a5d3ab676e754d0f8677adeb0ad6a956','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (486,'','2025-04-23 08:40:22.730626','2025-04-23 08:42:37.973543','Nebenkosten 02.2025 für 201/9904',2025,2,1,'2025-02-01',82.00,'1102',10,NULL,'2301','4294b9e40f1f44bf85adf7db3afdc9b6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (487,'','2025-04-23 08:40:22.767983','2025-04-23 08:42:37.965724','Nettomiete 01.2025 für 201/9904',2025,1,1,'2025-01-01',768.00,'1102',10,NULL,'3000','63a245f52f664f5a9a5ac63feb7a3e5a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (488,'','2025-04-23 08:40:22.805971','2025-04-23 08:42:37.968228','Nebenkosten 01.2025 für 201/9904',2025,1,1,'2025-01-01',82.00,'1102',10,NULL,'2301','2fd5b6371cca4beaaf60b9cdb1ec84e6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (489,'','2025-04-23 08:40:22.846989','2025-04-23 08:42:37.960132','Nettomiete 12.2024 für 201/9904',2024,12,1,'2024-12-01',768.00,'1102',10,NULL,'3000','09ff007ec5fa4b199a53c90f45e86a46','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (490,'','2025-04-23 08:40:22.878223','2025-04-23 08:42:37.963006','Nebenkosten 12.2024 für 201/9904',2024,12,1,'2024-12-01',82.00,'1102',10,NULL,'2301','6b6dd9ef573c435d846b1f6efb68471e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (491,'','2025-04-23 08:40:22.916274','2025-04-23 08:42:37.954916','Nettomiete 11.2024 für 201/9904',2024,11,1,'2024-11-01',768.00,'1102',10,NULL,'3000','96af52fb7a444f678fa4f6fae6a32c26','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (492,'','2025-04-23 08:40:22.943367','2025-04-23 08:42:37.957279','Nebenkosten 11.2024 für 201/9904',2024,11,1,'2024-11-01',82.00,'1102',10,NULL,'2301','05b8681d44294ddf80ff711aa2c7d071','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (493,'','2025-04-23 08:40:22.976254','2025-04-23 08:44:57.317002','Nettomiete 03.2025 für 202/9905',2025,3,1,'2025-03-01',1125.00,'1102',11,NULL,'3000','b4bc4532460f41178eda30a65f7505e4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (494,'','2025-04-23 08:40:23.003890','2025-04-23 08:44:57.319233','Nebenkosten 03.2025 für 202/9905',2025,3,1,'2025-03-01',195.00,'1102',11,NULL,'2301','02564b4687e94a12b6b49d5105bf5d93','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (495,'','2025-04-23 08:40:23.037013','2025-04-23 08:44:57.312891','Nettomiete 02.2025 für 202/9905',2025,2,1,'2025-02-01',1125.00,'1102',11,NULL,'3000','58fb83d9a8b7426491b9a492f4fa10af','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (496,'','2025-04-23 08:40:23.065327','2025-04-23 08:44:57.315009','Nebenkosten 02.2025 für 202/9905',2025,2,1,'2025-02-01',195.00,'1102',11,NULL,'2301','38176a31f51442798d9a1f73d1c0a208','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (497,'','2025-04-23 08:40:23.098835','2025-04-23 08:44:57.307672','Nettomiete 01.2025 für 202/9905',2025,1,1,'2025-01-01',1125.00,'1102',11,NULL,'3000','7e5029cafce3439d982ac147f82b35f7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (498,'','2025-04-23 08:40:23.126335','2025-04-23 08:44:57.310624','Nebenkosten 01.2025 für 202/9905',2025,1,1,'2025-01-01',195.00,'1102',11,NULL,'2301','ce0c1834a1524cb6ae7b948ec74009b2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (499,'','2025-04-23 08:40:23.160167','2025-04-23 08:44:57.303681','Nettomiete 12.2024 für 202/9905',2024,12,1,'2024-12-01',1125.00,'1102',11,NULL,'3000','8c0db00674c34ab9a9f361744ac9bdf7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (500,'','2025-04-23 08:40:23.191250','2025-04-23 08:44:57.305722','Nebenkosten 12.2024 für 202/9905',2024,12,1,'2024-12-01',195.00,'1102',11,NULL,'2301','3ca009ea572c42658b6c7193d0a8618f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (501,'','2025-04-23 08:40:23.225336','2025-04-23 08:44:57.299343','Nettomiete 11.2024 für 202/9905',2024,11,1,'2024-11-01',1125.00,'1102',11,NULL,'3000','b89343fb83ab4030bd83dea810006b2e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (502,'','2025-04-23 08:40:23.257535','2025-04-23 08:44:57.301734','Nebenkosten 11.2024 für 202/9905',2024,11,1,'2024-11-01',195.00,'1102',11,NULL,'2301','89f7eff54ae541159bb69bbd4916c7a9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (503,'','2025-04-23 08:40:23.291270','2025-04-23 08:44:57.353614','Nettomiete 03.2025 für 203',2025,3,1,'2025-03-01',445.00,'1102',12,NULL,'3000','eaf77b7e8dc24076bff887eef36dc62b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (504,'','2025-04-23 08:40:23.317797','2025-04-23 08:44:57.355703','Nebenkosten 03.2025 für 203',2025,3,1,'2025-03-01',55.00,'1102',12,NULL,'2301','67482ecb11f34640b490a2a8a3ee494e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (505,'','2025-04-23 08:40:23.354428','2025-04-23 08:44:57.349831','Nettomiete 02.2025 für 203',2025,2,1,'2025-02-01',445.00,'1102',12,NULL,'3000','de4f0cf042364bf4a9ba379386eddc91','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (506,'','2025-04-23 08:40:23.384453','2025-04-23 08:44:57.351774','Nebenkosten 02.2025 für 203',2025,2,1,'2025-02-01',55.00,'1102',12,NULL,'2301','ab77aa36e97644768fd1ef87212f61e7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (507,'','2025-04-23 08:40:23.422415','2025-04-23 08:44:57.345800','Nettomiete 01.2025 für 203',2025,1,1,'2025-01-01',445.00,'1102',12,NULL,'3000','fbca375635564a8d99c2ac010c8418b5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (508,'','2025-04-23 08:40:23.452489','2025-04-23 08:44:57.347794','Nebenkosten 01.2025 für 203',2025,1,1,'2025-01-01',55.00,'1102',12,NULL,'2301','fae458df49a443608ede281e7cc2a19f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (509,'','2025-04-23 08:40:23.484828','2025-04-23 08:44:57.341661','Nettomiete 12.2024 für 203',2024,12,1,'2024-12-01',445.00,'1102',12,NULL,'3000','b4d3344fa6234a44a8ea90331910fd6a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (510,'','2025-04-23 08:40:23.512288','2025-04-23 08:44:57.343739','Nebenkosten 12.2024 für 203',2024,12,1,'2024-12-01',55.00,'1102',12,NULL,'2301','856d26efd745416685b98935b6b5e32c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (511,'','2025-04-23 08:40:23.544006','2025-04-23 08:44:57.339563','Nettomiete 11.2024 für 203',2024,11,1,'2024-11-01',445.00,'1102',12,NULL,'3000','b2b6702ab56642dc9d214e98faebe2ec','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (512,'','2025-04-23 08:40:23.574497','2025-04-23 08:44:57.336978','Nebenkosten 11.2024 für 203',2024,11,1,'2024-11-01',55.00,'1102',12,NULL,'2301','1edad80d9754406d8d3b863b12c95f66','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (513,'','2025-04-23 08:40:23.615198','2025-04-23 08:44:30.395595','Nettomiete 03.2025 für 001/9901',2025,3,1,'2025-03-01',1610.00,'1102',13,NULL,'3000','9a0d22d24ada42bca69dce4424365c32','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (514,'','2025-04-23 08:40:23.644213','2025-04-23 08:44:30.397608','Nebenkosten 03.2025 für 001/9901',2025,3,1,'2025-03-01',180.00,'1102',13,NULL,'2301','0dcc6617ede44409a0d0d02b144f8ec7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (515,'','2025-04-23 08:40:23.678145','2025-04-23 08:44:30.391530','Nettomiete 02.2025 für 001/9901',2025,2,1,'2025-02-01',1610.00,'1102',13,NULL,'3000','2087ab2a3917445f9481ca38c0a8fde2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (516,'','2025-04-23 08:40:23.711335','2025-04-23 08:44:30.393745','Nebenkosten 02.2025 für 001/9901',2025,2,1,'2025-02-01',180.00,'1102',13,NULL,'2301','23f5ca7349ec4249b95053a12f4786a0','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (517,'','2025-04-23 08:40:23.747638','2025-04-23 08:44:30.387509','Nettomiete 01.2025 für 001/9901',2025,1,1,'2025-01-01',1610.00,'1102',13,NULL,'3000','d7e8164078974957b7b4fe7a192c0f89','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (518,'','2025-04-23 08:40:23.779407','2025-04-23 08:44:30.389620','Nebenkosten 01.2025 für 001/9901',2025,1,1,'2025-01-01',180.00,'1102',13,NULL,'2301','d96d7c7ad2844f38b844aad2ba77c0df','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (519,'','2025-04-23 08:40:23.815628','2025-04-23 08:44:30.383324','Nettomiete 12.2024 für 001/9901',2024,12,1,'2024-12-01',1610.00,'1102',13,NULL,'3000','e4c665e323174ec2b6999b1a4f91697e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (520,'','2025-04-23 08:40:23.847185','2025-04-23 08:44:30.385425','Nebenkosten 12.2024 für 001/9901',2024,12,1,'2024-12-01',180.00,'1102',13,NULL,'2301','0334c633ad60409dab8ed7bd14bc14a5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (521,'','2025-04-23 08:40:23.882681','2025-04-23 08:44:30.379074','Nettomiete 11.2024 für 001/9901',2024,11,1,'2024-11-01',1610.00,'1102',13,NULL,'3000','98a906b405cc493faad5b3af61e9a271','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (522,'','2025-04-23 08:40:23.915508','2025-04-23 08:44:30.381353','Nebenkosten 11.2024 für 001/9901',2024,11,1,'2024-11-01',180.00,'1102',13,NULL,'2301','afca5cebeb194c11a448d7f306e4695e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (523,'','2025-04-23 08:40:23.955853','2025-04-23 08:44:57.375805','Nettomiete 03.2025 für PP-01',2025,3,1,'2025-03-01',120.00,'1102',14,NULL,'3002','af7da98552bf4acd8edf83a054897feb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (524,'','2025-04-23 08:40:23.991381','2025-04-23 08:44:57.373644','Nettomiete 02.2025 für PP-01',2025,2,1,'2025-02-01',120.00,'1102',14,NULL,'3002','1a996776861344098b886811942e94db','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (525,'','2025-04-23 08:40:24.027893','2025-04-23 08:44:57.371657','Nettomiete 01.2025 für PP-01',2025,1,1,'2025-01-01',120.00,'1102',14,NULL,'3002','42ce5aa12d5148759417338abf42c6c6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (526,'','2025-04-23 08:40:24.063340','2025-04-23 08:44:57.369676','Nettomiete 12.2024 für PP-01',2024,12,1,'2024-12-01',120.00,'1102',14,NULL,'3002','6e4a431e74b548c7bef815feaddff325','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (527,'','2025-04-23 08:40:24.103443','2025-04-23 08:44:57.367527','Nettomiete 11.2024 für PP-01',2024,11,1,'2024-11-01',120.00,'1102',14,NULL,'3002','ec3688e0d1484e80acea41d19bbae8fe','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (528,'','2025-04-23 08:40:24.140238','2025-04-23 08:44:57.397907','Nettomiete 03.2025 für PP-01',2025,3,1,'2025-03-01',120.00,'1102',15,NULL,'3002','9a3dad3dc9884c778b211a854f4ec0ec','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (529,'','2025-04-23 08:40:24.175609','2025-04-23 08:44:57.396093','Nettomiete 02.2025 für PP-01',2025,2,1,'2025-02-01',120.00,'1102',15,NULL,'3002','621dc5b787c24310a9988b6a6ad9c227','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (530,'','2025-04-23 08:40:24.211782','2025-04-23 08:44:57.393921','Nettomiete 01.2025 für PP-01',2025,1,1,'2025-01-01',120.00,'1102',15,NULL,'3002','bf2d0c86b4db48a3a0a3ea7747e643f1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (531,'','2025-04-23 08:40:24.256146','2025-04-23 08:44:57.391948','Nettomiete 12.2024 für PP-01',2024,12,1,'2024-12-01',120.00,'1102',15,NULL,'3002','969102188ab94c17950695eaf30866b5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (532,'','2025-04-23 08:40:24.296726','2025-04-23 08:44:57.389834','Nettomiete 11.2024 für PP-01',2024,11,1,'2024-11-01',120.00,'1102',15,NULL,'3002','d5bec8d04c8a4abc85d3585190bd7e15','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (533,'','2025-04-23 08:40:24.334125','2025-04-23 08:44:56.828829','Nettomiete 03.2025 für 002/9902',2025,3,1,'2025-03-01',1950.00,'1102',1,NULL,'3000','5eea00b6fdb640e9b664a28fac3823cf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (534,'','2025-04-23 08:40:24.361373','2025-04-23 08:44:56.831366','Nebenkosten 03.2025 für 002/9902',2025,3,1,'2025-03-01',250.00,'1102',1,NULL,'2301','e64460554e04465b87915a77a92396bc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (535,'','2025-04-23 08:40:24.393918','2025-04-23 08:44:56.821346','Nettomiete 02.2025 für 002/9902',2025,2,1,'2025-02-01',1950.00,'1102',1,NULL,'3000','4a61e05087c04371b26deefb300c8f40','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (536,'','2025-04-23 08:40:24.420812','2025-04-23 08:44:56.826467','Nebenkosten 02.2025 für 002/9902',2025,2,1,'2025-02-01',250.00,'1102',1,NULL,'2301','61f8635810ef415cbc2cfd5df7020d65','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (537,'','2025-04-23 08:40:24.454458','2025-04-23 08:44:56.816444','Nettomiete 01.2025 für 002/9902',2025,1,1,'2025-01-01',1950.00,'1102',1,NULL,'3000','0cfd672d800540f5bd6ce1406ee735c5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (538,'','2025-04-23 08:40:24.482602','2025-04-23 08:44:56.819163','Nebenkosten 01.2025 für 002/9902',2025,1,1,'2025-01-01',250.00,'1102',1,NULL,'2301','e69b1b354bdf4969a5392f316a12e75b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (539,'','2025-04-23 08:40:24.517563','2025-04-23 08:44:56.811811','Nettomiete 12.2024 für 002/9902',2024,12,1,'2024-12-01',1950.00,'1102',1,NULL,'3000','1b299871538e4993aaa342a52fb0ee57','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (540,'','2025-04-23 08:40:24.547327','2025-04-23 08:44:56.814031','Nebenkosten 12.2024 für 002/9902',2024,12,1,'2024-12-01',250.00,'1102',1,NULL,'2301','202a1aeae537446fb7c40aff80d64e6a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (541,'','2025-04-23 08:40:24.581147','2025-04-23 08:44:56.807257','Nettomiete 11.2024 für 002/9902',2024,11,1,'2024-11-01',1950.00,'1102',1,NULL,'3000','3873415cea2d4e5cbf05fa3be3941469','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (542,'','2025-04-23 08:40:24.608978','2025-04-23 08:44:56.809760','Nebenkosten 11.2024 für 002/9902',2024,11,1,'2024-11-01',250.00,'1102',1,NULL,'2301','895b815baddb47ecba653e048995cbc2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (543,'','2025-04-23 08:40:24.647153','2025-04-23 08:44:56.883831','Nettomiete 03.2025 für 001/9901/9906',2025,3,1,'2025-03-01',1759.00,'1102',3,NULL,'3001','b63c7fb0e1b9418db113141d4b6595a8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (544,'','2025-04-23 08:40:24.673593','2025-04-23 08:44:56.886496','Nebenkosten 03.2025 für 001/9901/9906',2025,3,1,'2025-03-01',208.00,'1102',3,NULL,'2301','17152a3ed06d4cffa948a8128294cebe','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (545,'','2025-04-23 08:40:24.700640','2025-04-23 08:44:56.888663','Strompauschale 03.2025 für 001/9901/9906',2025,3,1,'2025-03-01',5.00,'1102',3,NULL,'2302','73dc9b1fe7d24078bc928fb74ccab417','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (546,'','2025-04-23 08:40:24.736307','2025-04-23 08:44:56.876245','Nettomiete 02.2025 für 001/9901/9906',2025,2,1,'2025-02-01',1759.00,'1102',3,NULL,'3001','b3720f5944b541ca990d1bbab54a2bed','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (547,'','2025-04-23 08:40:24.763379','2025-04-23 08:44:56.878883','Nebenkosten 02.2025 für 001/9901/9906',2025,2,1,'2025-02-01',208.00,'1102',3,NULL,'2301','ddba02065e53414fbeddaadc71017024','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (548,'','2025-04-23 08:40:24.790441','2025-04-23 08:44:56.881533','Strompauschale 02.2025 für 001/9901/9906',2025,2,1,'2025-02-01',5.00,'1102',3,NULL,'2302','bd34500a3769439e848e1fb87200fee9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (549,'','2025-04-23 08:40:24.826688','2025-04-23 08:44:56.869119','Nettomiete 01.2025 für 001/9901/9906',2025,1,1,'2025-01-01',1759.00,'1102',3,NULL,'3001','75e89ea29e5b4844b0e32f0bdf89980c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (550,'','2025-04-23 08:40:24.857151','2025-04-23 08:44:56.871437','Nebenkosten 01.2025 für 001/9901/9906',2025,1,1,'2025-01-01',208.00,'1102',3,NULL,'2301','1a9f7f5bf26f4662bf97994b882bbe43','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (551,'','2025-04-23 08:40:24.885241','2025-04-23 08:44:56.873852','Strompauschale 01.2025 für 001/9901/9906',2025,1,1,'2025-01-01',5.00,'1102',3,NULL,'2302','773db0a082464ad996d2c3b6fe1c9ab7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (552,'','2025-04-23 08:40:24.920874','2025-04-23 08:44:56.860997','Nettomiete 12.2024 für 001/9901/9906',2024,12,1,'2024-12-01',1759.00,'1102',3,NULL,'3001','6749cf26ea30460f8a3107628cc647e7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (553,'','2025-04-23 08:40:24.947117','2025-04-23 08:44:56.863566','Nebenkosten 12.2024 für 001/9901/9906',2024,12,1,'2024-12-01',208.00,'1102',3,NULL,'2301','ac6bb4a5afa44002be85a3ad31479493','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (554,'','2025-04-23 08:40:24.973790','2025-04-23 08:44:56.866628','Strompauschale 12.2024 für 001/9901/9906',2024,12,1,'2024-12-01',5.00,'1102',3,NULL,'2302','64a16b91d8aa4a3d9774a0887486ecfa','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (555,'','2025-04-23 08:40:25.010000','2025-04-23 08:44:56.853665','Nettomiete 11.2024 für 001/9901/9906',2024,11,1,'2024-11-01',1759.00,'1102',3,NULL,'3001','91b507a21d1145fea1db2b5639d670b9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (556,'','2025-04-23 08:40:25.036938','2025-04-23 08:44:56.855750','Nebenkosten 11.2024 für 001/9901/9906',2024,11,1,'2024-11-01',208.00,'1102',3,NULL,'2301','ac9f88e68a7d4a02beeec034f6a84eaf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (557,'','2025-04-23 08:40:25.063381','2025-04-23 08:44:56.858693','Strompauschale 11.2024 für 001/9901/9906',2024,11,1,'2024-11-01',5.00,'1102',3,NULL,'2302','922f14a3035849e0abce3857c6508bcf','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (558,'','2025-04-23 08:40:25.095750','2025-04-23 08:44:56.923645','Nettomiete 03.2025 für 101/9903',2025,3,1,'2025-03-01',6690.00,'1102',4,NULL,'3000','2622c74522b84ce7a3f904f777dcaec6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (559,'','2025-04-23 08:40:25.120775','2025-04-23 08:44:56.926484','Nebenkosten 03.2025 für 101/9903',2025,3,1,'2025-03-01',635.00,'1102',4,NULL,'2301','e28d67b2f6b84011a31c4ab892baaef6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (560,'','2025-04-23 08:40:25.150209','2025-04-23 08:44:56.919458','Nettomiete 02.2025 für 101/9903',2025,2,1,'2025-02-01',6690.00,'1102',4,NULL,'3000','16c307b057ec4ab4a6d8f1f60ddfe1b7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (561,'','2025-04-23 08:40:25.173391','2025-04-23 08:44:56.921659','Nebenkosten 02.2025 für 101/9903',2025,2,1,'2025-02-01',635.00,'1102',4,NULL,'2301','ca61d19f08104a24ae758980f19eba48','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (562,'','2025-04-23 08:40:25.202458','2025-04-23 08:44:56.915010','Nettomiete 01.2025 für 101/9903',2025,1,1,'2025-01-01',6690.00,'1102',4,NULL,'3000','b18dbafa04e5456e89c81201e62a3352','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (563,'','2025-04-23 08:40:25.224803','2025-04-23 08:44:56.917040','Nebenkosten 01.2025 für 101/9903',2025,1,1,'2025-01-01',635.00,'1102',4,NULL,'2301','bd0394a672a54f89beda24bb990c332e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (564,'','2025-04-23 08:40:25.253594','2025-04-23 08:44:56.909057','Nettomiete 12.2024 für 101/9903',2024,12,1,'2024-12-01',6690.00,'1102',4,NULL,'3000','8729c7e1b31f4358b76eb77329e53f27','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (565,'','2025-04-23 08:40:25.277770','2025-04-23 08:44:56.911918','Nebenkosten 12.2024 für 101/9903',2024,12,1,'2024-12-01',635.00,'1102',4,NULL,'2301','fef6bb3b2aa14d9c9609399c508eeff8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (566,'','2025-04-23 08:40:25.304843','2025-04-23 08:44:56.904749','Nettomiete 11.2024 für 101/9903',2024,11,1,'2024-11-01',6690.00,'1102',4,NULL,'3000','ff6bda16e1bd4608b85304a9f821cf16','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (567,'','2025-04-23 08:40:25.326016','2025-04-23 08:44:56.906867','Nebenkosten 11.2024 für 101/9903',2024,11,1,'2024-11-01',635.00,'1102',4,NULL,'2301','44c8dec2ab554728ab0ceb74ece781ef','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (568,'','2025-04-23 08:40:25.359144','2025-04-23 08:44:57.163704','Nettomiete 03.2025 für 201/9904',2025,3,1,'2025-03-01',768.00,'1102',5,NULL,'3000','0c2a855efdc54e7d83df115f6fec9db2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (569,'','2025-04-23 08:40:25.385790','2025-04-23 08:44:57.166565','Nebenkosten 03.2025 für 201/9904',2025,3,1,'2025-03-01',82.00,'1102',5,NULL,'2301','70fe3bf04f0a41aab4ae5006fdaa07de','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (570,'','2025-04-23 08:40:25.417028','2025-04-23 08:44:57.159250','Nettomiete 02.2025 für 201/9904',2025,2,1,'2025-02-01',768.00,'1102',5,NULL,'3000','88c34b3e2b9c47c0be3ff01c4416490c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (571,'','2025-04-23 08:40:25.448245','2025-04-23 08:44:57.161259','Nebenkosten 02.2025 für 201/9904',2025,2,1,'2025-02-01',82.00,'1102',5,NULL,'2301','765ca0d0ee324611a2b46ecdab923d73','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (572,'','2025-04-23 08:40:25.622379','2025-04-23 08:44:57.155072','Nettomiete 01.2025 für 201/9904',2025,1,1,'2025-01-01',768.00,'1102',5,NULL,'3000','dd3e37e882334f15ba559f11550b4a70','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (573,'','2025-04-23 08:40:25.650106','2025-04-23 08:44:57.157216','Nebenkosten 01.2025 für 201/9904',2025,1,1,'2025-01-01',82.00,'1102',5,NULL,'2301','4f61a5f37f294543a6698e9e505c6813','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (574,'','2025-04-23 08:40:25.682088','2025-04-23 08:44:57.150575','Nettomiete 12.2024 für 201/9904',2024,12,1,'2024-12-01',768.00,'1102',5,NULL,'3000','012260b1463d48cb9c39dd8295b65e5e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (575,'','2025-04-23 08:40:25.712039','2025-04-23 08:44:57.152851','Nebenkosten 12.2024 für 201/9904',2024,12,1,'2024-12-01',82.00,'1102',5,NULL,'2301','30585c6eb90240a1988d60b59a94af49','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (576,'','2025-04-23 08:40:25.748426','2025-04-23 08:44:57.145745','Nettomiete 11.2024 für 201/9904',2024,11,1,'2024-11-01',768.00,'1102',5,NULL,'3000','f5d65275147b4a069efedb3488d0d71a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (577,'','2025-04-23 08:40:25.775663','2025-04-23 08:44:57.147947','Nebenkosten 11.2024 für 201/9904',2024,11,1,'2024-11-01',82.00,'1102',5,NULL,'2301','29fffc8fb5bf4db189efe3145542b39b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (578,'','2025-04-23 08:40:25.809661','2025-04-23 08:44:57.199770','Nettomiete 03.2025 für 202',2025,3,1,'2025-03-01',1125.00,'1102',6,NULL,'3000','298f766f930a4ecd9033946615604cf8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (579,'','2025-04-23 08:40:25.836415','2025-04-23 08:44:57.201586','Nebenkosten 03.2025 für 202',2025,3,1,'2025-03-01',195.00,'1102',6,NULL,'2301','accad48259b746b080a00f36468e2acc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (580,'','2025-04-23 08:40:25.867861','2025-04-23 08:44:57.195832','Nettomiete 02.2025 für 202',2025,2,1,'2025-02-01',1125.00,'1102',6,NULL,'3000','3001d08144d841109d4bc7878e86e45a','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (581,'','2025-04-23 08:40:25.897104','2025-04-23 08:44:57.197840','Nebenkosten 02.2025 für 202',2025,2,1,'2025-02-01',195.00,'1102',6,NULL,'2301','b06fd7eb12784db68938bb182bfcccf3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (582,'','2025-04-23 08:40:25.930048','2025-04-23 08:44:57.191962','Nettomiete 01.2025 für 202',2025,1,1,'2025-01-01',1125.00,'1102',6,NULL,'3000','3092434dc5ea46d4b66665bf6b94fce3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (583,'','2025-04-23 08:40:25.959803','2025-04-23 08:44:57.193902','Nebenkosten 01.2025 für 202',2025,1,1,'2025-01-01',195.00,'1102',6,NULL,'2301','9562f80198ab4934bad858a36522ab27','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (584,'','2025-04-23 08:40:25.991177','2025-04-23 08:44:57.187897','Nettomiete 12.2024 für 202',2024,12,1,'2024-12-01',1125.00,'1102',6,NULL,'3000','fb053ba85ca3477b8999f01fb5f9ae19','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (585,'','2025-04-23 08:40:26.018825','2025-04-23 08:44:57.190082','Nebenkosten 12.2024 für 202',2024,12,1,'2024-12-01',195.00,'1102',6,NULL,'2301','7be9c7f072674775bea246fc0feed572','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (586,'','2025-04-23 08:40:26.050806','2025-04-23 08:44:57.183796','Nettomiete 11.2024 für 202',2024,11,1,'2024-11-01',1125.00,'1102',6,NULL,'3000','afa845ef4f23436983898fc666dea3c4','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (587,'','2025-04-23 08:40:26.082149','2025-04-23 08:44:57.185809','Nebenkosten 11.2024 für 202',2024,11,1,'2024-11-01',195.00,'1102',6,NULL,'2301','4d6d2b95a7c8409f973636b610aee513','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (588,'','2025-04-23 08:40:26.120132','2025-04-23 08:44:57.251903','Nettomiete 03.2025 für 003/9906',2025,3,1,'2025-03-01',1265.00,'1102',7,NULL,'3001','97bdbb69650742988ba09957dc4152e2','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (589,'','2025-04-23 08:40:26.147137','2025-04-23 08:44:57.253660','Nebenkosten 03.2025 für 003/9906',2025,3,1,'2025-03-01',187.00,'1102',7,NULL,'2301','921d3a0723574e14bcd98526fb5f7e0d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (590,'','2025-04-23 08:40:26.174958','2025-04-23 08:44:57.255487','Strompauschale 03.2025 für 003/9906',2025,3,1,'2025-03-01',5.00,'1102',7,NULL,'2302','c8bf3403863f45909eab34202a6a55e1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (591,'','2025-04-23 08:40:26.210461','2025-04-23 08:44:57.246222','Nettomiete 02.2025 für 003/9906',2025,2,1,'2025-02-01',1265.00,'1102',7,NULL,'3001','83b7646eeb8944bea4f5dec2aa5cd5f8','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (592,'','2025-04-23 08:40:26.238335','2025-04-23 08:44:57.248121','Nebenkosten 02.2025 für 003/9906',2025,2,1,'2025-02-01',187.00,'1102',7,NULL,'2301','992e5a7c9c30415f970a8f74b8c7ec2f','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (593,'','2025-04-23 08:40:26.266918','2025-04-23 08:44:57.250079','Strompauschale 02.2025 für 003/9906',2025,2,1,'2025-02-01',5.00,'1102',7,NULL,'2302','ece44ff4d97b475ebf552b6a5cd03e03','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (594,'','2025-04-23 08:40:26.302760','2025-04-23 08:44:57.239802','Nettomiete 01.2025 für 003/9906',2025,1,1,'2025-01-01',1265.00,'1102',7,NULL,'3001','d403875dca82485bbcd9cb89378c79c6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (595,'','2025-04-23 08:40:26.329887','2025-04-23 08:44:57.241960','Nebenkosten 01.2025 für 003/9906',2025,1,1,'2025-01-01',187.00,'1102',7,NULL,'2301','44b7f879b1684a8a90ea0dc03ed3a4eb','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (596,'','2025-04-23 08:40:26.358808','2025-04-23 08:44:57.243906','Strompauschale 01.2025 für 003/9906',2025,1,1,'2025-01-01',5.00,'1102',7,NULL,'2302','f55bdb76d95d4435a22529487acc8754','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (597,'','2025-04-23 08:40:26.395650','2025-04-23 08:44:57.231679','Nettomiete 12.2024 für 003/9906',2024,12,1,'2024-12-01',1265.00,'1102',7,NULL,'3001','89ed1f98b8d34679b430c314fa08d526','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (598,'','2025-04-23 08:40:26.422397','2025-04-23 08:44:57.234270','Nebenkosten 12.2024 für 003/9906',2024,12,1,'2024-12-01',187.00,'1102',7,NULL,'2301','54b1ba7acac24e0bb07689be2c57bf25','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (599,'','2025-04-23 08:40:26.448839','2025-04-23 08:44:57.237320','Strompauschale 12.2024 für 003/9906',2024,12,1,'2024-12-01',5.00,'1102',7,NULL,'2302','6bd90778bce64918a9ffe8c5c2579a73','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (600,'','2025-04-23 08:40:26.483477','2025-04-23 08:44:57.225316','Nettomiete 11.2024 für 003/9906',2024,11,1,'2024-11-01',1265.00,'1102',7,NULL,'3001','521fd20f662048ba8b434bb13cc3ee11','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (601,'','2025-04-23 08:40:26.513238','2025-04-23 08:44:57.227373','Nebenkosten 11.2024 für 003/9906',2024,11,1,'2024-11-01',187.00,'1102',7,NULL,'2301','03ff32c13e1144a2b00350d43b83b9fe','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (602,'','2025-04-23 08:40:26.542302','2025-04-23 08:44:57.229714','Strompauschale 11.2024 für 003/9906',2024,11,1,'2024-11-01',5.00,'1102',7,NULL,'2302','cd208d61381f419cbd6fa4620150ad33','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (603,'','2025-04-23 08:41:57.610976','2025-04-23 08:44:57.009546','Einzahlung Mietzins wiederkehrend 201/9904',NULL,NULL,1,'2025-04-23',28900.00,'1102',5,NULL,'1020.1','383887376e5f4522a4447277ffe2f192','Payment',1,2,'DEMO Einzahlung/Klein, Anna','100000000000000000000500006','_DEMO_100000000000000000000500006_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (604,'','2025-04-23 08:41:57.649392','2025-04-23 08:44:30.360417','Einzahlung Mietzins wiederkehrend 001/9901',NULL,NULL,1,'2025-04-23',14320.00,'1102',13,NULL,'1020.1','b2db2018a4554efd9ca7df3af5634fd3','Payment',1,2,'DEMO Einzahlung/Jäger, Marta','100000000000000000001300000','_DEMO_100000000000000000001300000_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (605,'','2025-04-23 08:41:57.682248','2025-04-23 08:42:37.952083','Einzahlung Mietzins wiederkehrend 201/9904',NULL,NULL,1,'2025-04-23',4250.00,'1102',10,NULL,'1020.1','3a4db56122df4e1e9b03361bfa267742','Payment',1,2,'DEMO Einzahlung/Deshar, Fatma','100000000000000000001000006','_DEMO_100000000000000000001000006_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (606,'','2025-04-23 08:41:57.716397','2025-04-23 08:44:57.334616','Einzahlung Mietzins wiederkehrend 203',NULL,NULL,1,'2025-04-23',2500.00,'1102',12,NULL,'1020.1','efae9c7997494edbbbc073741cd7da99','Payment',1,2,'DEMO Einzahlung/Rossi, Mario','100000000000000000001200007','_DEMO_100000000000000000001200007_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (607,'','2025-04-23 08:41:57.750533','2025-04-23 08:44:57.386763','Einzahlung Mietzins wiederkehrend PP-01',NULL,NULL,1,'2025-04-23',600.00,'1102',15,NULL,'1020.1','b29ae43cdfc84402954f27d07a02125a','Payment',1,2,'DEMO Einzahlung/Jäger, Marta','100000000000000000001500003','_DEMO_100000000000000000001500003_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (608,'','2025-04-23 08:41:57.788990','2025-04-23 08:44:56.851347','Einzahlung Mietzins wiederkehrend 001/9901/9906',NULL,NULL,1,'2025-04-23',9860.00,'1102',3,NULL,'1020.1','f917e3c5c6e7463f8a2406359d90ec26','Payment',1,2,'DEMO Einzahlung/Muster, Anna','100000000000000000000300004','_DEMO_100000000000000000000300004_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (609,'','2025-04-23 08:41:57.824026','2025-04-23 08:44:57.181479','Einzahlung Mietzins wiederkehrend 202',NULL,NULL,1,'2025-04-23',6600.00,'1102',6,NULL,'1020.1','578ce31e028e4235b3c3c76d62811107','Payment',1,2,'DEMO Einzahlung/Jensen, Hugo','100000000000000000000600001','_DEMO_100000000000000000000600001_20250423104106_',0);
INSERT INTO `geno_invoice` VALUES (612,'','2025-04-23 08:43:39.868123','2025-04-23 08:44:57.296715','Einzahlung Mietzins wiederkehrend 202/9905',NULL,NULL,1,'2025-04-23',6600.00,'1102',11,NULL,'1020.1','3fb21a79fb7c4f04a8f7dab9a707dc83','Payment',1,2,'DEMO Einzahlung/Rossi, Mario','100000000000000000001100001','_DEMO_100000000000000000001100001_20250423104330_',0);
INSERT INTO `geno_invoice` VALUES (613,'','2025-04-23 08:43:39.900264','2025-04-23 08:44:57.365213','Einzahlung Mietzins wiederkehrend PP-01',NULL,NULL,1,'2025-04-23',600.00,'1102',14,NULL,'1020.1','ccc4407ad14c45ee9d22ca572a34ce15','Payment',1,2,'DEMO Einzahlung/Brot GmbH,  ','100000000000000000001400002','_DEMO_100000000000000000001400002_20250423104330_',0);
INSERT INTO `geno_invoice` VALUES (614,'','2025-04-23 08:43:39.936960','2025-04-23 08:44:56.804086','Einzahlung Mietzins wiederkehrend 002/9902',NULL,NULL,1,'2025-04-23',11000.00,'1102',1,NULL,'1020.1','000aac9f3ade4409abb75c2d403ba3e5','Payment',1,2,'DEMO Einzahlung/Dupont, Jean','100000000000000000000100005','_DEMO_100000000000000000000100005_20250423104330_',0);
INSERT INTO `geno_invoice` VALUES (615,'','2025-04-23 08:43:39.969854','2025-04-23 08:44:56.902350','Einzahlung Mietzins wiederkehrend 101/9903',NULL,NULL,1,'2025-04-23',36625.00,'1102',4,NULL,'1020.1','23bc1ed4a6914290b153d44cdd118cab','Payment',1,2,'DEMO Einzahlung/Borg, Folana','100000000000000000000400008','_DEMO_100000000000000000000400008_20250423104330_',0);
INSERT INTO `geno_invoice` VALUES (616,'','2025-04-23 08:43:40.004720','2025-04-23 08:44:57.222832','Einzahlung Mietzins wiederkehrend 003/9906',NULL,NULL,1,'2025-04-23',7285.00,'1102',7,NULL,'1020.1','10810807acd34eeba8350963d7e48e8b','Payment',1,2,'DEMO Einzahlung/Brot GmbH,  ','100000000000000000000700007','_DEMO_100000000000000000000700007_20250423104330_',0);
INSERT INTO `geno_invoice` VALUES (617,'','2025-04-23 08:45:42.358677','2025-04-23 08:45:54.237147','Einzahlung Mietzins wiederkehrend 101/9903',NULL,NULL,1,'2025-04-23',58600.00,'1102',9,NULL,'1020.1','2d3090eddc1b44f684c95f2a2dac45e9','Payment',1,2,'DEMO Einzahlung/Dobler, Rudolf','100000000000000000000900002','_DEMO_100000000000000000000900002_20250423104533_',0);
INSERT INTO `geno_invoice` VALUES (618,'','2025-04-23 09:33:53.966542','2025-04-23 09:37:00.157410','Nettomiete 05.2025 für 002/9902',2025,5,1,'2025-05-01',1950.00,'1102',8,NULL,'3000','1e7df91a43e544d3a103737628e1d76d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (619,'','2025-04-23 09:33:54.003682','2025-04-23 09:37:00.159358','Nebenkosten 05.2025 für 002/9902',2025,5,1,'2025-05-01',250.00,'1102',8,NULL,'2301','78aef362632741b189b1d888b7b10c1e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (620,'','2025-04-23 09:33:54.040598','2025-04-23 09:37:00.153503','Nettomiete 04.2025 für 002/9902',2025,4,1,'2025-04-01',1950.00,'1102',8,NULL,'3000','31cfd1a339b942c4898d89a65c6d5c4d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (621,'','2025-04-23 09:33:54.071977','2025-04-23 09:37:00.155367','Nebenkosten 04.2025 für 002/9902',2025,4,1,'2025-04-01',250.00,'1102',8,NULL,'2301','ebeaec957d56464ab374fa1d0c24880b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (622,'','2025-04-23 09:33:54.111818','2025-04-23 09:33:54.111851','Nettomiete 05.2025 für 101/9903',2025,5,1,'2025-05-01',6690.00,'1102',9,NULL,'3000','e322ce65b8944f58b4a25a05fb09b978','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (623,'','2025-04-23 09:33:54.142826','2025-04-23 09:33:54.142863','Nebenkosten 05.2025 für 101/9903',2025,5,1,'2025-05-01',635.00,'1102',9,NULL,'2301','846541f0b60c48448fad0e4d7411bdac','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (624,'','2025-04-23 09:33:54.182060','2025-04-23 09:33:54.182093','Nettomiete 04.2025 für 101/9903',2025,4,1,'2025-04-01',6690.00,'1102',9,NULL,'3000','a19e804a39eb4b54b4f29bad650d284d','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (625,'','2025-04-23 09:33:54.211740','2025-04-23 09:33:54.211770','Nebenkosten 04.2025 für 101/9903',2025,4,1,'2025-04-01',635.00,'1102',9,NULL,'2301','0e850887e5454982a7672cfa8ed118ad','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (626,'','2025-04-23 09:33:54.251410','2025-04-23 09:37:00.176525','Nettomiete 05.2025 für 201/9904',2025,5,1,'2025-05-01',768.00,'1102',10,NULL,'3000','f7d7442745db4ca9bdfbe9437dc005f9','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (627,'','2025-04-23 09:33:54.281988','2025-04-23 09:37:00.178496','Nebenkosten 05.2025 für 201/9904',2025,5,1,'2025-05-01',82.00,'1102',10,NULL,'2301','ade1067bb466427088b1cc05a4f8f89e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (628,'','2025-04-23 09:33:54.318306','2025-04-23 09:37:00.172334','Nettomiete 04.2025 für 201/9904',2025,4,1,'2025-04-01',768.00,'1102',10,NULL,'3000','9f4ebe6bfe7e481ca2ce9c7c253dbcc1','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (629,'','2025-04-23 09:33:54.350592','2025-04-23 09:37:00.174529','Nebenkosten 04.2025 für 201/9904',2025,4,1,'2025-04-01',82.00,'1102',10,NULL,'2301','e1e6cdf8f97a4aebb821d84a408da95d','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (630,'','2025-04-23 09:33:54.390937','2025-04-23 09:33:54.390971','Nettomiete 05.2025 für 202/9905',2025,5,1,'2025-05-01',1125.00,'1102',11,NULL,'3000','a598a888d1514b909331a18ab28452b6','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (631,'','2025-04-23 09:33:54.423153','2025-04-23 09:33:54.423185','Nebenkosten 05.2025 für 202/9905',2025,5,1,'2025-05-01',195.00,'1102',11,NULL,'2301','374b5a720b1b40729fe372a3fbd54ca3','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (632,'','2025-04-23 09:33:54.456377','2025-04-23 09:33:54.456408','Nettomiete 04.2025 für 202/9905',2025,4,1,'2025-04-01',1125.00,'1102',11,NULL,'3000','a2f90dc161fe4e29a51c1fc57c1fa114','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (633,'','2025-04-23 09:33:54.485091','2025-04-23 09:33:54.485122','Nebenkosten 04.2025 für 202/9905',2025,4,1,'2025-04-01',195.00,'1102',11,NULL,'2301','b5b1e296fef84ce29517e84a23bc0240','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (634,'','2025-04-23 09:33:54.516891','2025-04-23 09:37:00.194894','Nettomiete 05.2025 für 203',2025,5,1,'2025-05-01',445.00,'1102',12,NULL,'3000','7f885c861b4548809f385c66e1f4254c','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (635,'','2025-04-23 09:33:54.553038','2025-04-23 09:37:00.197560','Nebenkosten 05.2025 für 203',2025,5,1,'2025-05-01',55.00,'1102',12,NULL,'2301','12738f7f890a4618ade521466334e105','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (636,'','2025-04-23 09:33:54.587438','2025-04-23 09:37:00.190939','Nettomiete 04.2025 für 203',2025,4,1,'2025-04-01',445.00,'1102',12,NULL,'3000','7f2505dd1f5d4183b7162106dae911dc','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (637,'','2025-04-23 09:33:54.618080','2025-04-23 09:37:00.193022','Nebenkosten 04.2025 für 203',2025,4,1,'2025-04-01',55.00,'1102',12,NULL,'2301','9c179f70810d4146a4f45dcbaeb7fcb3','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (638,'','2025-04-23 09:33:54.657858','2025-04-23 09:33:54.657890','Nettomiete 05.2025 für 001/9901',2025,5,1,'2025-05-01',1610.00,'1102',13,NULL,'3000','331a11bee2894d64ac3fbd412401a784','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (639,'','2025-04-23 09:33:54.688097','2025-04-23 09:33:54.688150','Nebenkosten 05.2025 für 001/9901',2025,5,1,'2025-05-01',180.00,'1102',13,NULL,'2301','4520c0aee67e4e0ab524761da93a6277','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (640,'','2025-04-23 09:33:54.724053','2025-04-23 09:33:54.724084','Nettomiete 04.2025 für 001/9901',2025,4,1,'2025-04-01',1610.00,'1102',13,NULL,'3000','290b6e9be5314f4e80a676bb00d297be','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (641,'','2025-04-23 09:33:54.753422','2025-04-23 09:33:54.753452','Nebenkosten 04.2025 für 001/9901',2025,4,1,'2025-04-01',180.00,'1102',13,NULL,'2301','804741de936c45288246451c4f61565d','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (642,'','2025-04-23 09:33:54.795108','2025-04-23 09:37:00.211286','Nettomiete 05.2025 für PP-01',2025,5,1,'2025-05-01',120.00,'1102',14,NULL,'3002','ea1934fe451f444d8dbd9e014844f990','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (643,'','2025-04-23 09:33:54.835514','2025-04-23 09:37:00.209362','Nettomiete 04.2025 für PP-01',2025,4,1,'2025-04-01',120.00,'1102',14,NULL,'3002','a08fbb3920704eaaa0559cbcc775a5b7','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (644,'','2025-04-23 09:33:54.881669','2025-04-23 09:33:54.881707','Nettomiete 05.2025 für PP-01',2025,5,1,'2025-05-01',120.00,'1102',15,NULL,'3002','86ca24a9d5234ef8ac425b51227272bc','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (645,'','2025-04-23 09:33:54.931505','2025-04-23 09:33:54.931547','Nettomiete 04.2025 für PP-01',2025,4,1,'2025-04-01',120.00,'1102',15,NULL,'3002','e114cbef9bfa4b42bd12d9e60d7b3c96','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (646,'','2025-04-23 09:33:54.976343','2025-04-23 09:37:00.063272','Nettomiete 05.2025 für 002/9902',2025,5,1,'2025-05-01',1950.00,'1102',1,NULL,'3000','60437e697d0b4d7fa99c2157e8a97529','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (647,'','2025-04-23 09:33:55.006264','2025-04-23 09:37:00.065301','Nebenkosten 05.2025 für 002/9902',2025,5,1,'2025-05-01',250.00,'1102',1,NULL,'2301','44b76a1d76984de4b4e5ec6fb7da57ce','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (648,'','2025-04-23 09:33:55.045875','2025-04-23 09:37:00.058411','Nettomiete 04.2025 für 002/9902',2025,4,1,'2025-04-01',1950.00,'1102',1,NULL,'3000','2c141675a58b41169a8f0f0a0bbfddff','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (649,'','2025-04-23 09:33:55.076099','2025-04-23 09:37:00.060892','Nebenkosten 04.2025 für 002/9902',2025,4,1,'2025-04-01',250.00,'1102',1,NULL,'2301','92bf5b7955f74e5b95caaf0a542f0685','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (650,'','2025-04-23 09:33:55.116183','2025-04-23 09:33:55.116214','Nettomiete 05.2025 für 001/9901/9906',2025,5,1,'2025-05-01',1759.00,'1102',3,NULL,'3001','8b43a9c97c2045468546ccbbfa19cc07','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (651,'','2025-04-23 09:33:55.145136','2025-04-23 09:33:55.145170','Nebenkosten 05.2025 für 001/9901/9906',2025,5,1,'2025-05-01',208.00,'1102',3,NULL,'2301','e3e1a74e3f774a65882e1e823f28b553','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (652,'','2025-04-23 09:33:55.181447','2025-04-23 09:33:55.181487','Strompauschale 05.2025 für 001/9901/9906',2025,5,1,'2025-05-01',5.00,'1102',3,NULL,'2302','b149974eda6d45b593428dbcdb27472c','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (653,'','2025-04-23 09:33:55.225398','2025-04-23 09:33:55.225438','Nettomiete 04.2025 für 001/9901/9906',2025,4,1,'2025-04-01',1759.00,'1102',3,NULL,'3001','699bc862ecfa4819b7e0007497b9a4e3','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (654,'','2025-04-23 09:33:55.260846','2025-04-23 09:33:55.260879','Nebenkosten 04.2025 für 001/9901/9906',2025,4,1,'2025-04-01',208.00,'1102',3,NULL,'2301','020712ee20474d3d8818f903927118aa','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (655,'','2025-04-23 09:33:55.294101','2025-04-23 09:33:55.294137','Strompauschale 04.2025 für 001/9901/9906',2025,4,1,'2025-04-01',5.00,'1102',3,NULL,'2302','ccd9d6144d2e4387be01a2be51a90dd0','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (656,'','2025-04-23 09:33:55.331534','2025-04-23 09:37:00.085116','Nettomiete 05.2025 für 101/9903',2025,5,1,'2025-05-01',6690.00,'1102',4,NULL,'3000','61c15104bfbe4a50bfd5135e081531e6','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (657,'','2025-04-23 09:33:55.356833','2025-04-23 09:37:00.087669','Nebenkosten 05.2025 für 101/9903',2025,5,1,'2025-05-01',635.00,'1102',4,NULL,'2301','5f0d35ee7a504c7ca0b1388d505577d5','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (658,'','2025-04-23 09:33:55.386005','2025-04-23 09:37:00.080302','Nettomiete 04.2025 für 101/9903',2025,4,1,'2025-04-01',6690.00,'1102',4,NULL,'3000','87345e1a064442e6bcb6a437c8b3efca','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (659,'','2025-04-23 09:33:55.569413','2025-04-23 09:37:00.082527','Nebenkosten 04.2025 für 101/9903',2025,4,1,'2025-04-01',635.00,'1102',4,NULL,'2301','a7bc9953289c4446ab10f0da9b51960e','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (660,'','2025-04-23 09:33:55.613483','2025-04-23 09:33:55.613516','Nettomiete 05.2025 für 201/9904',2025,5,1,'2025-05-01',768.00,'1102',5,NULL,'3000','b6f9e09d5bab42a79004d49baa6c2bd2','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (661,'','2025-04-23 09:33:55.645683','2025-04-23 09:33:55.645716','Nebenkosten 05.2025 für 201/9904',2025,5,1,'2025-05-01',82.00,'1102',5,NULL,'2301','ee7ff939d8f241cf92a4910b0afa2ef5','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (662,'','2025-04-23 09:33:55.684903','2025-04-23 09:33:55.684945','Nettomiete 04.2025 für 201/9904',2025,4,1,'2025-04-01',768.00,'1102',5,NULL,'3000','4e42ccaa8b5c4a90be9bc28d6a487071','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (663,'','2025-04-23 09:33:55.723318','2025-04-23 09:33:55.723357','Nebenkosten 04.2025 für 201/9904',2025,4,1,'2025-04-01',82.00,'1102',5,NULL,'2301','9a486385191144e1827dac47d6fb5dfb','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (664,'','2025-04-23 09:33:55.762935','2025-04-23 09:37:00.105878','Nettomiete 05.2025 für 202',2025,5,1,'2025-05-01',1125.00,'1102',6,NULL,'3000','f53716c6aebb4f2b8fb4be8f5c97ac72','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (665,'','2025-04-23 09:33:55.792801','2025-04-23 09:37:00.107976','Nebenkosten 05.2025 für 202',2025,5,1,'2025-05-01',195.00,'1102',6,NULL,'2301','3f6a3e252171449ea4ce16fc6e8f7015','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (666,'','2025-04-23 09:33:55.825404','2025-04-23 09:37:00.102054','Nettomiete 04.2025 für 202',2025,4,1,'2025-04-01',1125.00,'1102',6,NULL,'3000','53547e8cd93e4a3ca074bc6fd6b8208b','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (667,'','2025-04-23 09:33:55.853966','2025-04-23 09:37:00.104001','Nebenkosten 04.2025 für 202',2025,4,1,'2025-04-01',195.00,'1102',6,NULL,'2301','ad7d50cd152d46d28bf9377110562396','Invoice',1,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (668,'','2025-04-23 09:33:55.893025','2025-04-23 09:33:55.893053','Nettomiete 05.2025 für 003/9906',2025,5,1,'2025-05-01',1265.00,'1102',7,NULL,'3001','ac330e3a5cc74527b3b5b9ef04a73027','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (669,'','2025-04-23 09:33:55.922583','2025-04-23 09:33:55.922611','Nebenkosten 05.2025 für 003/9906',2025,5,1,'2025-05-01',187.00,'1102',7,NULL,'2301','123138bf7b03476b995beb861de4bb6f','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (670,'','2025-04-23 09:33:55.951635','2025-04-23 09:33:55.951664','Strompauschale 05.2025 für 003/9906',2025,5,1,'2025-05-01',5.00,'1102',7,NULL,'2302','ae3d882ef0604463b243e0cb51f24228','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (671,'','2025-04-23 09:33:55.994279','2025-04-23 09:33:55.994315','Nettomiete 04.2025 für 003/9906',2025,4,1,'2025-04-01',1265.00,'1102',7,NULL,'3001','9b4fe4d8d4e04aa28b18c6ad3408c01d','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (672,'','2025-04-23 09:33:56.031161','2025-04-23 09:33:56.031195','Nebenkosten 04.2025 für 003/9906',2025,4,1,'2025-04-01',187.00,'1102',7,NULL,'2301','dbf4a0cfaf6f4a2b92c73ef03f891a63','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (673,'','2025-04-23 09:33:56.066397','2025-04-23 09:33:56.066432','Strompauschale 04.2025 für 003/9906',2025,4,1,'2025-04-01',5.00,'1102',7,NULL,'2302','1e74180fe70c490baf4d636ac080771f','Invoice',0,2,'','','',0);
INSERT INTO `geno_invoice` VALUES (674,'','2025-04-23 09:36:38.434822','2025-04-23 09:37:00.129656','Einzahlung Mietzins wiederkehrend 002/9902',NULL,NULL,1,'2025-04-23',15400.00,'1102',8,NULL,'1020.1','12e021eaed24447ca53eb570c03df812','Payment',1,2,'DEMO Einzahlung/Alder, Mario','100000000000000000000800000','_DEMO_100000000000000000000800000_20250423113618_',0);
INSERT INTO `geno_invoice` VALUES (675,'','2025-04-23 09:36:38.473049','2025-04-23 09:37:00.170145','Einzahlung Mietzins wiederkehrend 201/9904',NULL,NULL,1,'2025-04-23',1700.00,'1102',10,NULL,'1020.1','87294fba626847a4af115a2f676b7fe6','Payment',1,2,'DEMO Einzahlung/Deshar, Fatma','100000000000000000001000006','_DEMO_100000000000000000001000006_20250423113618_',0);
INSERT INTO `geno_invoice` VALUES (676,'','2025-04-23 09:36:38.509192','2025-04-23 09:37:00.188862','Einzahlung Mietzins wiederkehrend 203',NULL,NULL,1,'2025-04-23',1000.00,'1102',12,NULL,'1020.1','a46826e9da6648899f460d1456a948b8','Payment',1,2,'DEMO Einzahlung/Rossi, Mario','100000000000000000001200007','_DEMO_100000000000000000001200007_20250423113618_',0);
INSERT INTO `geno_invoice` VALUES (677,'','2025-04-23 09:36:38.548278','2025-04-23 09:37:00.207251','Einzahlung Mietzins wiederkehrend PP-01',NULL,NULL,1,'2025-04-23',240.00,'1102',14,NULL,'1020.1','42a08a9a1e2f41b58203c07f18624b84','Payment',1,2,'DEMO Einzahlung/Brot GmbH,  ','100000000000000000001400002','_DEMO_100000000000000000001400002_20250423113618_',0);
INSERT INTO `geno_invoice` VALUES (678,'','2025-04-23 09:36:38.581709','2025-04-23 09:37:00.055496','Einzahlung Mietzins wiederkehrend 002/9902',NULL,NULL,1,'2025-04-23',4400.00,'1102',1,NULL,'1020.1','a20f72a7ff63400e896094460c3b9b00','Payment',1,2,'DEMO Einzahlung/Dupont, Jean','100000000000000000000100005','_DEMO_100000000000000000000100005_20250423113618_',0);
INSERT INTO `geno_invoice` VALUES (679,'','2025-04-23 09:36:38.614667','2025-04-23 09:37:00.078142','Einzahlung Mietzins wiederkehrend 101/9903',NULL,NULL,1,'2025-04-23',14650.00,'1102',4,NULL,'1020.1','4114beca8128423b8ac93d263054df0d','Payment',1,2,'DEMO Einzahlung/Borg, Folana','100000000000000000000400008','_DEMO_100000000000000000000400008_20250423113618_',0);
INSERT INTO `geno_invoice` VALUES (680,'','2025-04-23 09:36:38.649497','2025-04-23 09:37:00.099754','Einzahlung Mietzins wiederkehrend 202',NULL,NULL,1,'2025-04-23',2640.00,'1102',6,NULL,'1020.1','f5af006f2c5c4cda867ce1aac8de7011','Payment',1,2,'DEMO Einzahlung/Jensen, Hugo','100000000000000000000600001','_DEMO_100000000000000000000600001_20250423113618_',0);
/*!40000 ALTER TABLE `geno_invoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_invoicecategory`
--

DROP TABLE IF EXISTS `geno_invoicecategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_invoicecategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `reference_id` smallint(6) NOT NULL,
  `note` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `income_account` varchar(50) NOT NULL,
  `linked_object_type` varchar(50) NOT NULL,
  `manual_allowed` tinyint(1) NOT NULL,
  `receivables_account` varchar(50) NOT NULL,
  `email_template_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference_id` (`reference_id`),
  KEY `geno_invoicecategory_email_template_id_402bd2e1_fk_geno_cont` (`email_template_id`),
  CONSTRAINT `geno_invoicecategory_email_template_id_402bd2e1_fk_geno_cont` FOREIGN KEY (`email_template_id`) REFERENCES `geno_contenttemplate` (`id`),
  CONSTRAINT `geno_invoicecategory_reference_id_range` CHECK (`reference_id` > 0 and `reference_id` < 90)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_invoicecategory`
--

LOCK TABLES `geno_invoicecategory` WRITE;
/*!40000 ALTER TABLE `geno_invoicecategory` DISABLE KEYS */;
INSERT INTO `geno_invoicecategory` VALUES (1,'','2024-10-30 16:10:10.889454','2024-10-30 16:14:32.583073','Mitgliedschaft',36,'',1,'3001','Address',1,'1100',NULL);
INSERT INTO `geno_invoicecategory` VALUES (2,'','2024-10-30 16:11:02.493289','2024-10-30 16:11:02.493331','Mietzins wiederkehrend',10,'',1,'3000','Contract',0,'1102',NULL);
INSERT INTO `geno_invoicecategory` VALUES (3,'','2024-10-30 16:11:28.298790','2024-10-30 16:11:28.298834','Einlage Solidaritätsfonds',11,'',1,'0','Contract',0,'246',NULL);
INSERT INTO `geno_invoicecategory` VALUES (4,'','2024-10-30 16:11:52.463816','2024-10-30 16:11:52.463856','Nebenkostenabrechung',12,'',1,'1104','Contract',0,'1102',NULL);
INSERT INTO `geno_invoicecategory` VALUES (5,'','2024-10-30 16:12:12.740318','2024-10-30 16:12:12.740360','Nebenkosten Akonto ausserordentlich',13,'',1,'2301','Contract',1,'1102',NULL);
INSERT INTO `geno_invoicecategory` VALUES (6,'','2024-10-30 16:13:09.470801','2024-10-30 16:13:09.470847','Geschäftsstelle',30,'',1,'3500','Address',1,'1100',NULL);
INSERT INTO `geno_invoicecategory` VALUES (7,'','2024-10-30 16:13:41.417755','2024-10-30 16:14:09.749741','Miete Gästezimmer',31,'',1,'3520','Address',1,'1100',NULL);
/*!40000 ALTER TABLE `geno_invoicecategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_lookuptable`
--

DROP TABLE IF EXISTS `geno_lookuptable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_lookuptable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `lookup_type` varchar(20) NOT NULL,
  `value` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_lookuptable`
--

LOCK TABLES `geno_lookuptable` WRITE;
/*!40000 ALTER TABLE `geno_lookuptable` DISABLE KEYS */;
/*!40000 ALTER TABLE `geno_lookuptable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_member`
--

DROP TABLE IF EXISTS `geno_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `date_join` date NOT NULL,
  `date_leave` date DEFAULT NULL,
  `notes` longtext NOT NULL,
  `name_id` int(11) NOT NULL,
  `flag_01` tinyint(1) NOT NULL,
  `flag_02` tinyint(1) NOT NULL,
  `flag_03` tinyint(1) NOT NULL,
  `flag_04` tinyint(1) NOT NULL,
  `flag_05` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_id` (`name_id`),
  CONSTRAINT `geno_member_name_id_b5d31bbc_fk_geno_address_id` FOREIGN KEY (`name_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_member`
--

LOCK TABLES `geno_member` WRITE;
/*!40000 ALTER TABLE `geno_member` DISABLE KEYS */;
INSERT INTO `geno_member` VALUES (1,'','2024-10-30 16:03:12.682708','2024-11-25 16:08:53.224894','2022-02-01',NULL,'',2,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (2,'','2024-10-30 16:03:18.913315','2024-11-25 16:08:53.208569','2020-05-01',NULL,'',3,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (3,'','2024-10-30 16:03:23.293556','2024-11-25 16:08:53.240829','2021-10-11',NULL,'',7,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (4,'','2024-10-30 16:03:27.699291','2024-11-25 16:08:53.454562','2020-01-14',NULL,'',17,0,1,0,0,0);
INSERT INTO `geno_member` VALUES (5,'','2024-10-30 16:03:31.198114','2024-11-25 16:08:53.470493','2022-01-21',NULL,'',18,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (6,'','2024-10-30 16:03:34.741712','2024-11-25 16:08:53.257671','2022-09-10',NULL,'',24,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (7,'','2024-10-30 16:03:38.457845','2024-11-25 16:08:53.421934','2022-01-22',NULL,'',9,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (8,'','2024-10-30 16:03:41.805955','2024-11-25 16:08:53.438290','2021-01-09',NULL,'',11,1,0,0,0,0);
INSERT INTO `geno_member` VALUES (9,'','2024-11-25 16:08:52.929995','2024-11-25 16:08:52.930068','2023-01-30',NULL,'',29,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (10,'','2024-11-25 16:08:52.947120','2024-11-25 16:08:52.947161','2020-01-27',NULL,'',27,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (11,'','2024-11-25 16:08:52.966087','2024-11-25 16:08:52.966127','2022-09-17',NULL,'',28,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (12,'','2024-11-25 16:08:52.982062','2024-11-25 16:08:52.982102','2021-10-20',NULL,'',19,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (13,'','2024-11-25 16:08:52.998763','2024-11-25 16:08:52.998803','2023-03-24',NULL,'',12,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (14,'','2024-11-25 16:08:53.015186','2024-11-25 16:08:53.015225','2022-02-26',NULL,'',23,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (15,'','2024-11-25 16:08:53.031297','2024-11-25 16:08:53.031337','2021-12-14',NULL,'',26,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (16,'','2024-11-25 16:08:53.047276','2024-11-25 16:08:53.047316','2022-08-15',NULL,'',4,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (17,'','2024-11-25 16:08:53.063187','2024-11-25 16:08:53.063227','2023-10-07',NULL,'',5,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (18,'','2024-11-25 16:08:53.079765','2024-11-25 16:08:53.079805','2023-06-05',NULL,'',6,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (19,'','2024-11-25 16:08:53.096154','2024-11-25 16:08:53.096195','2022-05-01',NULL,'',20,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (20,'','2024-11-25 16:08:53.112127','2024-11-25 16:08:53.112167','2020-10-27',NULL,'',15,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (21,'','2024-11-25 16:08:53.128247','2024-11-25 16:08:53.128303','2022-09-15',NULL,'',16,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (22,'','2024-11-25 16:08:53.144362','2024-11-25 16:08:53.144402','2021-10-21',NULL,'',8,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (23,'','2024-11-25 16:08:53.160386','2024-11-25 16:08:53.160426','2020-07-17',NULL,'',10,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (24,'','2024-11-25 16:08:53.176541','2024-11-25 16:08:53.176581','2023-06-15',NULL,'',25,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (25,'','2024-11-25 16:08:53.192607','2024-11-25 16:08:53.192647','2022-10-18',NULL,'',13,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (26,'','2024-11-25 16:08:53.274134','2024-11-25 16:08:53.274174','2022-02-08',NULL,'',31,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (27,'','2024-11-25 16:08:53.291275','2024-11-25 16:08:53.291315','2023-11-20',NULL,'',30,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (28,'','2024-11-25 16:08:53.307429','2024-11-25 16:08:53.307469','2023-11-13',NULL,'',22,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (29,'','2024-11-25 16:08:53.323808','2024-11-25 16:08:53.323848','2022-09-21',NULL,'',32,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (30,'','2024-11-25 16:08:53.340677','2024-11-25 16:08:53.340717','2020-07-20',NULL,'',14,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (31,'','2024-11-25 16:08:53.358171','2024-11-25 16:08:53.358211','2022-01-18',NULL,'',33,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (32,'','2024-11-25 16:08:53.373994','2024-11-25 16:08:53.374035','2023-07-27',NULL,'',21,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (33,'','2024-11-25 16:08:53.389859','2024-11-25 16:08:53.389899','2020-12-05',NULL,'',34,0,0,0,0,0);
INSERT INTO `geno_member` VALUES (34,'','2024-11-25 16:08:53.406039','2024-11-25 16:08:53.406079','2021-10-19',NULL,'',35,0,0,0,0,0);
/*!40000 ALTER TABLE `geno_member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_memberattribute`
--

DROP TABLE IF EXISTS `geno_memberattribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_memberattribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `date` date DEFAULT NULL,
  `value` varchar(100) NOT NULL,
  `attribute_type_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_memberattribute_attribute_type_id_be925fdf_fk_geno_memb` (`attribute_type_id`),
  KEY `geno_memberattribute_member_id_d029ecd0_fk_geno_member_id` (`member_id`),
  CONSTRAINT `geno_memberattribute_attribute_type_id_be925fdf_fk_geno_memb` FOREIGN KEY (`attribute_type_id`) REFERENCES `geno_memberattributetype` (`id`),
  CONSTRAINT `geno_memberattribute_member_id_d029ecd0_fk_geno_member_id` FOREIGN KEY (`member_id`) REFERENCES `geno_member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_memberattribute`
--

LOCK TABLES `geno_memberattribute` WRITE;
/*!40000 ALTER TABLE `geno_memberattribute` DISABLE KEYS */;
INSERT INTO `geno_memberattribute` VALUES (1,'','2024-10-30 16:07:08.204007','2024-10-30 16:07:08.204063','2024-10-30','Bezahlt',1,1);
INSERT INTO `geno_memberattribute` VALUES (2,'','2024-10-30 16:07:23.768287','2024-10-30 16:07:23.768328','2024-08-30','Rechnung verschickt',3,2);
/*!40000 ALTER TABLE `geno_memberattribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_memberattributetype`
--

DROP TABLE IF EXISTS `geno_memberattributetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_memberattributetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_memberattributetype`
--

LOCK TABLES `geno_memberattributetype` WRITE;
/*!40000 ALTER TABLE `geno_memberattributetype` DISABLE KEYS */;
INSERT INTO `geno_memberattributetype` VALUES (1,'','2024-10-30 16:05:14.328555','2024-10-30 16:05:14.328596','Beitrittsgebühr','Inkasso Beitrittsgebühr');
INSERT INTO `geno_memberattributetype` VALUES (2,'','2024-10-30 16:05:32.556904','2024-10-30 16:05:48.327894','Versand Einladung','Tracking Versand');
INSERT INTO `geno_memberattributetype` VALUES (3,'','2024-10-30 16:06:08.028617','2024-10-30 16:06:08.028659','Mitgliederbeitrag 2024','Inkasso Mitgliederbeitrag');
/*!40000 ALTER TABLE `geno_memberattributetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_registration`
--

DROP TABLE IF EXISTS `geno_registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_registration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `slot_id` int(11) NOT NULL,
  `check1` tinyint(1) NOT NULL,
  `check2` tinyint(1) NOT NULL,
  `check3` tinyint(1) NOT NULL,
  `check4` tinyint(1) NOT NULL,
  `check5` tinyint(1) NOT NULL,
  `notes` longtext NOT NULL,
  `text1` varchar(100) NOT NULL,
  `text2` varchar(100) NOT NULL,
  `text3` varchar(100) NOT NULL,
  `text4` varchar(100) NOT NULL,
  `text5` varchar(100) NOT NULL,
  `telephone` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_registration_slot_id_55aec6da_fk_geno_registrationslot_id` (`slot_id`),
  CONSTRAINT `geno_registration_slot_id_55aec6da_fk_geno_registrationslot_id` FOREIGN KEY (`slot_id`) REFERENCES `geno_registrationslot` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_registration`
--

LOCK TABLES `geno_registration` WRITE;
/*!40000 ALTER TABLE `geno_registration` DISABLE KEYS */;
/*!40000 ALTER TABLE `geno_registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_registrationevent`
--

DROP TABLE IF EXISTS `geno_registrationevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_registrationevent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `confirmation_mail_sender` varchar(50) NOT NULL,
  `confirmation_mail_text` longtext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `check1_label` varchar(100) NOT NULL,
  `check2_label` varchar(100) NOT NULL,
  `check3_label` varchar(100) NOT NULL,
  `check4_label` varchar(100) NOT NULL,
  `check5_label` varchar(100) NOT NULL,
  `enable_notes` tinyint(1) NOT NULL,
  `publication_end` datetime(6) DEFAULT NULL,
  `publication_start` datetime(6) DEFAULT NULL,
  `publication_type` varchar(30) NOT NULL,
  `text1_label` varchar(100) NOT NULL,
  `text2_label` varchar(100) NOT NULL,
  `text3_label` varchar(100) NOT NULL,
  `text4_label` varchar(100) NOT NULL,
  `text5_label` varchar(100) NOT NULL,
  `enable_telephone` tinyint(1) NOT NULL,
  `show_counter` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_registrationevent_active_f29b187f` (`active`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_registrationevent`
--

LOCK TABLES `geno_registrationevent` WRITE;
/*!40000 ALTER TABLE `geno_registrationevent` DISABLE KEYS */;
INSERT INTO `geno_registrationevent` VALUES (1,'','2024-10-22 08:03:44.194127','2024-10-30 15:23:22.051118','Hausführung','Öffentliche Hausführung, Anmeldung erforderlich.','info@example.com','Freundliche Grüsse,\r\nGenossenschaft Musterweg',1,'Ich nehme am Apéro teil','','','','',0,NULL,NULL,'public','','','','','',0,1);
/*!40000 ALTER TABLE `geno_registrationevent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_registrationslot`
--

DROP TABLE IF EXISTS `geno_registrationslot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_registrationslot` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` datetime(6) NOT NULL,
  `max_places` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `alt_text` varchar(100) NOT NULL,
  `is_backup_for_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `is_backup_for_id` (`is_backup_for_id`),
  KEY `geno_registrationslo_event_id_5733ee3c_fk_geno_regi` (`event_id`),
  CONSTRAINT `geno_registrationslo_event_id_5733ee3c_fk_geno_regi` FOREIGN KEY (`event_id`) REFERENCES `geno_registrationevent` (`id`),
  CONSTRAINT `geno_registrationslo_is_backup_for_id_dcbee07d_fk_geno_regi` FOREIGN KEY (`is_backup_for_id`) REFERENCES `geno_registrationslot` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_registrationslot`
--

LOCK TABLES `geno_registrationslot` WRITE;
/*!40000 ALTER TABLE `geno_registrationslot` DISABLE KEYS */;
INSERT INTO `geno_registrationslot` VALUES (1,'','2024-10-22 08:03:44.226518','2024-10-30 15:23:22.052411','2026-10-22 16:00:00.000000',10,1,'',NULL);
INSERT INTO `geno_registrationslot` VALUES (2,'','2024-10-22 08:21:11.993336','2024-10-30 15:23:22.053462','2026-10-23 16:00:00.000000',10,1,'',NULL);
/*!40000 ALTER TABLE `geno_registrationslot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_rentalunit`
--

DROP TABLE IF EXISTS `geno_rentalunit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_rentalunit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `rental_type` varchar(50) NOT NULL,
  `floor` varchar(50) NOT NULL,
  `area` decimal(10,2) DEFAULT NULL,
  `area_balcony` decimal(10,2) DEFAULT NULL,
  `area_add` decimal(10,2) DEFAULT NULL,
  `height` varchar(10) DEFAULT NULL,
  `rooms` decimal(5,1) DEFAULT NULL,
  `min_occupancy` decimal(5,1) DEFAULT NULL,
  `nk` decimal(10,2) DEFAULT NULL,
  `rent_total` decimal(10,2) DEFAULT NULL,
  `depot` decimal(10,2) DEFAULT NULL,
  `share` decimal(10,2) DEFAULT NULL,
  `note` varchar(200) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `description` longtext NOT NULL,
  `label` varchar(50) NOT NULL,
  `label_short` varchar(50) NOT NULL,
  `rent_year` decimal(11,2) DEFAULT NULL,
  `status` varchar(100) NOT NULL,
  `svg_polygon` longtext NOT NULL,
  `nk_electricity` decimal(10,2) DEFAULT NULL,
  `adit_serial` longtext NOT NULL,
  `building_id` int(11) NOT NULL,
  `volume` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `geno_rentalunit_name_building_link_id_1fa2a7c0_uniq` (`name`,`building_id`),
  KEY `geno_rentalunit_building_id_b5a6149d_fk_geno_building_id` (`building_id`),
  CONSTRAINT `geno_rentalunit_building_id_b5a6149d_fk_geno_building_id` FOREIGN KEY (`building_id`) REFERENCES `geno_building` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_rentalunit`
--

LOCK TABLES `geno_rentalunit` WRITE;
/*!40000 ALTER TABLE `geno_rentalunit` DISABLE KEYS */;
INSERT INTO `geno_rentalunit` VALUES (1,'','2024-10-16 15:38:13.867417','2024-10-21 14:15:55.777244','001','Wohnung','EG',75.50,6.30,NULL,'2.5',3.0,2.0,180.00,1790.00,NULL,28000.00,'',1,'','','',NULL,'Vermietet','',NULL,'900223',2,188.75);
INSERT INTO `geno_rentalunit` VALUES (2,'','2024-10-21 08:42:16.868973','2024-10-21 11:51:58.128082','003','Gewerbe','EG',65.30,NULL,NULL,'3.5',NULL,NULL,159.00,1275.00,NULL,13400.00,'',1,'','Gewerberaum','003_Gewerberaum',NULL,'Vermietet','',NULL,'',1,228.55);
INSERT INTO `geno_rentalunit` VALUES (3,'','2024-10-21 11:35:33.086770','2024-10-21 14:16:04.377693','101','Grosswohnung','1.OG',285.00,12.00,NULL,'2.5',10.0,8.0,635.00,7325.00,NULL,101400.00,'',1,'','','',NULL,'Vermietet','',NULL,'900225',2,712.50);
INSERT INTO `geno_rentalunit` VALUES (4,'','2024-10-21 11:38:12.818506','2024-10-21 14:16:14.003349','201','Wohnung','2.OG',36.00,6.00,NULL,'2.5',1.5,1.0,82.00,850.00,NULL,14000.00,'',1,'','','',NULL,'Vermietet','',NULL,'900226',2,90.00);
INSERT INTO `geno_rentalunit` VALUES (5,'','2024-10-21 11:42:00.462746','2024-10-21 14:16:22.259339','202','Wohnung','2.OG',54.75,5.50,NULL,'2.5',2.5,1.0,195.00,1320.00,NULL,20800.00,'',1,'','','',NULL,'Vermietet','',NULL,'900227',2,136.88);
INSERT INTO `geno_rentalunit` VALUES (6,'','2024-10-21 11:49:24.275434','2024-10-21 14:19:57.070902','203','Jokerzimmer','2.OG',24.00,NULL,NULL,'2.5',1.0,1.0,55.00,500.00,NULL,NULL,'',1,'','Gästezimmer','',NULL,'Verfügbar','',NULL,'900128',1,48.00);
INSERT INTO `geno_rentalunit` VALUES (7,'','2024-10-21 11:54:04.703317','2024-10-21 11:54:04.703359','9901','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 001',1,'','','',NULL,'Vermietet','',NULL,'',1,34.93);
INSERT INTO `geno_rentalunit` VALUES (8,'','2024-10-21 11:54:28.806001','2024-10-21 11:54:28.806044','9902','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 002',1,'','','',NULL,'Vermietet','',NULL,'',1,34.93);
INSERT INTO `geno_rentalunit` VALUES (9,'','2024-10-21 11:55:39.053229','2024-10-21 11:55:39.053274','9903','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 201',1,'','','',NULL,'Vermietet','',NULL,'',1,34.93);
INSERT INTO `geno_rentalunit` VALUES (10,'','2024-10-21 11:55:46.835078','2024-10-21 11:55:46.835122','9904','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 202',1,'','','',NULL,'Vermietet','',NULL,'',1,34.93);
INSERT INTO `geno_rentalunit` VALUES (11,'','2024-10-21 11:56:19.212736','2024-10-21 11:56:19.212778','9905','Kellerabteil','Keller',26.00,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 101',1,'','','',NULL,'Vermietet','',NULL,'',1,71.50);
INSERT INTO `geno_rentalunit` VALUES (12,'','2024-10-21 14:04:09.038687','2024-10-21 14:08:22.445361','9906','Lager','Keller',20.50,NULL,NULL,'2.75',NULL,NULL,28.00,182.00,NULL,2000.00,'',1,'','','',NULL,'Vermietet','',5.00,'',1,56.38);
INSERT INTO `geno_rentalunit` VALUES (13,'','2024-10-21 14:16:55.375643','2024-10-21 14:16:55.375685','001','Wohnung','EG',75.50,6.30,NULL,'2.5',3.0,2.0,180.00,1790.00,NULL,28000.00,'',1,'','','',NULL,'Vermietet','',NULL,'900123',1,188.75);
INSERT INTO `geno_rentalunit` VALUES (14,'','2024-10-21 14:17:07.046346','2024-10-21 14:17:07.046399','101','Grosswohnung','1.OG',285.00,12.00,NULL,'2.5',10.0,8.0,635.00,7325.00,NULL,101400.00,'',1,'','','',NULL,'Vermietet','',NULL,'900125',1,712.50);
INSERT INTO `geno_rentalunit` VALUES (15,'','2024-10-21 14:17:16.463198','2024-10-21 14:17:16.463242','201','Wohnung','2.OG',36.00,6.00,NULL,'2.5',1.5,1.0,82.00,850.00,NULL,14000.00,'',1,'','','',NULL,'Vermietet','',NULL,'900126',1,90.00);
INSERT INTO `geno_rentalunit` VALUES (16,'','2024-10-21 14:17:24.658353','2024-10-21 14:17:24.658398','202','Wohnung','2.OG',54.75,5.50,NULL,'2.5',2.5,1.0,195.00,1320.00,NULL,20800.00,'',1,'','','',NULL,'Vermietet','',NULL,'900127',1,136.88);
INSERT INTO `geno_rentalunit` VALUES (17,'','2024-10-21 14:17:34.333769','2024-10-21 14:19:33.478191','203','Jokerzimmer','2.OG',24.00,NULL,NULL,'2.5',1.0,1.0,55.00,500.00,NULL,NULL,'',1,'','','',NULL,'Vermietet','',NULL,'900228',2,48.00);
INSERT INTO `geno_rentalunit` VALUES (18,'','2024-10-21 14:18:45.555063','2024-10-21 14:18:45.555106','003','Gemeinschaft','EG',65.30,NULL,NULL,'3.5',NULL,NULL,NULL,NULL,NULL,NULL,'',1,'','Gemeinschaftsküche','Gemeinschaftsküche',NULL,'Verfügbar','',NULL,'',2,228.55);
INSERT INTO `geno_rentalunit` VALUES (19,'','2024-10-21 14:21:06.457788','2024-10-21 14:21:06.457842','9901','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 001',1,'','','',NULL,'Vermietet','',NULL,'',2,34.93);
INSERT INTO `geno_rentalunit` VALUES (20,'','2024-10-21 14:21:11.169737','2024-10-21 14:21:11.169781','9902','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 002',1,'','','',NULL,'Vermietet','',NULL,'',2,34.93);
INSERT INTO `geno_rentalunit` VALUES (21,'','2024-10-21 14:21:15.288376','2024-10-21 14:21:15.288419','9903','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 201',1,'','','',NULL,'Vermietet','',NULL,'',2,34.93);
INSERT INTO `geno_rentalunit` VALUES (22,'','2024-10-21 14:21:22.227255','2024-10-21 14:21:22.227298','9904','Kellerabteil','Keller',12.70,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 202',1,'','','',NULL,'Vermietet','',NULL,'',2,34.93);
INSERT INTO `geno_rentalunit` VALUES (23,'','2024-10-21 14:21:29.047504','2024-10-21 14:21:29.047547','9905','Kellerabteil','Keller',26.00,NULL,NULL,'2.75',NULL,NULL,NULL,NULL,NULL,NULL,'Mieterkeller Wohnung 101',1,'','','',NULL,'Vermietet','',NULL,'',2,71.50);
INSERT INTO `geno_rentalunit` VALUES (24,'','2024-10-21 14:21:43.937391','2024-10-21 14:21:43.937433','9906','Hobby','Keller',20.50,NULL,NULL,'2.75',NULL,NULL,28.00,182.00,NULL,2000.00,'',1,'','','',NULL,'Vermietet','',5.00,'',2,56.38);
INSERT INTO `geno_rentalunit` VALUES (25,'','2024-10-21 14:24:11.820814','2024-10-21 14:24:11.820855','PP-01','Parkplatz','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,120.00,NULL,NULL,'',1,'','Parkplatz','',NULL,'Vermietet','',NULL,'',2,NULL);
INSERT INTO `geno_rentalunit` VALUES (26,'','2024-10-21 14:40:31.367913','2024-10-21 14:40:31.367957','002','Wohnung','',99.25,6.50,NULL,'2.5',4.0,3.0,250.00,2200.00,NULL,40000.00,'',1,'','','',NULL,'Vermietet','',NULL,'900124',1,248.13);
INSERT INTO `geno_rentalunit` VALUES (27,'','2024-10-21 14:40:40.930186','2024-10-21 14:40:40.930240','002','Wohnung','',99.25,6.50,NULL,'2.5',4.0,3.0,250.00,2200.00,NULL,40000.00,'',1,'','','',NULL,'Vermietet','',NULL,'900224',2,248.13);
INSERT INTO `geno_rentalunit` VALUES (28,'','2024-10-22 14:52:50.446193','2024-10-22 14:52:50.446246','PP-02','Parkplatz','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,120.00,NULL,NULL,'',1,'','Parkplatz','',NULL,'Vermietet','',NULL,'',2,NULL);
/*!40000 ALTER TABLE `geno_rentalunit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_share`
--

DROP TABLE IF EXISTS `geno_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_share` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `date` date NOT NULL,
  `quantity` int(10) unsigned NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `name_id` int(11) NOT NULL,
  `share_type_id` int(11) NOT NULL,
  `date_end` date DEFAULT NULL,
  `state` varchar(50) NOT NULL,
  `is_interest_credit` tinyint(1) NOT NULL,
  `note` varchar(200) NOT NULL,
  `duration` int(10) unsigned DEFAULT NULL,
  `date_due` date DEFAULT NULL,
  `is_pension_fund` tinyint(1) NOT NULL,
  `is_business` tinyint(1) NOT NULL,
  `attached_to_contract_id` int(11) DEFAULT NULL,
  `interest_mode` varchar(50) NOT NULL,
  `manual_interest` decimal(4,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `geno_share_name_id_80b3fa43_fk_geno_address_id` (`name_id`),
  KEY `geno_share_share_type_id_83c57506_fk_geno_sharetype_id` (`share_type_id`),
  KEY `geno_share_attached_to_contract_id_38abb509_fk_geno_contract_id` (`attached_to_contract_id`),
  CONSTRAINT `geno_share_attached_to_contract_id_38abb509_fk_geno_contract_id` FOREIGN KEY (`attached_to_contract_id`) REFERENCES `geno_contract` (`id`),
  CONSTRAINT `geno_share_name_id_80b3fa43_fk_geno_address_id` FOREIGN KEY (`name_id`) REFERENCES `geno_address` (`id`),
  CONSTRAINT `geno_share_share_type_id_83c57506_fk_geno_sharetype_id` FOREIGN KEY (`share_type_id`) REFERENCES `geno_sharetype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_share`
--

LOCK TABLES `geno_share` WRITE;
/*!40000 ALTER TABLE `geno_share` DISABLE KEYS */;
INSERT INTO `geno_share` VALUES (1,'','2024-10-30 15:57:09.009692','2024-12-03 10:26:42.673007','2023-07-20',25,200.00,2,1,NULL,'bezahlt',0,'',NULL,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (2,'','2024-10-30 15:57:20.017705','2024-12-03 10:26:47.059297','2023-07-20',25,200.00,3,1,NULL,'bezahlt',0,'',NULL,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (3,'','2024-10-30 15:57:54.834265','2024-12-03 10:35:18.684516','2024-06-22',27,200.00,5,1,NULL,'bezahlt',0,'',NULL,NULL,1,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (4,'','2024-10-30 15:58:27.471729','2024-10-30 15:58:27.471770','2024-06-20',16,200.00,4,1,NULL,'bezahlt',0,'',NULL,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (5,'','2024-10-30 15:59:37.014982','2024-12-03 10:26:25.651116','2023-03-01',1,10000.00,19,3,NULL,'bezahlt',0,'',10,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (6,'','2024-10-30 15:59:44.811766','2024-12-03 10:26:20.723935','2022-03-01',1,10000.00,20,3,NULL,'bezahlt',0,'',10,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (7,'','2024-10-30 16:00:05.291242','2024-12-03 10:26:15.352942','2022-03-01',1,20000.00,7,2,NULL,'bezahlt',0,'',5,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (8,'','2024-10-30 16:00:39.699635','2024-12-03 10:26:07.462381','2023-05-15',1,5000.00,2,4,NULL,'bezahlt',0,'',NULL,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (9,'','2024-10-30 16:01:12.873293','2024-12-03 10:26:02.642552','2022-05-21',1,12500.00,24,4,NULL,'bezahlt',0,'',NULL,NULL,0,0,NULL,'Standard',0.00);
INSERT INTO `geno_share` VALUES (10,'','2024-12-03 10:34:59.021965','2024-12-03 10:38:04.984504','2022-06-13',1,100000.00,37,2,NULL,'bezahlt',0,'',8,NULL,0,0,NULL,'Manual',1.45);
/*!40000 ALTER TABLE `geno_share` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_sharetype`
--

DROP TABLE IF EXISTS `geno_sharetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_sharetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  `standard_interest` decimal(4,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_sharetype`
--

LOCK TABLES `geno_sharetype` WRITE;
/*!40000 ALTER TABLE `geno_sharetype` DISABLE KEYS */;
INSERT INTO `geno_sharetype` VALUES (1,'','2024-10-30 15:24:32.952276','2024-10-30 15:24:32.952319','Anteilschein','Anteilscheine der Genossenschaft',0.00);
INSERT INTO `geno_sharetype` VALUES (2,'','2024-10-30 15:25:36.997871','2024-10-30 15:25:36.997913','Darlehen verzinst','Verzinste Darlehen',1.25);
INSERT INTO `geno_sharetype` VALUES (3,'','2024-10-30 15:25:55.428708','2024-10-30 15:25:55.428753','Darlehen zinslos','Unverzinste Darlehen',0.00);
INSERT INTO `geno_sharetype` VALUES (4,'','2024-10-30 15:26:13.859455','2024-10-30 15:26:13.859496','Depositenkasse','Depositenkasseneinlagen',0.75);
/*!40000 ALTER TABLE `geno_sharetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geno_tenant`
--

DROP TABLE IF EXISTS `geno_tenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `geno_tenant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `key_number` varchar(30) NOT NULL,
  `notes` longtext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `building_id` int(11) NOT NULL,
  `name_id` int(11) NOT NULL,
  `invitation_date` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_id` (`name_id`),
  KEY `geno_tenant_building_id_4060f5f7_fk_geno_building_id` (`building_id`),
  CONSTRAINT `geno_tenant_building_id_4060f5f7_fk_geno_building_id` FOREIGN KEY (`building_id`) REFERENCES `geno_building` (`id`),
  CONSTRAINT `geno_tenant_name_id_12fb95f3_fk_geno_address_id` FOREIGN KEY (`name_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geno_tenant`
--

LOCK TABLES `geno_tenant` WRITE;
/*!40000 ALTER TABLE `geno_tenant` DISABLE KEYS */;
/*!40000 ALTER TABLE `geno_tenant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oauth2_provider_accesstoken`
--

DROP TABLE IF EXISTS `oauth2_provider_accesstoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `oauth2_provider_accesstoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `expires` datetime(6) NOT NULL,
  `scope` longtext NOT NULL,
  `application_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `source_refresh_token_id` bigint(20) DEFAULT NULL,
  `id_token_id` bigint(20) DEFAULT NULL,
  `token_checksum` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth2_provider_accesstoken_token_checksum_85319a26_uniq` (`token_checksum`),
  UNIQUE KEY `source_refresh_token_id` (`source_refresh_token_id`),
  UNIQUE KEY `id_token_id` (`id_token_id`),
  KEY `oauth2_provider_acce_application_id_b22886e1_fk_oauth2_pr` (`application_id`),
  KEY `oauth2_provider_accesstoken_user_id_6e4c9a65_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_acce_application_id_b22886e1_fk_oauth2_pr` FOREIGN KEY (`application_id`) REFERENCES `oauth2_provider_application` (`id`),
  CONSTRAINT `oauth2_provider_acce_id_token_id_85db651b_fk_oauth2_pr` FOREIGN KEY (`id_token_id`) REFERENCES `oauth2_provider_idtoken` (`id`),
  CONSTRAINT `oauth2_provider_acce_source_refresh_token_e66fbc72_fk_oauth2_pr` FOREIGN KEY (`source_refresh_token_id`) REFERENCES `oauth2_provider_refreshtoken` (`id`),
  CONSTRAINT `oauth2_provider_accesstoken_user_id_6e4c9a65_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oauth2_provider_accesstoken`
--

LOCK TABLES `oauth2_provider_accesstoken` WRITE;
/*!40000 ALTER TABLE `oauth2_provider_accesstoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `oauth2_provider_accesstoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oauth2_provider_application`
--

DROP TABLE IF EXISTS `oauth2_provider_application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `oauth2_provider_application` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `client_id` varchar(100) NOT NULL,
  `redirect_uris` longtext NOT NULL,
  `client_type` varchar(32) NOT NULL,
  `authorization_grant_type` varchar(32) NOT NULL,
  `client_secret` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `skip_authorization` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `algorithm` varchar(5) NOT NULL,
  `post_logout_redirect_uris` longtext NOT NULL,
  `hash_client_secret` tinyint(1) NOT NULL,
  `allowed_origins` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`),
  KEY `oauth2_provider_application_client_secret_53133678` (`client_secret`),
  KEY `oauth2_provider_application_user_id_79829054_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_application_user_id_79829054_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oauth2_provider_application`
--

LOCK TABLES `oauth2_provider_application` WRITE;
/*!40000 ALTER TABLE `oauth2_provider_application` DISABLE KEYS */;
/*!40000 ALTER TABLE `oauth2_provider_application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oauth2_provider_grant`
--

DROP TABLE IF EXISTS `oauth2_provider_grant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `oauth2_provider_grant` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) NOT NULL,
  `expires` datetime(6) NOT NULL,
  `redirect_uri` longtext NOT NULL,
  `scope` longtext NOT NULL,
  `application_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `code_challenge` varchar(128) NOT NULL,
  `code_challenge_method` varchar(10) NOT NULL,
  `nonce` varchar(255) NOT NULL,
  `claims` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `oauth2_provider_gran_application_id_81923564_fk_oauth2_pr` (`application_id`),
  KEY `oauth2_provider_grant_user_id_e8f62af8_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_gran_application_id_81923564_fk_oauth2_pr` FOREIGN KEY (`application_id`) REFERENCES `oauth2_provider_application` (`id`),
  CONSTRAINT `oauth2_provider_grant_user_id_e8f62af8_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oauth2_provider_grant`
--

LOCK TABLES `oauth2_provider_grant` WRITE;
/*!40000 ALTER TABLE `oauth2_provider_grant` DISABLE KEYS */;
/*!40000 ALTER TABLE `oauth2_provider_grant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oauth2_provider_idtoken`
--

DROP TABLE IF EXISTS `oauth2_provider_idtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `oauth2_provider_idtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `jti` char(32) NOT NULL,
  `expires` datetime(6) NOT NULL,
  `scope` longtext NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `application_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jti` (`jti`),
  KEY `oauth2_provider_idto_application_id_08c5ff4f_fk_oauth2_pr` (`application_id`),
  KEY `oauth2_provider_idtoken_user_id_dd512b59_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_idto_application_id_08c5ff4f_fk_oauth2_pr` FOREIGN KEY (`application_id`) REFERENCES `oauth2_provider_application` (`id`),
  CONSTRAINT `oauth2_provider_idtoken_user_id_dd512b59_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oauth2_provider_idtoken`
--

LOCK TABLES `oauth2_provider_idtoken` WRITE;
/*!40000 ALTER TABLE `oauth2_provider_idtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `oauth2_provider_idtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oauth2_provider_refreshtoken`
--

DROP TABLE IF EXISTS `oauth2_provider_refreshtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `oauth2_provider_refreshtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `token` varchar(255) NOT NULL,
  `access_token_id` bigint(20) DEFAULT NULL,
  `application_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `revoked` datetime(6) DEFAULT NULL,
  `token_family` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `access_token_id` (`access_token_id`),
  UNIQUE KEY `oauth2_provider_refreshtoken_token_revoked_af8a5134_uniq` (`token`,`revoked`),
  KEY `oauth2_provider_refr_application_id_2d1c311b_fk_oauth2_pr` (`application_id`),
  KEY `oauth2_provider_refreshtoken_user_id_da837fce_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_refr_access_token_id_775e84e8_fk_oauth2_pr` FOREIGN KEY (`access_token_id`) REFERENCES `oauth2_provider_accesstoken` (`id`),
  CONSTRAINT `oauth2_provider_refr_application_id_2d1c311b_fk_oauth2_pr` FOREIGN KEY (`application_id`) REFERENCES `oauth2_provider_application` (`id`),
  CONSTRAINT `oauth2_provider_refreshtoken_user_id_da837fce_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oauth2_provider_refreshtoken`
--

LOCK TABLES `oauth2_provider_refreshtoken` WRITE;
/*!40000 ALTER TABLE `oauth2_provider_refreshtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `oauth2_provider_refreshtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portal_portalhelppage`
--

DROP TABLE IF EXISTS `portal_portalhelppage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_portalhelppage` (
  `page_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `portal_portalhelppag_page_ptr_id_5de993f1_fk_wagtailco` FOREIGN KEY (`page_ptr_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portal_portalhelppage`
--

LOCK TABLES `portal_portalhelppage` WRITE;
/*!40000 ALTER TABLE `portal_portalhelppage` DISABLE KEYS */;
/*!40000 ALTER TABLE `portal_portalhelppage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portal_portalhelppagesection`
--

DROP TABLE IF EXISTS `portal_portalhelppagesection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_portalhelppagesection` (
  `page_ptr_id` int(11) NOT NULL,
  `parts` longtext NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `portal_portalhelppag_page_ptr_id_c44fa5d6_fk_wagtailco` FOREIGN KEY (`page_ptr_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portal_portalhelppagesection`
--

LOCK TABLES `portal_portalhelppagesection` WRITE;
/*!40000 ALTER TABLE `portal_portalhelppagesection` DISABLE KEYS */;
/*!40000 ALTER TABLE `portal_portalhelppagesection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portal_portalpage`
--

DROP TABLE IF EXISTS `portal_portalpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_portalpage` (
  `page_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `portal_portalpage_page_ptr_id_f8d54997_fk_wagtailcore_page_id` FOREIGN KEY (`page_ptr_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portal_portalpage`
--

LOCK TABLES `portal_portalpage` WRITE;
/*!40000 ALTER TABLE `portal_portalpage` DISABLE KEYS */;
/*!40000 ALTER TABLE `portal_portalpage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portal_tenantadmin`
--

DROP TABLE IF EXISTS `portal_tenantadmin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_tenantadmin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `notes` longtext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `name_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_id` (`name_id`),
  CONSTRAINT `portal_tenantadmin_name_id_b51daa69_fk_geno_address_id` FOREIGN KEY (`name_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portal_tenantadmin`
--

LOCK TABLES `portal_tenantadmin` WRITE;
/*!40000 ALTER TABLE `portal_tenantadmin` DISABLE KEYS */;
/*!40000 ALTER TABLE `portal_tenantadmin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portal_tenantadmin_buildings`
--

DROP TABLE IF EXISTS `portal_tenantadmin_buildings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `portal_tenantadmin_buildings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenantadmin_id` int(11) NOT NULL,
  `building_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `portal_tenantadmin_build_tenantadmin_id_building__0855df23_uniq` (`tenantadmin_id`,`building_id`),
  KEY `portal_tenantadmin_b_building_id_b79e60a7_fk_geno_buil` (`building_id`),
  CONSTRAINT `portal_tenantadmin_b_building_id_b79e60a7_fk_geno_buil` FOREIGN KEY (`building_id`) REFERENCES `geno_building` (`id`),
  CONSTRAINT `portal_tenantadmin_b_tenantadmin_id_f680af2f_fk_portal_te` FOREIGN KEY (`tenantadmin_id`) REFERENCES `portal_tenantadmin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portal_tenantadmin_buildings`
--

LOCK TABLES `portal_tenantadmin_buildings` WRITE;
/*!40000 ALTER TABLE `portal_tenantadmin_buildings` DISABLE KEYS */;
/*!40000 ALTER TABLE `portal_tenantadmin_buildings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_report`
--

DROP TABLE IF EXISTS `report_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(80) NOT NULL,
  `task_id` char(32) DEFAULT NULL,
  `state` varchar(30) NOT NULL,
  `state_info` longtext NOT NULL,
  `report_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_report_name_report_type_id_5c8f7e0d_uniq` (`name`,`report_type_id`),
  KEY `report_report_report_type_id_93f63394_fk_report_reporttype_id` (`report_type_id`),
  CONSTRAINT `report_report_report_type_id_93f63394_fk_report_reporttype_id` FOREIGN KEY (`report_type_id`) REFERENCES `report_reporttype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_report`
--

LOCK TABLES `report_report` WRITE;
/*!40000 ALTER TABLE `report_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_reportinputdata`
--

DROP TABLE IF EXISTS `report_reportinputdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_reportinputdata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `value` longtext NOT NULL,
  `name_id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_reportinputdata_name_id_report_id_30cd96a9_uniq` (`name_id`,`report_id`),
  KEY `report_reportinputdata_report_id_671d129c_fk_report_report_id` (`report_id`),
  CONSTRAINT `report_reportinputda_name_id_f4751f3d_fk_report_re` FOREIGN KEY (`name_id`) REFERENCES `report_reportinputfield` (`id`),
  CONSTRAINT `report_reportinputdata_report_id_671d129c_fk_report_report_id` FOREIGN KEY (`report_id`) REFERENCES `report_report` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_reportinputdata`
--

LOCK TABLES `report_reportinputdata` WRITE;
/*!40000 ALTER TABLE `report_reportinputdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_reportinputdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_reportinputfield`
--

DROP TABLE IF EXISTS `report_reportinputfield`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_reportinputfield` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(80) NOT NULL,
  `description` varchar(200) NOT NULL,
  `field_type` varchar(30) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `report_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_reportinputfield_name_report_type_id_faebfca3_uniq` (`name`,`report_type_id`),
  KEY `report_reportinputfi_report_type_id_9795f889_fk_report_re` (`report_type_id`),
  CONSTRAINT `report_reportinputfi_report_type_id_9795f889_fk_report_re` FOREIGN KEY (`report_type_id`) REFERENCES `report_reporttype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_reportinputfield`
--

LOCK TABLES `report_reportinputfield` WRITE;
/*!40000 ALTER TABLE `report_reportinputfield` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_reportinputfield` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_reportoutput`
--

DROP TABLE IF EXISTS `report_reportoutput`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_reportoutput` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(200) NOT NULL,
  `group` varchar(80) NOT NULL,
  `output_type` varchar(30) NOT NULL,
  `value` longtext NOT NULL,
  `report_id` int(11) NOT NULL,
  `regeneration_json` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_reportoutput_name_report_id_4114ac00_uniq` (`name`,`report_id`),
  KEY `report_reportoutput_report_id_8b66b670_fk_report_report_id` (`report_id`),
  CONSTRAINT `report_reportoutput_report_id_8b66b670_fk_report_report_id` FOREIGN KEY (`report_id`) REFERENCES `report_report` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_reportoutput`
--

LOCK TABLES `report_reportoutput` WRITE;
/*!40000 ALTER TABLE `report_reportoutput` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_reportoutput` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_reporttype`
--

DROP TABLE IF EXISTS `report_reporttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_reporttype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_reporttype`
--

LOCK TABLES `report_reporttype` WRITE;
/*!40000 ALTER TABLE `report_reporttype` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_reporttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_report`
--

DROP TABLE IF EXISTS `reservation_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `contact_text` varchar(300) NOT NULL,
  `text` longtext NOT NULL,
  `report_date` datetime(6) NOT NULL,
  `status_date` datetime(6) NOT NULL,
  `status` varchar(30) NOT NULL,
  `category_id` int(11) NOT NULL,
  `contact_id` int(11) DEFAULT NULL,
  `rental_unit_id` int(11) DEFAULT NULL,
  `report_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `reservation_report_category_id_96fcb70d_fk_reservati` (`category_id`),
  KEY `reservation_report_contact_id_38b48005_fk_geno_address_id` (`contact_id`),
  KEY `reservation_report_rental_unit_id_0ee053ea_fk_geno_rentalunit_id` (`rental_unit_id`),
  KEY `reservation_report_report_type_id_00fcb83b_fk_reservati` (`report_type_id`),
  KEY `reservation_report_status_36e60e3f` (`status`),
  CONSTRAINT `reservation_report_category_id_96fcb70d_fk_reservati` FOREIGN KEY (`category_id`) REFERENCES `reservation_reportcategory` (`id`),
  CONSTRAINT `reservation_report_contact_id_38b48005_fk_geno_address_id` FOREIGN KEY (`contact_id`) REFERENCES `geno_address` (`id`),
  CONSTRAINT `reservation_report_rental_unit_id_0ee053ea_fk_geno_rentalunit_id` FOREIGN KEY (`rental_unit_id`) REFERENCES `geno_rentalunit` (`id`),
  CONSTRAINT `reservation_report_report_type_id_00fcb83b_fk_reservati` FOREIGN KEY (`report_type_id`) REFERENCES `reservation_reporttype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_report`
--

LOCK TABLES `reservation_report` WRITE;
/*!40000 ALTER TABLE `reservation_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reportcategory`
--

DROP TABLE IF EXISTS `reservation_reportcategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reportcategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `report_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reservation_reportcategory_name_report_type_id_fac365b4_uniq` (`name`,`report_type_id`),
  KEY `reservation_reportca_report_type_id_d32c0207_fk_reservati` (`report_type_id`),
  CONSTRAINT `reservation_reportca_report_type_id_d32c0207_fk_reservati` FOREIGN KEY (`report_type_id`) REFERENCES `reservation_reporttype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reportcategory`
--

LOCK TABLES `reservation_reportcategory` WRITE;
/*!40000 ALTER TABLE `reservation_reportcategory` DISABLE KEYS */;
INSERT INTO `reservation_reportcategory` VALUES (1,'','2022-11-28 15:25:51.414000','2022-11-28 15:25:51.414000','[Etwas anderes] (bitte genau beschreiben)',1);
INSERT INTO `reservation_reportcategory` VALUES (2,'','2022-11-28 15:33:44.859000','2022-11-28 15:33:44.859000','Boden',1);
INSERT INTO `reservation_reportcategory` VALUES (3,'','2022-11-28 15:33:55.201000','2022-11-28 15:33:55.201000','Decke',1);
INSERT INTO `reservation_reportcategory` VALUES (4,'','2022-11-28 15:34:00.789000','2022-11-28 15:34:00.789000','Wände',1);
INSERT INTO `reservation_reportcategory` VALUES (5,'','2022-11-28 15:34:11.629000','2022-11-28 15:34:11.629000','Fenster',1);
INSERT INTO `reservation_reportcategory` VALUES (6,'','2022-11-28 15:34:16.456000','2022-11-28 15:34:16.456000','Türen',1);
INSERT INTO `reservation_reportcategory` VALUES (7,'','2022-11-28 15:34:41.205000','2022-11-28 15:34:41.205000','Storen',1);
INSERT INTO `reservation_reportcategory` VALUES (8,'','2022-11-28 15:34:46.779000','2022-11-28 15:34:46.779000','Balkon',1);
INSERT INTO `reservation_reportcategory` VALUES (9,'','2022-11-28 15:34:56.157000','2022-11-28 15:34:56.157000','Elektrische Installationen',1);
INSERT INTO `reservation_reportcategory` VALUES (10,'','2022-11-28 15:35:20.213000','2022-11-28 15:35:20.213000','Küche - Herd/Backofen',1);
INSERT INTO `reservation_reportcategory` VALUES (11,'','2022-11-28 15:35:35.864000','2022-11-28 15:35:35.864000','Küche - Kühlschrank',1);
INSERT INTO `reservation_reportcategory` VALUES (12,'','2022-11-28 15:35:45.514000','2022-11-28 15:35:45.514000','Küche - Abwaschmaschine',1);
INSERT INTO `reservation_reportcategory` VALUES (13,'','2022-11-28 15:36:19.289000','2022-11-28 15:36:19.289000','Küche - Einbauten/Anderes',1);
INSERT INTO `reservation_reportcategory` VALUES (14,'','2022-11-28 15:36:42.770000','2022-11-28 15:36:42.770000','Bad - Dusche/Badewanne',1);
INSERT INTO `reservation_reportcategory` VALUES (15,'','2022-11-28 15:36:49.675000','2022-11-28 15:36:49.675000','Bad - Lavabo',1);
INSERT INTO `reservation_reportcategory` VALUES (16,'','2022-11-28 15:37:12.800000','2022-11-28 15:37:12.801000','Bad - WC',1);
INSERT INTO `reservation_reportcategory` VALUES (17,'','2022-11-28 15:37:32.395000','2022-11-28 15:37:32.395000','Bad - Diverses',1);
INSERT INTO `reservation_reportcategory` VALUES (18,'','2022-11-28 15:39:43.304000','2022-11-28 15:39:43.304000','Küche - Abwaschbecken',1);
INSERT INTO `reservation_reportcategory` VALUES (19,'','2022-12-16 15:03:02.579000','2022-12-16 15:03:02.579000','Heizung',1);
INSERT INTO `reservation_reportcategory` VALUES (20,'','2022-12-16 15:03:20.547000','2022-12-16 15:03:20.547000','Lüftung',1);
INSERT INTO `reservation_reportcategory` VALUES (21,'','2024-02-27 08:51:34.966000','2024-02-27 08:51:34.966000','Brandschutzeinrichtungen',1);
/*!40000 ALTER TABLE `reservation_reportcategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reportlogentry`
--

DROP TABLE IF EXISTS `reservation_reportlogentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reportlogentry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `text` longtext NOT NULL,
  `name_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `reservation_reportlo_name_id_d7818d12_fk_reservati` (`name_id`),
  KEY `reservation_reportlogentry_user_id_02371677_fk_auth_user_id` (`user_id`),
  CONSTRAINT `reservation_reportlo_name_id_d7818d12_fk_reservati` FOREIGN KEY (`name_id`) REFERENCES `reservation_report` (`id`),
  CONSTRAINT `reservation_reportlogentry_user_id_02371677_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reportlogentry`
--

LOCK TABLES `reservation_reportlogentry` WRITE;
/*!40000 ALTER TABLE `reservation_reportlogentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_reportlogentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reportpicture`
--

DROP TABLE IF EXISTS `reservation_reportpicture`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reportpicture` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `image` varchar(100) NOT NULL,
  `report_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reservation_reportpicture_image_report_id_69b14c97_uniq` (`image`,`report_id`),
  KEY `reservation_reportpi_report_id_75224f5e_fk_reservati` (`report_id`),
  CONSTRAINT `reservation_reportpi_report_id_75224f5e_fk_reservati` FOREIGN KEY (`report_id`) REFERENCES `reservation_report` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reportpicture`
--

LOCK TABLES `reservation_reportpicture` WRITE;
/*!40000 ALTER TABLE `reservation_reportpicture` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_reportpicture` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reporttype`
--

DROP TABLE IF EXISTS `reservation_reporttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reporttype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reporttype`
--

LOCK TABLES `reservation_reporttype` WRITE;
/*!40000 ALTER TABLE `reservation_reporttype` DISABLE KEYS */;
INSERT INTO `reservation_reporttype` VALUES (1,'','2022-11-28 15:25:46.913000','2022-11-28 15:25:46.913000','Reparaturmeldung');
/*!40000 ALTER TABLE `reservation_reporttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reservation`
--

DROP TABLE IF EXISTS `reservation_reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reservation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `date_start` datetime(6) NOT NULL,
  `date_end` datetime(6) NOT NULL,
  `state` varchar(30) NOT NULL,
  `key_number` varchar(10) NOT NULL,
  `key_back` tinyint(1) NOT NULL,
  `billed` tinyint(1) NOT NULL,
  `additional_information` longtext NOT NULL,
  `contact_id` int(11) NOT NULL,
  `contact_text` varchar(200) NOT NULL,
  `flink_id` varchar(20) DEFAULT NULL,
  `flink_user_id` int(11) DEFAULT NULL,
  `remark` longtext NOT NULL,
  `name_id` int(11) NOT NULL,
  `is_auto_blocker` tinyint(1) NOT NULL,
  `summary` varchar(120) NOT NULL,
  `usage_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `flink_id` (`flink_id`),
  KEY `reservation_reservation_contact_id_06789970_fk_geno_address_id` (`contact_id`),
  KEY `reservation_reservation_state_61cce512` (`state`),
  KEY `reservation_reservat_name_id_1b4c1387_fk_reservati` (`name_id`),
  KEY `reservation_reservat_usage_type_id_18af0537_fk_reservati` (`usage_type_id`),
  CONSTRAINT `reservation_reservat_name_id_1b4c1387_fk_reservati` FOREIGN KEY (`name_id`) REFERENCES `reservation_reservationobject` (`id`),
  CONSTRAINT `reservation_reservat_usage_type_id_18af0537_fk_reservati` FOREIGN KEY (`usage_type_id`) REFERENCES `reservation_reservationusagetype` (`id`),
  CONSTRAINT `reservation_reservation_contact_id_06789970_fk_geno_address_id` FOREIGN KEY (`contact_id`) REFERENCES `geno_address` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reservation`
--

LOCK TABLES `reservation_reservation` WRITE;
/*!40000 ALTER TABLE `reservation_reservation` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_reservation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reservationobject`
--

DROP TABLE IF EXISTS `reservation_reservationobject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reservationobject` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(80) NOT NULL,
  `short_description` varchar(300) NOT NULL,
  `description` longtext NOT NULL,
  `image` varchar(100) NOT NULL,
  `cost` decimal(7,2) NOT NULL,
  `reservation_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reservation_reservationo_name_reservation_type_id_8c1a7735_uniq` (`name`,`reservation_type_id`),
  KEY `reservation_reservat_reservation_type_id_057c2f3f_fk_reservati` (`reservation_type_id`),
  CONSTRAINT `reservation_reservat_reservation_type_id_057c2f3f_fk_reservati` FOREIGN KEY (`reservation_type_id`) REFERENCES `reservation_reservationtype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reservationobject`
--

LOCK TABLES `reservation_reservationobject` WRITE;
/*!40000 ALTER TABLE `reservation_reservationobject` DISABLE KEYS */;
INSERT INTO `reservation_reservationobject` VALUES (1,'','2025-08-27 11:19:24.378263','2025-08-27 11:25:00.199666','Gästezimmer A','Kleines Gästezimmer','Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.','reservation/images/bedroom-guest-room-sleep-0ac3e7-1024.jpg',50.00,1);
INSERT INTO `reservation_reservationobject` VALUES (2,'','2025-08-27 11:19:53.286887','2025-08-27 11:24:52.490912','Gästezimmer B','Grosses Gästezimmer','Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.','reservation/images/pexels-jahangir-alam-jahan-279240197-13008559.jpg',75.00,1);
INSERT INTO `reservation_reservationobject` VALUES (3,'','2025-08-27 11:26:04.629816','2025-08-27 11:26:04.629855','Sitzungszimmer klein','bis 6 Personen','Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.','',0.00,2);
INSERT INTO `reservation_reservationobject` VALUES (4,'','2025-08-27 11:26:19.681309','2025-08-27 11:26:19.681343','Sitzungszimmer gross','Bis 12 Personen','Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.','',0.00,2);
/*!40000 ALTER TABLE `reservation_reservationobject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reservationobject_usage_types`
--

DROP TABLE IF EXISTS `reservation_reservationobject_usage_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reservationobject_usage_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reservationobject_id` int(11) NOT NULL,
  `reservationusagetype_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reservation_reservationo_reservationobject_id_res_24b727b4_uniq` (`reservationobject_id`,`reservationusagetype_id`),
  KEY `reservation_reservat_reservationusagetype_c00413c2_fk_reservati` (`reservationusagetype_id`),
  CONSTRAINT `reservation_reservat_reservationobject_id_3b94f308_fk_reservati` FOREIGN KEY (`reservationobject_id`) REFERENCES `reservation_reservationobject` (`id`),
  CONSTRAINT `reservation_reservat_reservationusagetype_c00413c2_fk_reservati` FOREIGN KEY (`reservationusagetype_id`) REFERENCES `reservation_reservationusagetype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reservationobject_usage_types`
--

LOCK TABLES `reservation_reservationobject_usage_types` WRITE;
/*!40000 ALTER TABLE `reservation_reservationobject_usage_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_reservationobject_usage_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reservationprice`
--

DROP TABLE IF EXISTS `reservation_reservationprice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reservationprice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `priority` int(11) NOT NULL,
  `time_unit` varchar(20) NOT NULL,
  `duration_min` double NOT NULL,
  `duration_max` double NOT NULL,
  `cost` decimal(7,2) NOT NULL,
  `cost_type` varchar(20) NOT NULL,
  `usage_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reservation_reservationp_usage_type_id_priority_7a17000d_uniq` (`usage_type_id`,`priority`),
  CONSTRAINT `reservation_reservat_usage_type_id_26f207cb_fk_reservati` FOREIGN KEY (`usage_type_id`) REFERENCES `reservation_reservationusagetype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reservationprice`
--

LOCK TABLES `reservation_reservationprice` WRITE;
/*!40000 ALTER TABLE `reservation_reservationprice` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_reservationprice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reservationtype`
--

DROP TABLE IF EXISTS `reservation_reservationtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reservationtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `default_time_end` time(6) NOT NULL,
  `default_time_start` time(6) NOT NULL,
  `fixed_time` tinyint(1) NOT NULL,
  `summary_required` tinyint(1) NOT NULL,
  `color` varchar(7) NOT NULL,
  `confirmation_email_sender` varchar(100) NOT NULL,
  `confirmation_email_template_id` int(11) DEFAULT NULL,
  `required_role` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reservation_reservationtype_name_7dd5be9d_uniq` (`name`),
  KEY `reservation_reservat_confirmation_email_t_50ce5e64_fk_geno_cont` (`confirmation_email_template_id`),
  CONSTRAINT `reservation_reservat_confirmation_email_t_50ce5e64_fk_geno_cont` FOREIGN KEY (`confirmation_email_template_id`) REFERENCES `geno_contenttemplate` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reservationtype`
--

LOCK TABLES `reservation_reservationtype` WRITE;
/*!40000 ALTER TABLE `reservation_reservationtype` DISABLE KEYS */;
INSERT INTO `reservation_reservationtype` VALUES (1,'','2025-08-27 11:17:35.252987','2025-08-27 11:17:35.253017','Gästezimmer',1,'12:00:00.000000','14:00:00.000000',1,0,'#7d7d78','admin@example.com',NULL,'renter');
INSERT INTO `reservation_reservationtype` VALUES (2,'','2025-08-27 11:25:36.501129','2025-08-27 11:25:36.501153','Sitzungszimmer',1,'12:00:00.000000','10:00:00.000000',0,1,'#ff7d78','admin@example.com',NULL,'user');
/*!40000 ALTER TABLE `reservation_reservationtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation_reservationusagetype`
--

DROP TABLE IF EXISTS `reservation_reservationusagetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation_reservationusagetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(500) NOT NULL,
  `ts_created` datetime(6) NOT NULL,
  `ts_modified` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `label` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation_reservationusagetype`
--

LOCK TABLES `reservation_reservationusagetype` WRITE;
/*!40000 ALTER TABLE `reservation_reservationusagetype` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation_reservationusagetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `taggit_tag`
--

DROP TABLE IF EXISTS `taggit_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `taggit_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `slug` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `taggit_tag`
--

LOCK TABLES `taggit_tag` WRITE;
/*!40000 ALTER TABLE `taggit_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `taggit_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `taggit_taggeditem`
--

DROP TABLE IF EXISTS `taggit_taggeditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `taggit_taggeditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taggit_taggeditem_content_type_id_object_id_tag_id_4bb97a8e_uniq` (`content_type_id`,`object_id`,`tag_id`),
  KEY `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` (`tag_id`),
  KEY `taggit_taggeditem_object_id_e2d7d1df` (`object_id`),
  KEY `taggit_taggeditem_content_type_id_object_id_196cc965_idx` (`content_type_id`,`object_id`),
  CONSTRAINT `taggit_taggeditem_content_type_id_9957a03c_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `taggit_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `taggit_taggeditem`
--

LOCK TABLES `taggit_taggeditem` WRITE;
/*!40000 ALTER TABLE `taggit_taggeditem` DISABLE KEYS */;
/*!40000 ALTER TABLE `taggit_taggeditem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailadmin_admin`
--

DROP TABLE IF EXISTS `wagtailadmin_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailadmin_admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailadmin_admin`
--

LOCK TABLES `wagtailadmin_admin` WRITE;
/*!40000 ALTER TABLE `wagtailadmin_admin` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailadmin_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_collection`
--

DROP TABLE IF EXISTS `wagtailcore_collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_collection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(255) NOT NULL,
  `depth` int(10) unsigned NOT NULL,
  `numchild` int(10) unsigned NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `path` (`path`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_collection`
--

LOCK TABLES `wagtailcore_collection` WRITE;
/*!40000 ALTER TABLE `wagtailcore_collection` DISABLE KEYS */;
INSERT INTO `wagtailcore_collection` VALUES (1,'0001',1,0,'Root');
/*!40000 ALTER TABLE `wagtailcore_collection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_collectionviewrestriction`
--

DROP TABLE IF EXISTS `wagtailcore_collectionviewrestriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_collectionviewrestriction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `restriction_type` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `collection_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_collecti_collection_id_761908ec_fk_wagtailco` (`collection_id`),
  CONSTRAINT `wagtailcore_collecti_collection_id_761908ec_fk_wagtailco` FOREIGN KEY (`collection_id`) REFERENCES `wagtailcore_collection` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_collectionviewrestriction`
--

LOCK TABLES `wagtailcore_collectionviewrestriction` WRITE;
/*!40000 ALTER TABLE `wagtailcore_collectionviewrestriction` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_collectionviewrestriction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_collectionviewrestriction_groups`
--

DROP TABLE IF EXISTS `wagtailcore_collectionviewrestriction_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_collectionviewrestriction_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `collectionviewrestriction_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_collectionvi_collectionviewrestrictio_988995ae_uniq` (`collectionviewrestriction_id`,`group_id`),
  KEY `wagtailcore_collecti_group_id_1823f2a3_fk_auth_grou` (`group_id`),
  CONSTRAINT `wagtailcore_collecti_collectionviewrestri_47320efd_fk_wagtailco` FOREIGN KEY (`collectionviewrestriction_id`) REFERENCES `wagtailcore_collectionviewrestriction` (`id`),
  CONSTRAINT `wagtailcore_collecti_group_id_1823f2a3_fk_auth_grou` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_collectionviewrestriction_groups`
--

LOCK TABLES `wagtailcore_collectionviewrestriction_groups` WRITE;
/*!40000 ALTER TABLE `wagtailcore_collectionviewrestriction_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_collectionviewrestriction_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_comment`
--

DROP TABLE IF EXISTS `wagtailcore_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` longtext NOT NULL,
  `contentpath` longtext NOT NULL,
  `position` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `resolved_at` datetime(6) DEFAULT NULL,
  `page_id` int(11) NOT NULL,
  `resolved_by_id` int(11) DEFAULT NULL,
  `revision_created_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_comment_resolved_by_id_a282aa0e_fk_auth_user_id` (`resolved_by_id`),
  KEY `wagtailcore_comment_revision_created_id_1d058279_fk_wagtailco` (`revision_created_id`),
  KEY `wagtailcore_comment_user_id_0c577ca6_fk_auth_user_id` (`user_id`),
  KEY `wagtailcore_comment_page_id_108444b5` (`page_id`),
  CONSTRAINT `wagtailcore_comment_page_id_108444b5_fk_wagtailcore_page_id` FOREIGN KEY (`page_id`) REFERENCES `wagtailcore_page` (`id`),
  CONSTRAINT `wagtailcore_comment_resolved_by_id_a282aa0e_fk_auth_user_id` FOREIGN KEY (`resolved_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `wagtailcore_comment_revision_created_id_1d058279_fk_wagtailco` FOREIGN KEY (`revision_created_id`) REFERENCES `wagtailcore_revision` (`id`),
  CONSTRAINT `wagtailcore_comment_user_id_0c577ca6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_comment`
--

LOCK TABLES `wagtailcore_comment` WRITE;
/*!40000 ALTER TABLE `wagtailcore_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_commentreply`
--

DROP TABLE IF EXISTS `wagtailcore_commentreply`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_commentreply` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `comment_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_commentreply_user_id_d0b3b9c3_fk_auth_user_id` (`user_id`),
  KEY `wagtailcore_commentreply_comment_id_afc7e027` (`comment_id`),
  CONSTRAINT `wagtailcore_commentr_comment_id_afc7e027_fk_wagtailco` FOREIGN KEY (`comment_id`) REFERENCES `wagtailcore_comment` (`id`),
  CONSTRAINT `wagtailcore_commentreply_user_id_d0b3b9c3_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_commentreply`
--

LOCK TABLES `wagtailcore_commentreply` WRITE;
/*!40000 ALTER TABLE `wagtailcore_commentreply` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_commentreply` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_groupapprovaltask`
--

DROP TABLE IF EXISTS `wagtailcore_groupapprovaltask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_groupapprovaltask` (
  `task_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`task_ptr_id`),
  CONSTRAINT `wagtailcore_groupapp_task_ptr_id_cfe58781_fk_wagtailco` FOREIGN KEY (`task_ptr_id`) REFERENCES `wagtailcore_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_groupapprovaltask`
--

LOCK TABLES `wagtailcore_groupapprovaltask` WRITE;
/*!40000 ALTER TABLE `wagtailcore_groupapprovaltask` DISABLE KEYS */;
INSERT INTO `wagtailcore_groupapprovaltask` VALUES (1);
/*!40000 ALTER TABLE `wagtailcore_groupapprovaltask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_groupapprovaltask_groups`
--

DROP TABLE IF EXISTS `wagtailcore_groupapprovaltask_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_groupapprovaltask_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `groupapprovaltask_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_groupapprova_groupapprovaltask_id_gro_bb5ee7eb_uniq` (`groupapprovaltask_id`,`group_id`),
  KEY `wagtailcore_groupapp_group_id_2e64b61f_fk_auth_grou` (`group_id`),
  CONSTRAINT `wagtailcore_groupapp_group_id_2e64b61f_fk_auth_grou` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `wagtailcore_groupapp_groupapprovaltask_id_9a9255ea_fk_wagtailco` FOREIGN KEY (`groupapprovaltask_id`) REFERENCES `wagtailcore_groupapprovaltask` (`task_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_groupapprovaltask_groups`
--

LOCK TABLES `wagtailcore_groupapprovaltask_groups` WRITE;
/*!40000 ALTER TABLE `wagtailcore_groupapprovaltask_groups` DISABLE KEYS */;
INSERT INTO `wagtailcore_groupapprovaltask_groups` VALUES (1,1,1);
/*!40000 ALTER TABLE `wagtailcore_groupapprovaltask_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_groupcollectionpermission`
--

DROP TABLE IF EXISTS `wagtailcore_groupcollectionpermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_groupcollectionpermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `collection_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_groupcollect_group_id_collection_id_p_a21cefe9_uniq` (`group_id`,`collection_id`,`permission_id`),
  KEY `wagtailcore_groupcol_collection_id_5423575a_fk_wagtailco` (`collection_id`),
  KEY `wagtailcore_groupcol_permission_id_1b626275_fk_auth_perm` (`permission_id`),
  CONSTRAINT `wagtailcore_groupcol_collection_id_5423575a_fk_wagtailco` FOREIGN KEY (`collection_id`) REFERENCES `wagtailcore_collection` (`id`),
  CONSTRAINT `wagtailcore_groupcol_group_id_05d61460_fk_auth_grou` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `wagtailcore_groupcol_permission_id_1b626275_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_groupcollectionpermission`
--

LOCK TABLES `wagtailcore_groupcollectionpermission` WRITE;
/*!40000 ALTER TABLE `wagtailcore_groupcollectionpermission` DISABLE KEYS */;
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (2,1,1,2);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (4,1,1,3);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (6,1,1,5);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (8,1,1,6);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (10,1,1,7);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (12,1,1,9);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (1,1,2,2);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (3,1,2,3);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (5,1,2,5);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (7,1,2,6);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (9,1,2,7);
INSERT INTO `wagtailcore_groupcollectionpermission` VALUES (11,1,2,9);
/*!40000 ALTER TABLE `wagtailcore_groupcollectionpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_grouppagepermission`
--

DROP TABLE IF EXISTS `wagtailcore_grouppagepermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_grouppagepermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `permission_type` varchar(20) DEFAULT NULL,
  `group_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  `permission_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_permission` (`group_id`,`page_id`,`permission_id`),
  UNIQUE KEY `unique_permission_type` (`group_id`,`page_id`,`permission_type`),
  KEY `wagtailcore_grouppag_page_id_710b114a_fk_wagtailco` (`page_id`),
  KEY `wagtailcore_grouppag_permission_id_05acb22e_fk_auth_perm` (`permission_id`),
  KEY `wagtailcore_grouppagepermission_group_id_fc07e671` (`group_id`),
  CONSTRAINT `wagtailcore_grouppag_group_id_fc07e671_fk_auth_grou` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `wagtailcore_grouppag_page_id_710b114a_fk_wagtailco` FOREIGN KEY (`page_id`) REFERENCES `wagtailcore_page` (`id`),
  CONSTRAINT `wagtailcore_grouppag_permission_id_05acb22e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `permission_or_permission_type_not_null` CHECK (`permission_id` is not null or `permission_type` is not null)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_grouppagepermission`
--

LOCK TABLES `wagtailcore_grouppagepermission` WRITE;
/*!40000 ALTER TABLE `wagtailcore_grouppagepermission` DISABLE KEYS */;
INSERT INTO `wagtailcore_grouppagepermission` VALUES (1,'add',1,1,236);
INSERT INTO `wagtailcore_grouppagepermission` VALUES (2,'change',1,1,237);
INSERT INTO `wagtailcore_grouppagepermission` VALUES (3,'publish',1,1,466);
INSERT INTO `wagtailcore_grouppagepermission` VALUES (4,'add',2,1,236);
INSERT INTO `wagtailcore_grouppagepermission` VALUES (5,'change',2,1,237);
INSERT INTO `wagtailcore_grouppagepermission` VALUES (6,'lock',1,1,465);
INSERT INTO `wagtailcore_grouppagepermission` VALUES (7,'unlock',1,1,467);
/*!40000 ALTER TABLE `wagtailcore_grouppagepermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_locale`
--

DROP TABLE IF EXISTS `wagtailcore_locale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_locale` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `language_code` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `language_code` (`language_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_locale`
--

LOCK TABLES `wagtailcore_locale` WRITE;
/*!40000 ALTER TABLE `wagtailcore_locale` DISABLE KEYS */;
INSERT INTO `wagtailcore_locale` VALUES (1,'de');
/*!40000 ALTER TABLE `wagtailcore_locale` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_modellogentry`
--

DROP TABLE IF EXISTS `wagtailcore_modellogentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_modellogentry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` longtext NOT NULL,
  `action` varchar(255) NOT NULL,
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`data`)),
  `timestamp` datetime(6) NOT NULL,
  `content_changed` tinyint(1) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `uuid` char(32) DEFAULT NULL,
  `revision_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_modellog_content_type_id_68849e77_fk_django_co` (`content_type_id`),
  KEY `wagtailcore_modellogentry_action_d2d856ee` (`action`),
  KEY `wagtailcore_modellogentry_content_changed_8bc39742` (`content_changed`),
  KEY `wagtailcore_modellogentry_object_id_e0e7d4ef` (`object_id`),
  KEY `wagtailcore_modellogentry_user_id_0278d1bf` (`user_id`),
  KEY `wagtailcore_modellogentry_timestamp_9694521b` (`timestamp`),
  KEY `wagtailcore_modellogentry_revision_id_df6ca33a` (`revision_id`),
  CONSTRAINT `wagtailcore_modellog_content_type_id_68849e77_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_modellogentry`
--

LOCK TABLES `wagtailcore_modellogentry` WRITE;
/*!40000 ALTER TABLE `wagtailcore_modellogentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_modellogentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_page`
--

DROP TABLE IF EXISTS `wagtailcore_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(255) NOT NULL,
  `depth` int(10) unsigned NOT NULL,
  `numchild` int(10) unsigned NOT NULL,
  `title` varchar(255) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `live` tinyint(1) NOT NULL,
  `has_unpublished_changes` tinyint(1) NOT NULL,
  `url_path` longtext NOT NULL,
  `seo_title` varchar(255) NOT NULL,
  `show_in_menus` tinyint(1) NOT NULL,
  `search_description` longtext NOT NULL,
  `go_live_at` datetime(6) DEFAULT NULL,
  `expire_at` datetime(6) DEFAULT NULL,
  `expired` tinyint(1) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `locked` tinyint(1) NOT NULL,
  `latest_revision_created_at` datetime(6) DEFAULT NULL,
  `first_published_at` datetime(6) DEFAULT NULL,
  `live_revision_id` int(11) DEFAULT NULL,
  `last_published_at` datetime(6) DEFAULT NULL,
  `draft_title` varchar(255) NOT NULL,
  `locked_at` datetime(6) DEFAULT NULL,
  `locked_by_id` int(11) DEFAULT NULL,
  `translation_key` char(32) NOT NULL,
  `locale_id` int(11) NOT NULL,
  `alias_of_id` int(11) DEFAULT NULL,
  `latest_revision_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `path` (`path`),
  UNIQUE KEY `wagtailcore_page_translation_key_locale_id_9b041bad_uniq` (`translation_key`,`locale_id`),
  KEY `wagtailcore_page_slug_e7c11b8f` (`slug`),
  KEY `wagtailcore_page_first_published_at_2b5dd637` (`first_published_at`),
  KEY `wagtailcore_page_content_type_id_c28424df_fk_django_co` (`content_type_id`),
  KEY `wagtailcore_page_live_revision_id_930bd822_fk_wagtailco` (`live_revision_id`),
  KEY `wagtailcore_page_owner_id_fbf7c332_fk_auth_user_id` (`owner_id`),
  KEY `wagtailcore_page_locked_by_id_bcb86245_fk_auth_user_id` (`locked_by_id`),
  KEY `wagtailcore_page_locale_id_3c7e30a6_fk_wagtailcore_locale_id` (`locale_id`),
  KEY `wagtailcore_page_alias_of_id_12945502_fk_wagtailcore_page_id` (`alias_of_id`),
  KEY `wagtailcore_page_latest_revision_id_e60fef51_fk_wagtailco` (`latest_revision_id`),
  CONSTRAINT `wagtailcore_page_alias_of_id_12945502_fk_wagtailcore_page_id` FOREIGN KEY (`alias_of_id`) REFERENCES `wagtailcore_page` (`id`),
  CONSTRAINT `wagtailcore_page_content_type_id_c28424df_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_page_latest_revision_id_e60fef51_fk_wagtailco` FOREIGN KEY (`latest_revision_id`) REFERENCES `wagtailcore_revision` (`id`),
  CONSTRAINT `wagtailcore_page_live_revision_id_930bd822_fk_wagtailco` FOREIGN KEY (`live_revision_id`) REFERENCES `wagtailcore_revision` (`id`),
  CONSTRAINT `wagtailcore_page_locale_id_3c7e30a6_fk_wagtailcore_locale_id` FOREIGN KEY (`locale_id`) REFERENCES `wagtailcore_locale` (`id`),
  CONSTRAINT `wagtailcore_page_locked_by_id_bcb86245_fk_auth_user_id` FOREIGN KEY (`locked_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `wagtailcore_page_owner_id_fbf7c332_fk_auth_user_id` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_page`
--

LOCK TABLES `wagtailcore_page` WRITE;
/*!40000 ALTER TABLE `wagtailcore_page` DISABLE KEYS */;
INSERT INTO `wagtailcore_page` VALUES (1,'0001',1,1,'Root','root',1,0,'/','',0,'',NULL,NULL,0,1,NULL,0,NULL,NULL,NULL,NULL,'Root',NULL,NULL,'541621eba1e84e0bbe93230375767c5c',1,NULL,NULL);
INSERT INTO `wagtailcore_page` VALUES (2,'00010001',2,0,'Welcome to your new Wagtail site!','home',1,0,'/home/','',0,'',NULL,NULL,0,1,NULL,0,NULL,NULL,NULL,NULL,'Welcome to your new Wagtail site!',NULL,NULL,'98da7eb299194fc08fdd190133f55898',1,NULL,NULL);
/*!40000 ALTER TABLE `wagtailcore_page` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_pagelogentry`
--

DROP TABLE IF EXISTS `wagtailcore_pagelogentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_pagelogentry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` longtext NOT NULL,
  `action` varchar(255) NOT NULL,
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`data`)),
  `timestamp` datetime(6) NOT NULL,
  `content_changed` tinyint(1) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `page_id` int(11) NOT NULL,
  `revision_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `uuid` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_pageloge_content_type_id_74e7708a_fk_django_co` (`content_type_id`),
  KEY `wagtailcore_pagelogentry_action_c2408198` (`action`),
  KEY `wagtailcore_pagelogentry_content_changed_99f27ade` (`content_changed`),
  KEY `wagtailcore_pagelogentry_page_id_8464e327` (`page_id`),
  KEY `wagtailcore_pagelogentry_revision_id_8043d103` (`revision_id`),
  KEY `wagtailcore_pagelogentry_user_id_604ccfd8` (`user_id`),
  KEY `wagtailcore_pagelogentry_timestamp_deb774c4` (`timestamp`),
  CONSTRAINT `wagtailcore_pageloge_content_type_id_74e7708a_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_pagelogentry`
--

LOCK TABLES `wagtailcore_pagelogentry` WRITE;
/*!40000 ALTER TABLE `wagtailcore_pagelogentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_pagelogentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_pagesubscription`
--

DROP TABLE IF EXISTS `wagtailcore_pagesubscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_pagesubscription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment_notifications` tinyint(1) NOT NULL,
  `page_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_pagesubscription_page_id_user_id_0cef73ed_uniq` (`page_id`,`user_id`),
  KEY `wagtailcore_pagesubscription_user_id_89d7def9_fk_auth_user_id` (`user_id`),
  CONSTRAINT `wagtailcore_pagesubs_page_id_a085e7a6_fk_wagtailco` FOREIGN KEY (`page_id`) REFERENCES `wagtailcore_page` (`id`),
  CONSTRAINT `wagtailcore_pagesubscription_user_id_89d7def9_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_pagesubscription`
--

LOCK TABLES `wagtailcore_pagesubscription` WRITE;
/*!40000 ALTER TABLE `wagtailcore_pagesubscription` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_pagesubscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_pageviewrestriction`
--

DROP TABLE IF EXISTS `wagtailcore_pageviewrestriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_pageviewrestriction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(255) NOT NULL,
  `page_id` int(11) NOT NULL,
  `restriction_type` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_pageview_page_id_15a8bea6_fk_wagtailco` (`page_id`),
  CONSTRAINT `wagtailcore_pageview_page_id_15a8bea6_fk_wagtailco` FOREIGN KEY (`page_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_pageviewrestriction`
--

LOCK TABLES `wagtailcore_pageviewrestriction` WRITE;
/*!40000 ALTER TABLE `wagtailcore_pageviewrestriction` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_pageviewrestriction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_pageviewrestriction_groups`
--

DROP TABLE IF EXISTS `wagtailcore_pageviewrestriction_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_pageviewrestriction_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pageviewrestriction_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_pageviewrest_pageviewrestriction_id_g_d23f80bb_uniq` (`pageviewrestriction_id`,`group_id`),
  KEY `wagtailcore_pageview_group_id_6460f223_fk_auth_grou` (`group_id`),
  CONSTRAINT `wagtailcore_pageview_group_id_6460f223_fk_auth_grou` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `wagtailcore_pageview_pageviewrestriction__f147a99a_fk_wagtailco` FOREIGN KEY (`pageviewrestriction_id`) REFERENCES `wagtailcore_pageviewrestriction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_pageviewrestriction_groups`
--

LOCK TABLES `wagtailcore_pageviewrestriction_groups` WRITE;
/*!40000 ALTER TABLE `wagtailcore_pageviewrestriction_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_pageviewrestriction_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_referenceindex`
--

DROP TABLE IF EXISTS `wagtailcore_referenceindex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_referenceindex` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_id` varchar(255) NOT NULL,
  `to_object_id` varchar(255) NOT NULL,
  `model_path` longtext NOT NULL,
  `content_path` longtext NOT NULL,
  `content_path_hash` char(32) NOT NULL,
  `base_content_type_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `to_content_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_referenceind_base_content_type_id_obj_9e6ccd6a_uniq` (`base_content_type_id`,`object_id`,`to_content_type_id`,`to_object_id`,`content_path_hash`),
  KEY `wagtailcore_referenc_content_type_id_766e0336_fk_django_co` (`content_type_id`),
  KEY `wagtailcore_referenc_to_content_type_id_93690bbd_fk_django_co` (`to_content_type_id`),
  CONSTRAINT `wagtailcore_referenc_base_content_type_id_313cf40f_fk_django_co` FOREIGN KEY (`base_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_referenc_content_type_id_766e0336_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_referenc_to_content_type_id_93690bbd_fk_django_co` FOREIGN KEY (`to_content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_referenceindex`
--

LOCK TABLES `wagtailcore_referenceindex` WRITE;
/*!40000 ALTER TABLE `wagtailcore_referenceindex` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_referenceindex` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_revision`
--

DROP TABLE IF EXISTS `wagtailcore_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_revision` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `submitted_for_moderation` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`content`)),
  `approved_go_live_at` datetime(6) DEFAULT NULL,
  `object_id` varchar(255) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `content_type_id` int(11) NOT NULL,
  `base_content_type_id` int(11) NOT NULL,
  `object_str` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_pagerevision_submitted_for_moderation_c682e44c` (`submitted_for_moderation`),
  KEY `wagtailcore_pagerevision_user_id_2409d2f4_fk_auth_user_id` (`user_id`),
  KEY `wagtailcore_pagerevision_created_at_66954e3b` (`created_at`),
  KEY `wagtailcore_pagerevision_approved_go_live_at_e56afc67` (`approved_go_live_at`),
  KEY `content_object_idx` (`content_type_id`,`object_id`),
  KEY `base_content_object_idx` (`base_content_type_id`,`object_id`),
  CONSTRAINT `wagtailcore_pagerevision_user_id_2409d2f4_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `wagtailcore_revision_base_content_type_id_5b4ef7bd_fk_django_co` FOREIGN KEY (`base_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_revision_content_type_id_c8cb69c0_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_revision`
--

LOCK TABLES `wagtailcore_revision` WRITE;
/*!40000 ALTER TABLE `wagtailcore_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_revision` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_site`
--

DROP TABLE IF EXISTS `wagtailcore_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) NOT NULL,
  `port` int(11) NOT NULL,
  `is_default_site` tinyint(1) NOT NULL,
  `root_page_id` int(11) NOT NULL,
  `site_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_site_hostname_port_2c626d70_uniq` (`hostname`,`port`),
  KEY `wagtailcore_site_hostname_96b20b46` (`hostname`),
  KEY `wagtailcore_site_root_page_id_e02fb95c_fk_wagtailcore_page_id` (`root_page_id`),
  CONSTRAINT `wagtailcore_site_root_page_id_e02fb95c_fk_wagtailcore_page_id` FOREIGN KEY (`root_page_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_site`
--

LOCK TABLES `wagtailcore_site` WRITE;
/*!40000 ALTER TABLE `wagtailcore_site` DISABLE KEYS */;
INSERT INTO `wagtailcore_site` VALUES (1,'localhost',80,1,2,'');
/*!40000 ALTER TABLE `wagtailcore_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_task`
--

DROP TABLE IF EXISTS `wagtailcore_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_task_content_type_id_249ab8ba_fk_django_co` (`content_type_id`),
  CONSTRAINT `wagtailcore_task_content_type_id_249ab8ba_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_task`
--

LOCK TABLES `wagtailcore_task` WRITE;
/*!40000 ALTER TABLE `wagtailcore_task` DISABLE KEYS */;
INSERT INTO `wagtailcore_task` VALUES (1,'Moderators approval',1,2);
/*!40000 ALTER TABLE `wagtailcore_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_taskstate`
--

DROP TABLE IF EXISTS `wagtailcore_taskstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_taskstate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(50) NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `finished_at` datetime(6) DEFAULT NULL,
  `content_type_id` int(11) NOT NULL,
  `revision_id` int(11) NOT NULL,
  `task_id` int(11) NOT NULL,
  `workflow_state_id` int(11) NOT NULL,
  `finished_by_id` int(11) DEFAULT NULL,
  `comment` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailcore_taskstat_content_type_id_0a758fdc_fk_django_co` (`content_type_id`),
  KEY `wagtailcore_taskstat_page_revision_id_9f52c88e_fk_wagtailco` (`revision_id`),
  KEY `wagtailcore_taskstate_task_id_c3677c34_fk_wagtailcore_task_id` (`task_id`),
  KEY `wagtailcore_taskstat_workflow_state_id_9239a775_fk_wagtailco` (`workflow_state_id`),
  KEY `wagtailcore_taskstate_finished_by_id_13f98229_fk_auth_user_id` (`finished_by_id`),
  CONSTRAINT `wagtailcore_taskstat_content_type_id_0a758fdc_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_taskstat_revision_id_df25a499_fk_wagtailco` FOREIGN KEY (`revision_id`) REFERENCES `wagtailcore_revision` (`id`),
  CONSTRAINT `wagtailcore_taskstat_workflow_state_id_9239a775_fk_wagtailco` FOREIGN KEY (`workflow_state_id`) REFERENCES `wagtailcore_workflowstate` (`id`),
  CONSTRAINT `wagtailcore_taskstate_finished_by_id_13f98229_fk_auth_user_id` FOREIGN KEY (`finished_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `wagtailcore_taskstate_task_id_c3677c34_fk_wagtailcore_task_id` FOREIGN KEY (`task_id`) REFERENCES `wagtailcore_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_taskstate`
--

LOCK TABLES `wagtailcore_taskstate` WRITE;
/*!40000 ALTER TABLE `wagtailcore_taskstate` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_taskstate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_workflow`
--

DROP TABLE IF EXISTS `wagtailcore_workflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_workflow` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_workflow`
--

LOCK TABLES `wagtailcore_workflow` WRITE;
/*!40000 ALTER TABLE `wagtailcore_workflow` DISABLE KEYS */;
INSERT INTO `wagtailcore_workflow` VALUES (1,'Moderators approval',1);
/*!40000 ALTER TABLE `wagtailcore_workflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_workflowcontenttype`
--

DROP TABLE IF EXISTS `wagtailcore_workflowcontenttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_workflowcontenttype` (
  `content_type_id` int(11) NOT NULL,
  `workflow_id` int(11) NOT NULL,
  PRIMARY KEY (`content_type_id`),
  KEY `wagtailcore_workflow_workflow_id_9aad7cd2_fk_wagtailco` (`workflow_id`),
  CONSTRAINT `wagtailcore_workflow_content_type_id_b261bb37_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_workflow_workflow_id_9aad7cd2_fk_wagtailco` FOREIGN KEY (`workflow_id`) REFERENCES `wagtailcore_workflow` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_workflowcontenttype`
--

LOCK TABLES `wagtailcore_workflowcontenttype` WRITE;
/*!40000 ALTER TABLE `wagtailcore_workflowcontenttype` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_workflowcontenttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_workflowpage`
--

DROP TABLE IF EXISTS `wagtailcore_workflowpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_workflowpage` (
  `page_id` int(11) NOT NULL,
  `workflow_id` int(11) NOT NULL,
  PRIMARY KEY (`page_id`),
  KEY `wagtailcore_workflow_workflow_id_56f56ff6_fk_wagtailco` (`workflow_id`),
  CONSTRAINT `wagtailcore_workflow_workflow_id_56f56ff6_fk_wagtailco` FOREIGN KEY (`workflow_id`) REFERENCES `wagtailcore_workflow` (`id`),
  CONSTRAINT `wagtailcore_workflowpage_page_id_81e7bab6_fk_wagtailcore_page_id` FOREIGN KEY (`page_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_workflowpage`
--

LOCK TABLES `wagtailcore_workflowpage` WRITE;
/*!40000 ALTER TABLE `wagtailcore_workflowpage` DISABLE KEYS */;
INSERT INTO `wagtailcore_workflowpage` VALUES (1,1);
/*!40000 ALTER TABLE `wagtailcore_workflowpage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_workflowstate`
--

DROP TABLE IF EXISTS `wagtailcore_workflowstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_workflowstate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `current_task_state_id` int(11) DEFAULT NULL,
  `object_id` varchar(255) NOT NULL,
  `requested_by_id` int(11) DEFAULT NULL,
  `workflow_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `base_content_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `current_task_state_id` (`current_task_state_id`),
  KEY `wagtailcore_workflow_requested_by_id_4090bca3_fk_auth_user` (`requested_by_id`),
  KEY `wagtailcore_workflow_workflow_id_1f18378f_fk_wagtailco` (`workflow_id`),
  KEY `workflowstate_ct_id_idx` (`content_type_id`,`object_id`),
  KEY `workflowstate_base_ct_id_idx` (`base_content_type_id`,`object_id`),
  CONSTRAINT `wagtailcore_workflow_base_content_type_id_a30dc576_fk_django_co` FOREIGN KEY (`base_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_workflow_content_type_id_2bb78ce1_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `wagtailcore_workflow_current_task_state_i_3a1a0632_fk_wagtailco` FOREIGN KEY (`current_task_state_id`) REFERENCES `wagtailcore_taskstate` (`id`),
  CONSTRAINT `wagtailcore_workflow_requested_by_id_4090bca3_fk_auth_user` FOREIGN KEY (`requested_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `wagtailcore_workflow_workflow_id_1f18378f_fk_wagtailco` FOREIGN KEY (`workflow_id`) REFERENCES `wagtailcore_workflow` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_workflowstate`
--

LOCK TABLES `wagtailcore_workflowstate` WRITE;
/*!40000 ALTER TABLE `wagtailcore_workflowstate` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailcore_workflowstate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailcore_workflowtask`
--

DROP TABLE IF EXISTS `wagtailcore_workflowtask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailcore_workflowtask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sort_order` int(11) DEFAULT NULL,
  `task_id` int(11) NOT NULL,
  `workflow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailcore_workflowtask_workflow_id_task_id_4ec7a62b_uniq` (`workflow_id`,`task_id`),
  KEY `wagtailcore_workflowtask_task_id_ce7716fe_fk_wagtailcore_task_id` (`task_id`),
  KEY `wagtailcore_workflowtask_workflow_id_b9717175` (`workflow_id`),
  CONSTRAINT `wagtailcore_workflow_workflow_id_b9717175_fk_wagtailco` FOREIGN KEY (`workflow_id`) REFERENCES `wagtailcore_workflow` (`id`),
  CONSTRAINT `wagtailcore_workflowtask_task_id_ce7716fe_fk_wagtailcore_task_id` FOREIGN KEY (`task_id`) REFERENCES `wagtailcore_task` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailcore_workflowtask`
--

LOCK TABLES `wagtailcore_workflowtask` WRITE;
/*!40000 ALTER TABLE `wagtailcore_workflowtask` DISABLE KEYS */;
INSERT INTO `wagtailcore_workflowtask` VALUES (1,0,1,1);
/*!40000 ALTER TABLE `wagtailcore_workflowtask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtaildocs_document`
--

DROP TABLE IF EXISTS `wagtaildocs_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtaildocs_document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `file` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `uploaded_by_user_id` int(11) DEFAULT NULL,
  `collection_id` int(11) NOT NULL,
  `file_size` int(10) unsigned DEFAULT NULL,
  `file_hash` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtaildocs_document_collection_id_23881625_fk_wagtailco` (`collection_id`),
  KEY `wagtaildocs_document_uploaded_by_user_id_17258b41_fk_auth_user` (`uploaded_by_user_id`),
  CONSTRAINT `wagtaildocs_document_collection_id_23881625_fk_wagtailco` FOREIGN KEY (`collection_id`) REFERENCES `wagtailcore_collection` (`id`),
  CONSTRAINT `wagtaildocs_document_uploaded_by_user_id_17258b41_fk_auth_user` FOREIGN KEY (`uploaded_by_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtaildocs_document`
--

LOCK TABLES `wagtaildocs_document` WRITE;
/*!40000 ALTER TABLE `wagtaildocs_document` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtaildocs_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtaildocs_uploadeddocument`
--

DROP TABLE IF EXISTS `wagtaildocs_uploadeddocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtaildocs_uploadeddocument` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file` varchar(200) NOT NULL,
  `uploaded_by_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtaildocs_uploaded_uploaded_by_user_id_8dd61a73_fk_auth_user` (`uploaded_by_user_id`),
  CONSTRAINT `wagtaildocs_uploaded_uploaded_by_user_id_8dd61a73_fk_auth_user` FOREIGN KEY (`uploaded_by_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtaildocs_uploadeddocument`
--

LOCK TABLES `wagtaildocs_uploadeddocument` WRITE;
/*!40000 ALTER TABLE `wagtaildocs_uploadeddocument` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtaildocs_uploadeddocument` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailembeds_embed`
--

DROP TABLE IF EXISTS `wagtailembeds_embed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailembeds_embed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` longtext NOT NULL,
  `max_width` smallint(6) DEFAULT NULL,
  `type` varchar(10) NOT NULL,
  `html` longtext NOT NULL,
  `title` longtext NOT NULL,
  `author_name` longtext NOT NULL,
  `provider_name` longtext NOT NULL,
  `thumbnail_url` longtext NOT NULL,
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `last_updated` datetime(6) NOT NULL,
  `hash` varchar(32) NOT NULL,
  `cache_until` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailembeds_embed_hash_c9bd8c9a_uniq` (`hash`),
  KEY `wagtailembeds_embed_cache_until_26c94bb0` (`cache_until`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailembeds_embed`
--

LOCK TABLES `wagtailembeds_embed` WRITE;
/*!40000 ALTER TABLE `wagtailembeds_embed` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailembeds_embed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailforms_formsubmission`
--

DROP TABLE IF EXISTS `wagtailforms_formsubmission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailforms_formsubmission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `form_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`form_data`)),
  `submit_time` datetime(6) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailforms_formsub_page_id_e48e93e7_fk_wagtailco` (`page_id`),
  CONSTRAINT `wagtailforms_formsub_page_id_e48e93e7_fk_wagtailco` FOREIGN KEY (`page_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailforms_formsubmission`
--

LOCK TABLES `wagtailforms_formsubmission` WRITE;
/*!40000 ALTER TABLE `wagtailforms_formsubmission` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailforms_formsubmission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailimages_image`
--

DROP TABLE IF EXISTS `wagtailimages_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailimages_image` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `file` varchar(100) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `focal_point_x` int(10) unsigned DEFAULT NULL,
  `focal_point_y` int(10) unsigned DEFAULT NULL,
  `focal_point_width` int(10) unsigned DEFAULT NULL,
  `focal_point_height` int(10) unsigned DEFAULT NULL,
  `uploaded_by_user_id` int(11) DEFAULT NULL,
  `file_size` int(10) unsigned DEFAULT NULL,
  `collection_id` int(11) NOT NULL,
  `file_hash` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailimages_image_uploaded_by_user_id_5d73dc75_fk_auth_user_id` (`uploaded_by_user_id`),
  KEY `wagtailimages_image_collection_id_c2f8af7e_fk_wagtailco` (`collection_id`),
  KEY `wagtailimages_image_created_at_86fa6cd4` (`created_at`),
  KEY `wagtailimages_image_file_hash_fb5bbb23` (`file_hash`),
  CONSTRAINT `wagtailimages_image_collection_id_c2f8af7e_fk_wagtailco` FOREIGN KEY (`collection_id`) REFERENCES `wagtailcore_collection` (`id`),
  CONSTRAINT `wagtailimages_image_uploaded_by_user_id_5d73dc75_fk_auth_user_id` FOREIGN KEY (`uploaded_by_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailimages_image`
--

LOCK TABLES `wagtailimages_image` WRITE;
/*!40000 ALTER TABLE `wagtailimages_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailimages_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailimages_rendition`
--

DROP TABLE IF EXISTS `wagtailimages_rendition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailimages_rendition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `focal_point_key` varchar(16) NOT NULL,
  `filter_spec` varchar(255) NOT NULL,
  `image_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailimages_rendition_image_id_filter_spec_foc_323c8fe0_uniq` (`image_id`,`filter_spec`,`focal_point_key`),
  KEY `wagtailimages_rendition_filter_spec_1cba3201` (`filter_spec`),
  CONSTRAINT `wagtailimages_rendit_image_id_3e1fd774_fk_wagtailim` FOREIGN KEY (`image_id`) REFERENCES `wagtailimages_image` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailimages_rendition`
--

LOCK TABLES `wagtailimages_rendition` WRITE;
/*!40000 ALTER TABLE `wagtailimages_rendition` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailimages_rendition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailimages_uploadedimage`
--

DROP TABLE IF EXISTS `wagtailimages_uploadedimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailimages_uploadedimage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file` varchar(200) NOT NULL,
  `uploaded_by_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wagtailimages_upload_uploaded_by_user_id_85921689_fk_auth_user` (`uploaded_by_user_id`),
  CONSTRAINT `wagtailimages_upload_uploaded_by_user_id_85921689_fk_auth_user` FOREIGN KEY (`uploaded_by_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailimages_uploadedimage`
--

LOCK TABLES `wagtailimages_uploadedimage` WRITE;
/*!40000 ALTER TABLE `wagtailimages_uploadedimage` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailimages_uploadedimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailredirects_redirect`
--

DROP TABLE IF EXISTS `wagtailredirects_redirect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailredirects_redirect` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `old_path` varchar(255) NOT NULL,
  `is_permanent` tinyint(1) NOT NULL,
  `redirect_link` varchar(255) NOT NULL,
  `redirect_page_id` int(11) DEFAULT NULL,
  `site_id` int(11) DEFAULT NULL,
  `automatically_created` tinyint(1) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `redirect_page_route_path` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailredirects_redirect_old_path_site_id_783622d7_uniq` (`old_path`,`site_id`),
  KEY `wagtailredirects_redirect_old_path_bb35247b` (`old_path`),
  KEY `wagtailredirects_red_redirect_page_id_b5728a8f_fk_wagtailco` (`redirect_page_id`),
  KEY `wagtailredirects_red_site_id_780a0e1e_fk_wagtailco` (`site_id`),
  CONSTRAINT `wagtailredirects_red_redirect_page_id_b5728a8f_fk_wagtailco` FOREIGN KEY (`redirect_page_id`) REFERENCES `wagtailcore_page` (`id`),
  CONSTRAINT `wagtailredirects_red_site_id_780a0e1e_fk_wagtailco` FOREIGN KEY (`site_id`) REFERENCES `wagtailcore_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailredirects_redirect`
--

LOCK TABLES `wagtailredirects_redirect` WRITE;
/*!40000 ALTER TABLE `wagtailredirects_redirect` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailredirects_redirect` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailsearch_indexentry`
--

DROP TABLE IF EXISTS `wagtailsearch_indexentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailsearch_indexentry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_id` varchar(50) NOT NULL,
  `title_norm` double NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `autocomplete` longtext DEFAULT NULL,
  `body` longtext DEFAULT NULL,
  `title` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailsearch_indexentry_content_type_id_object_id_bcd7ba73_uniq` (`content_type_id`,`object_id`),
  FULLTEXT KEY `fulltext_body` (`body`),
  FULLTEXT KEY `fulltext_title` (`title`),
  FULLTEXT KEY `fulltext_title_body` (`title`,`body`),
  FULLTEXT KEY `fulltext_autocomplete` (`autocomplete`),
  CONSTRAINT `wagtailsearch_indexe_content_type_id_62ed694f_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailsearch_indexentry`
--

LOCK TABLES `wagtailsearch_indexentry` WRITE;
/*!40000 ALTER TABLE `wagtailsearch_indexentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailsearch_indexentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailsearch_query`
--

DROP TABLE IF EXISTS `wagtailsearch_query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailsearch_query` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `query_string` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `query_string` (`query_string`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailsearch_query`
--

LOCK TABLES `wagtailsearch_query` WRITE;
/*!40000 ALTER TABLE `wagtailsearch_query` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailsearch_query` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailsearch_querydailyhits`
--

DROP TABLE IF EXISTS `wagtailsearch_querydailyhits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailsearch_querydailyhits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `hits` int(11) NOT NULL,
  `query_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wagtailsearch_querydailyhits_query_id_date_1dd232e6_uniq` (`query_id`,`date`),
  CONSTRAINT `wagtailsearch_queryd_query_id_2185994b_fk_wagtailse` FOREIGN KEY (`query_id`) REFERENCES `wagtailsearch_query` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailsearch_querydailyhits`
--

LOCK TABLES `wagtailsearch_querydailyhits` WRITE;
/*!40000 ALTER TABLE `wagtailsearch_querydailyhits` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailsearch_querydailyhits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wagtailusers_userprofile`
--

DROP TABLE IF EXISTS `wagtailusers_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `wagtailusers_userprofile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `submitted_notifications` tinyint(1) NOT NULL,
  `approved_notifications` tinyint(1) NOT NULL,
  `rejected_notifications` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  `preferred_language` varchar(10) NOT NULL,
  `current_time_zone` varchar(40) NOT NULL,
  `avatar` varchar(100) NOT NULL,
  `updated_comments_notifications` tinyint(1) NOT NULL,
  `dismissibles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`dismissibles`)),
  `theme` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `wagtailusers_userprofile_user_id_59c92331_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wagtailusers_userprofile`
--

LOCK TABLES `wagtailusers_userprofile` WRITE;
/*!40000 ALTER TABLE `wagtailusers_userprofile` DISABLE KEYS */;
/*!40000 ALTER TABLE `wagtailusers_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `website_event`
--

DROP TABLE IF EXISTS `website_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(200) NOT NULL,
  `ts_created` datetime(6) DEFAULT NULL,
  `ts_modified` datetime(6) DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `event_type` varchar(20) NOT NULL,
  `desc_short` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_event`
--

LOCK TABLES `website_event` WRITE;
/*!40000 ALTER TABLE `website_event` DISABLE KEYS */;
/*!40000 ALTER TABLE `website_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `website_event_description`
--

DROP TABLE IF EXISTS `website_event_description`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_event_description` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `textblock_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `website_event_description_event_id_textblock_id_d1f45be7_uniq` (`event_id`,`textblock_id`),
  KEY `website_event_descri_textblock_id_df881172_fk_website_t` (`textblock_id`),
  CONSTRAINT `website_event_descri_textblock_id_df881172_fk_website_t` FOREIGN KEY (`textblock_id`) REFERENCES `website_textblock` (`id`),
  CONSTRAINT `website_event_description_event_id_9ca275d8_fk_website_event_id` FOREIGN KEY (`event_id`) REFERENCES `website_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_event_description`
--

LOCK TABLES `website_event_description` WRITE;
/*!40000 ALTER TABLE `website_event_description` DISABLE KEYS */;
/*!40000 ALTER TABLE `website_event_description` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `website_medienspiegel`
--

DROP TABLE IF EXISTS `website_medienspiegel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_medienspiegel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(200) NOT NULL,
  `ts_created` datetime(6) DEFAULT NULL,
  `ts_modified` datetime(6) DEFAULT NULL,
  `date` date NOT NULL,
  `name` varchar(500) NOT NULL,
  `medium` varchar(50) NOT NULL,
  `pdf_file` varchar(100) NOT NULL,
  `url` varchar(1000) NOT NULL,
  `link_text` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_medienspiegel`
--

LOCK TABLES `website_medienspiegel` WRITE;
/*!40000 ALTER TABLE `website_medienspiegel` DISABLE KEYS */;
/*!40000 ALTER TABLE `website_medienspiegel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `website_textblock`
--

DROP TABLE IF EXISTS `website_textblock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_textblock` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment` varchar(200) NOT NULL,
  `ts_created` datetime(6) DEFAULT NULL,
  `ts_modified` datetime(6) DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `title` varchar(50) NOT NULL,
  `text` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_textblock`
--

LOCK TABLES `website_textblock` WRITE;
/*!40000 ALTER TABLE `website_textblock` DISABLE KEYS */;
/*!40000 ALTER TABLE `website_textblock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `website_websitemainpage`
--

DROP TABLE IF EXISTS `website_websitemainpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_websitemainpage` (
  `page_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `website_websitemainp_page_ptr_id_c0c0e58a_fk_wagtailco` FOREIGN KEY (`page_ptr_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_websitemainpage`
--

LOCK TABLES `website_websitemainpage` WRITE;
/*!40000 ALTER TABLE `website_websitemainpage` DISABLE KEYS */;
/*!40000 ALTER TABLE `website_websitemainpage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `website_websitepage`
--

DROP TABLE IF EXISTS `website_websitepage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `website_websitepage` (
  `page_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `website_websitepage_page_ptr_id_509ce8a7_fk_wagtailcore_page_id` FOREIGN KEY (`page_ptr_id`) REFERENCES `wagtailcore_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `website_websitepage`
--

LOCK TABLES `website_websitepage` WRITE;
/*!40000 ALTER TABLE `website_websitepage` DISABLE KEYS */;
/*!40000 ALTER TABLE `website_websitepage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'cohiva-demo_django'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-03 15:38:40
