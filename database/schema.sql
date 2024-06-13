DROP TABLE IF EXISTS gamma.readings, gamma.plants, gamma.locations, gamma.timezones, gamma.botanists, gamma.country_codes, gamma.plant_species;
GO

CREATE TABLE gamma.timezones(
    timezone_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    timezone VARCHAR(25) NOT NULL
);
GO

CREATE TABLE gamma.country_codes(
    country_code_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL
);
GO

CREATE TABLE gamma.locations(
    location_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    location_name VARCHAR(50) NOT NULL,
    location_lat DECIMAL(10, 7) NOT NULL, 
    location_lon DECIMAL(10, 7) NOT NULL,
    timezone_id SMALLINT NOT NULL,
    country_code_id SMALLINT NOT NULL,
    FOREIGN KEY (timezone_id) REFERENCES gamma.timezones(timezone_id),
    FOREIGN KEY (country_code_id) REFERENCES gamma.country_codes(country_code_id)
);
GO

CREATE TABLE gamma.plant_species(
    species_id SMALLINT IDENTITY(1, 1) PRIMARY KEY,
    common_name VARCHAR(100) UNIQUE NOT NULL,
    scientific_name VARCHAR(100)
);
GO

CREATE UNIQUE INDEX IX_plant_species
ON gamma.plant_species(scientific_name)
WHERE scientific_name IS NOT NULL;


CREATE TABLE gamma.plants(
    plant_id SMALLINT PRIMARY KEY,
    naming_id SMALLINT NOT NULL,
    location_id SMALLINT NOT NULL,
    FOREIGN KEY (naming_id) REFERENCES gamma.plant_species(species_id),
    FOREIGN KEY (location_id) REFERENCES gamma.locations(location_id)   
);
GO

CREATE TABLE gamma.botanists(
    botanists_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(25) NOT NULL,
    last_name VARCHAR(25) NOT NULL,
    email VARCHAR(75) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
);
GO

CREATE TABLE gamma.readings (
    reading_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    plant_id SMALLINT NOT NULL,
    reading_at DATETIME2 NOT NULL,
    moisture DECIMAL(5, 2) NOT NULL,
    temp DECIMAL(5, 2) NOT NULL,
    botanist_id SMALLINT NOT NULL,
    watered_at DATETIME2 NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES gamma.plants(plant_id),
    FOREIGN KEY (botanist_id) REFERENCES gamma.botanists(botanists_id)
);
GO

INSERT INTO gamma.botanists (first_name, last_name, email, phone_number) VALUES 
('Carl', 'Linnaeus', 'carl.linnaeus@lnhm.co.uk', '(146)994-1635x35992'),
('Eliza', 'Andrews', 'eliza.andrews@lnhm.co.uk', '(846)669-6651x75948'),
('Gertrude', 'Jekyll', 'gertrude.jekyll@lnhm.co.uk', '001-481-273-3691x127')
;
GO

INSERT INTO gamma.plants (plant_id, naming_id, location_id) 
VALUES 
(0, 44, 29),
(1, 9, 42),
(2, 27, 25),
(3, 18, 29),
(4, 24, 5),
(5, 29, 31),
(6, 42, 40),
(8, 37, 36),
(9, 3, 10),
(10, 46, 7),
(11, 38, 18),
(12, 41, 1),
(13, 26, 3),
(14, 25, 4),
(15, 35, 2),
(16, 36, 38),
(17, 23, 41),
(18, 10, 44),
(19, 4, 11),
(20, 20, 22),
(21, 31, 27),
(22, 37, 26),
(24, 32, 13),
(25, 21, 32),
(26, 19, 24),
(27, 40, 19),
(28, 13, 17),
(29, 22, 33),
(30, 14, 16),
(31, 8, 14),
(32, 5, 30),
(33, 6, 9),
(34, 45, 22),
(35, 43, 37),
(36, 17, 23),
(37, 16, 15),
(38, 33, 6),
(39, 30, 39),
(40, 34, 20),
(41, 7, 21),
(42, 11, 35),
(44, 28, 43),
(45, 39, 42),
(46, 1, 28),
(47, 2, 34),
(48, 12, 8),
(49, 15, 12),
(50, 44, 29);
GO

