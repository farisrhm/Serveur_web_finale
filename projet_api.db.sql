BEGIN TRANSACTION;


CREATE TABLE IF NOT EXISTS "rdv" (
	"id"	INTEGER,
	"idmedecin"	INTEGER,
	"idpatient"	INTEGER,
	"date"	TEXT,
	"heure"	TEXT
);

CREATE TABLE IF NOT EXISTS "auth" (
	"identifier"	INTEGER NOT NULL UNIQUE,
	"login"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"statut"	TEXT NOT NULL,
	PRIMARY KEY("identifier" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Patient" (
	"identifier"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"telecom"	TEXT NOT NULL,
	"gender"	TEXT NOT NULL,
	"birthDate"	TEXT NOT NULL,
	"address"	TEXT NOT NULL,
	"generalPractitioner"	TEXT,
	"num"	TEXT NOT NULL,
	PRIMARY KEY("identifier" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Practitioner" (
	"identifier"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"telecom"	TEXT NOT NULL,
	"gender"	TEXT NOT NULL,
	"birthDate"	TEXT NOT NULL,
	"address"	TEXT NOT NULL,
	"num"	TEXT NOT NULL,
	PRIMARY KEY("identifier" AUTOINCREMENT)
);

COMMIT;
