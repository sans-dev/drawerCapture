create database if not exists drawerCaptureDB;
show databases;
use drawerCaptureDB;

-- Tabelle "Museum"
CREATE TABLE if not exists Museum (
    museumID INT AUTO_INCREMENT PRIMARY KEY,
    museumName VARCHAR(255) NOT NULL,
    museumAddress VARCHAR(255) NOT NULL
);

-- Tabelle "Collection"
CREATE TABLE if not exists Collection (
    collectionID INT AUTO_INCREMENT PRIMARY KEY,
    collectionName VARCHAR(255),
    museumID INT,
    FOREIGN KEY (museumID) REFERENCES Museum(museumID)
);

-- Tabelle "Image"
CREATE TABLE if not exists Image (
    imageID INT AUTO_INCREMENT PRIMARY KEY,
    data BLOB,
    thumb BLOB
);

-- Tabelle "Taxon"
CREATE TABLE if not exists Taxon (
    taxonID INT AUTO_INCREMENT PRIMARY KEY,
    taxonOrder VARCHAR(255),
    taxonFamily VARCHAR(255),
    taxonGenus VARCHAR(255),
    taxonSpecies VARCHAR(255),
    gbifID INT,
    isValidated BOOLEAN
);

-- Tabelle "User"
CREATE TABLE if not exists User (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    userName VARCHAR(255),
    userPassword VARCHAR(255) NOT NULL
);

-- Tabelle "Session"
CREATE TABLE if not exists Session (
    sessionID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP,
    userID INT,
    drawerID INT,
    FOREIGN KEY (userID) REFERENCES User(userID)
);

-- Tabelle "Drawer"
CREATE TABLE if not exists Drawer (
    drawerID INT AUTO_INCREMENT PRIMARY KEY,
    Location VARCHAR(255),
    Year INT,
    imageID INT,
    collectionID INT,
    sessionID INT,
    taxonID INT,
    FOREIGN KEY (imageID) REFERENCES Image(imageID),
    FOREIGN KEY (collectionID) REFERENCES Collection(collectionID),
    FOREIGN KEY (sessionID) REFERENCES Session(sessionID),
    FOREIGN KEY (taxonID) REFERENCES Taxon(taxonID)
);