INSERT INTO gamma.locations (location_name, location_lat, location_lon, timezone_id, country_code_id)
VALUES
('Longview', 32.5007000, -94.7404900, 20, 21),
('Siliana', 36.0849700, 9.3708200, 1, 16),
('Bensheim', 49.6836900, 8.6183900, 14, 8),
('Gainesville', 29.6516300, -82.3248300, 4, 21),
('Ilopango', 13.7016700, -89.1094400, 22, 3),
('Magomeni', -6.8000000, 39.2500000, 15, 5),
('Split', 43.5089100, 16.4391500, 11, 7),
('Calauan', 14.1498900, 121.3152000, 5, 18),
('Bachhraon', 28.9269400, 78.2345600, 17, 2),
('Weimar', 50.9803000, 11.3290300, 14, 8),
('Tonota', -21.4423600, 27.4615300, 8, 11),
('Acayucan', 17.9497900, -94.9138600, 25, 25),
('Motomachi', 43.8263400, 144.0963800, 27, 27),
('Licheng', 23.2954900, 113.8246500, 10, 6),
('Malaut', 30.2112100, 74.4818000, 17, 2),
('Ajdabiya', 30.7554500, 20.2262500, 23, 26),
('Brunswick', 43.9145200, -69.9653300, 4, 21),
('Kahului', 20.8895300, -156.4743200, 16, 21),
('Hlukhiv', 51.6782200, 33.9162000, 9, 23),
('Valence', 44.9280100, 4.8951000, 18, 9),
('Pujali', 22.4711000, 88.1453000, 17, 2),
('Reus', 41.1561200, 1.1068700, 21, 19),
('Dublin', 32.5404400, -82.9037500, 4, 21),
('El Achir', 36.0638600, 4.6274400, 12, 20),
('Efon-Alaaye', 7.6564900, 4.9223500, 24, 17),
('Friedberg', 48.3569300, 10.9846100, 14, 8),
('Carlos Barbosa', -29.2975000, -51.5036100, 7, 10),
('Salima', -13.7804000, 34.4587000, 13, 22),
('Resplendor', -19.3255600, -41.2552800, 7, 10),
('Gifhorn', 52.4777400, 10.5511000, 14, 8),
('Jashpurnagar', 22.8878300, 84.1386400, 17, 2),
('Ar Ruseris', 11.8659000, 34.3869000, 29, 4),
('Ueno-ebisumachi', 34.7585600, 136.1310800, 27, 27),
('Catania', 37.4922300, 15.0704100, 30, 15),
('Smolyan', 41.5743900, 24.7120400, 28, 12),
('Bonoua', 5.2724700, -3.5962500, 2, 24),
('La Ligua', -32.4524200, -71.2310600, 3, 13),
('Yonkers', 40.9312100, -73.8987500, 4, 21),
('Fujioka', 36.2462400, 139.0720400, 27, 27),
('Markham', 43.8668200, -79.2663000, 19, 1),
('Wangon', -7.5161100, 109.0538900, 26, 14),
('South Whittier', 33.9501500, -118.0391700, 6, 21),
('Zacoalco de Torres', 20.2281600, -103.5687000, 25, 25),
('Oschatz', 51.3000100, 13.1098400, 14, 8);
GO


INSERT INTO gamma.country_codes (country_code)
VALUES
('CA'),
('IN'),
('SV'),
('SD'),
('TZ'),
('CN'),
('HR'),
('DE'),
('FR'),
('BR'),
('BW'),
('BG'),
('CL'),
('ID'),
('IT'),
('TN'),
('NG'),
('PH'),
('ES'),
('DZ'),
('US'),
('MW'),
('UA'),
('CI'),
('MX'),
('LY'),
('JP');
GO

INSERT INTO gamma.timezones (timezone)
VALUES
('Africa/Tunis'),
('Africa/Abidjan'),
('America/Santiago'),
('America/New_York'),
('Asia/Manila'),
('America/Los_Angeles'),
('America/Sao_Paulo'),
('Africa/Gaborone'),
('Europe/Kiev'),
('Asia/Shanghai'),
('Europe/Zagreb'),
('Africa/Algiers'),
('Africa/Blantyre'),
('Europe/Berlin'),
('Africa/Dar_es_Salaam'),
('Pacific/Honolulu'),
('Asia/Kolkata'),
('Europe/Paris'),
('America/Toronto'),
('America/Chicago'),
('Europe/Madrid'),
('America/El_Salvador'),
('Africa/Tripoli'),
('Africa/Lagos'),
('America/Mexico_City'),
('Asia/Jakarta'),
('Asia/Tokyo'),
('Europe/Sofia'),
('Africa/Khartoum'),
('Europe/Rome');
GO