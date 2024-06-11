DROP TABLE IF EXISTS botanists, timezones, plants, locations, plants


CREATE TABLE botanists(
    botanists_id SMALLINT IDENTITY(1,1),
    first_name VARCHAR(25) NOT NULL,
    last_name VARCHAR(25) NOT NULL,
    email VARCHAR(75) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    PRIMARY KEY(botanists_id)
);

CREATE TABLE timezones(
    timezone_id SMALLINT IDENTITY(1,1),
    timezone VARCHAR(25) NOT NULL
);

CREATE TABLE country_codes(
    country_code_id SMALLINT IDENTITY(1,1),
    country_code VARCHAR(2) NOT NULL
);

CREATE TABLE locations(
    location_id SMALLINT IDENTITY(1,1),
    location_name VARCHAR(50) NOT NULL
    location_lat DECIMAL NOT NULL, 
    location_lon DECIMAL NOT NULL
    timezone_id SMALLINT NOT NULL,
    country_code_id SMALLINT NOT NULL,
    FOREIGN KEY (timezone_id) REFERENCES timezones(timezone_id),
    FOREIGN KEY (country_code) REFERENCES country_codes(country_code)  
);

CREATE TABLE plants(
    plant_id SMALLINT IDENTITY(1,1),
    scientific_name VARCHAR(100) UNIQUE NOT NULL,
    common_name VARCHAR(100) UNIQUE NOT NULL, 
    FOREIGN KEY (location_id) REFERENCES locations(location_id)   
);