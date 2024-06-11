DROP TABLE IF EXISTS botanists, timezones, plants


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


CREATE TABLE plants(
    plant_id SMALLINT IDENTITY(1,1),
    scientific_name VARCHAR(100) NOT NULL,
    common_name VARCHAR(100) NOT NULL, 
    FOREIGN KEY (location_id) REFERENCES locations(location_id)   
);