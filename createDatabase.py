# ONLY RUN ONCE TO INITIALZE DATABASE

import mysql.connector as mysql
import os
from dotenv import load_dotenv

load_dotenv()

# Creates empty snomedct database
snomedDB = mysql.connect(
    host="localhost",
    user=os.getenv("MYSQL_USERNAME"),
    password=os.getenv("MYSQL_PASSWORD")
)
print(snomedDB)
cursor = snomedDB.cursor()
cursor.execute("DROP DATABASE IF EXISTS snomedct")
cursor.execute("CREATE DATABASE snomedct /*!40100 DEFAULT CHARACTER SET utf8mb4 */")
print("ja")
# Connect to specific database
snomedDB = mysql.connect(
    host="localhost",
    user=os.getenv("MYSQL_USERNAME"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="snomedct"
)
cursor = snomedDB.cursor()

# Set global db rules
cursor.execute("SET GLOBAL net_write_timeout = 60")
cursor.execute("SET GLOBAL net_read_timeout = 120")
cursor.execute("SET GLOBAL sql_mode = ''")
cursor.execute("SET SESSION sql_mode = ''")

# Drop existing tables
cursor.execute("DROP TABLE IF EXISTS concept")
cursor.execute("DROP TABLE IF EXISTS description")
cursor.execute("DROP TABLE IF EXISTS relationship")
cursor.execute("DROP TABLE IF EXISTS definition")

# Create empty tables
cursor.execute("CREATE TABLE concept (" + 
    "id BIGINT NOT NULL DEFAULT 0," + 
    "effectiveTime DATETIME NOT NULL DEFAULT '2000-01-31 00:00:00'," +
    "active TINYINT NOT NULL DEFAULT 0," +
    "moduleId BIGINT NOT NULL DEFAULT 0," +
    "definitionStatusId BIGINT NOT NULL DEFAULT 0," +
    "PRIMARY KEY (id, effectiveTime))" +
    "ENGINE=MyISAM DEFAULT CHARSET=utf8mb4")
cursor.execute("CREATE TABLE description(" +
    "id BIGINT NOT NULL DEFAULT 0," +
    "effectiveTime DATETIME NOT NULL DEFAULT '2000-01-31 00:00:00'," +
    "active TINYINT NOT NULL DEFAULT 0," +
    "moduleId BIGINT NOT NULL DEFAULT 0," +
    "conceptId BIGINT NOT NULL DEFAULT 0," +
    "languageCode VARCHAR(3) NOT NULL DEFAULT ''," +
    "typeId BIGINT NOT NULL DEFAULT 0," +
    "term TEXT NOT NULL," +
    "caseSignificanceId BIGINT NOT NULL DEFAULT 0," +
    "PRIMARY KEY (id, effectiveTime))" +
    "ENGINE=MyISAM DEFAULT CHARSET=utf8mb4")
cursor.execute("CREATE TABLE relationship (" +
    "id BIGINT NOT NULL DEFAULT 0," +
    "effectiveTime DATETIME NOT NULL DEFAULT '2000-01-31 00:00:00'," +
    "active TINYINT NOT NULL DEFAULT 0," +
    "moduleId BIGINT NOT NULL DEFAULT 0," +
    "sourceId BIGINT NOT NULL DEFAULT 0," +
    "destinationId BIGINT NOT NULL DEFAULT 0," +
    "relationshipGroup INT NOT NULL DEFAULT 0," +
    "typeId BIGINT NOT NULL DEFAULT 0," +
    "characteristicTypeId BIGINT NOT NULL DEFAULT 0," +
    "modifierId BIGINT NOT NULL DEFAULT 0," +
    "PRIMARY KEY (id, effectiveTime))" +
    "ENGINE=MyISAM DEFAULT CHARSET=utf8mb4")
cursor.execute("CREATE TABLE definition (" +
    "id BIGINT NOT NULL DEFAULT 0," +
    "effectiveTime DATETIME NOT NULL DEFAULT '2000-01-31 00:00:00'," +
    "active TINYINT NOT NULL DEFAULT 0," +
    "moduleId BIGINT NOT NULL DEFAULT 0," +
    "conceptId BIGINT NOT NULL DEFAULT 0," +
    "languageCode VARCHAR(3) NOT NULL DEFAULT ''," +
    "typeId BIGINT NOT NULL DEFAULT 0," +
    "term TEXT NOT NULL," +
    "caseSignificanceId BIGINT NOT NULL DEFAULT 0," +
    "PRIMARY KEY (id, effectiveTime))" +
    "ENGINE=MyISAM DEFAULT CHARSET=utf8mb4")

# Create additional indexes
cursor.execute("CREATE FULLTEXT INDEX description_term ON description(term)")
cursor.execute("CREATE INDEX description_concept ON description(conceptId)")
cursor.execute("CREATE INDEX relationship_source ON relationship(sourceId, typeID, destinationID)")
cursor.execute("CREATE INDEX definition_concept ON definition(conceptId)")


# C:/Users/ravan/Documents/GitHub
# Import files
## Add following line to "C:\ProgramData\MySQL\MySQL Server 9.1\my.ini", under [mysql], [mysqld] and [client]:
### local-infile=1
## Restart MySQL from Services

## Run following commands in Mysql clc, always use '/' in paths and fill in full path
# Allow loading files:
## SET GLOBAL local_infile=1;
## GRANT FILE ON *.* TO 'root'@'localhost';
## \u snomedct
# Concepts:
## LOAD DATA LOCAL INFILE "C:/Users/ravan/Documents/GitHub/OntologyGeneration/SnomedNL/Snapshot/Terminology/sct2_Concept_Snapshot_NL1000146_20240930.txt" INTO TABLE concept LINES TERMINATED BY '\r\n' IGNORE 1 LINES (`id`,`effectiveTime`,`active`,`moduleId`,`definitionStatusId`);
# Descriptions:
## LOAD DATA LOCAL INFILE "C:/Users/ravan/Documents/GitHub/OntologyGeneration/SnomedNL/Snapshot/Terminology/sct2_Description_Snapshot-nl_NL1000146_20240930.txt" INTO TABLE description LINES TERMINATED BY '\r\n' IGNORE 1 LINES (`id`,`effectiveTime`,`active`,`moduleId`,`conceptId`,`languageCode`,`typeId`,`term`,`caseSignificanceId`);
# Relationships:
## LOAD DATA LOCAL INFILE "C:/Users/ravan/Documents/GitHub/OntologyGeneration/SnomedNL/Snapshot/Terminology/sct2_Relationship_Snapshot_NL1000146_20240930.txt" INTO TABLE relationship LINES TERMINATED BY '\r\n' IGNORE 1 LINES (`id`,`effectiveTime`,`active`,`moduleId`,`sourceId`,`destinationId`,`relationshipGroup`,`typeId`,`characteristicTypeId`,`modifierId`);
# Definitions:
## LOAD DATA LOCAL INFILE "C:/Users/ravan/Documents/GitHub/OntologyGeneration/SnomedNL/Snapshot/Terminology/sct2_TextDefinition_Snapshot-nl_NL1000146_20240930.txt" INTO TABLE definition LINES TERMINATED BY '\r\n' IGNORE 1 LINES (`id`, `effectiveTime`, `active`, `moduleId`, `conceptId`, `languageCode`, `typeId`, `term`, `caseSignificanceId`);

#For Kars:
# CMD
# mysql -u root -p --local_infile=1
# USE snomedct
# 
# LOAD DATA LOCAL INFILE "C:\\Users\\karst\\Documents\\University\\SP\\Software Production - Ontology Generation\\SnomedNL\\SnomedCT_ManagedServiceNL_PRODUCTION_NL1000146_20240930T120000Z\\Snapshot\\Terminology\\sct2_Concept_Snapshot_NL1000146_20240930.txt"
# INTO TABLE concept
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (`id`, `effectiveTime`, `active`, `moduleId`, `definitionStatusId`);
#
# LOAD DATA LOCAL INFILE "C:\\Users\\karst\\Documents\\University\\SP\\Software Production - Ontology Generation\\SnomedNL\\SnomedCT_ManagedServiceNL_PRODUCTION_NL1000146_20240930T120000Z\\Snapshot\\Terminology\\sct2_Description_Snapshot-nl_NL1000146_20240930.txt"
# INTO TABLE description
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (`id`, `effectiveTime`, `active`, `moduleId`, `conceptId`, `languageCode`, `typeId`, `term`, `caseSignificanceId`);
#
# LOAD DATA LOCAL INFILE "C:\\Users\\karst\\Documents\\University\\SP\\Software Production - Ontology Generation\\SnomedNL\\SnomedCT_ManagedServiceNL_PRODUCTION_NL1000146_20240930T120000Z\\Snapshot\\Terminology\\sct2_Relationship_Snapshot_NL1000146_20240930.txt"
# INTO TABLE relationship
# LINES TERMINATED BY '\r\n'
# IGNORE 1 LINES
# (`id`, `effectiveTime`, `active`, `moduleId`, `sourceId`, `destinationId`, `relationshipGroup`, `typeId`, `characteristicTypeId`, `modifierId`);


