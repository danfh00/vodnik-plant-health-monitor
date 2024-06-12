DROP TABLE IF EXISTS gamma.readings, gamma.plants, gamma.locations, gamma.timezones, gamma.botanists, gamma.country_codes;
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

CREATE TABLE gamma.scientific_plant_names(
    scientific_plant_name_id SMALLINT IDENTITY(1, 1) PRIMARY KEY,
    scientific_name VARCHAR(100) UNIQUE NOT NULL
);
GO

CREATE TABLE gamma.common_plant_names(
    common_plant_name_id SMALLINT IDENTITY(1, 1) PRIMARY KEY,
    common_name VARCHAR(100) UNIQUE NOT NULL
);
GO

CREATE TABLE gamma.plants(
    plant_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    scientific_name_id VARCHAR(100),
    common_name_id SMALLINT NOT NULL,
    location_id SMALLINT NOT NULL,
    FOREIGN KEY (scientific_name_id) REFERENCES gamma.scientific_plant_names(scientific_plant_name_id),
    FOREIGN KEY (common_name_id) REFERENCES gamma.common_plant_names(common_plant_name_id),
    FOREIGN KEY (location_id) REFERENCES gamma.locations(location_id)   
);
GO

CREATE UNIQUE INDEX IX_plants_scientific_name
ON gamma.plants(scientific_name)
WHERE scientific_name IS NOT NULL;

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