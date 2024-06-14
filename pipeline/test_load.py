import pytest
from unittest.mock import MagicMock, patch

from load import check_if_botanist_in_db, add_botanist_to_db, check_if_timezone_in_db, add_timezone_to_db, check_if_country_code_in_db, add_country_code_to_db, check_if_location_in_db, add_location_to_db, check_if_species_in_db, add_species_to_db, check_if_plant_in_db, add_plant_to_db, botanist_checks, timezone_checks, country_code_checks, location_checks, plant_species_checks, plant_checks, botanist_checks


@pytest.fixture
def mock_create_connection():
    with patch("pymssql.connect") as mock:
        yield mock


@pytest.fixture
def mock_cursor(mock_create_connection):
    mock_cursor = MagicMock()
    mock_create_connection.cursor.return_value = mock_cursor
    return mock_cursor


def test_check_if_botanist_in_db_found(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    test_email = "test@example.com"
    test_schema = "test_schema"
    assert check_if_botanist_in_db(
        test_email, test_schema, mock_cursor) == (1,)

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT botanists_id FROM {test_schema}.botanists WHERE email=%s""", (test_email,))

    mock_cursor.fetchone.assert_called_once()


def test_check_if_botanist_in_db_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    test_email = None
    test_schema = "test_schema"
    assert check_if_botanist_in_db(
        test_email, test_schema, mock_cursor) == None

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT botanists_id FROM {test_schema}.botanists WHERE email=%s""", (test_email,))

    mock_cursor.fetchone.assert_called_once()


def test_add_botanist_to_db(mock_create_connection, mock_cursor):
    botanist_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '123-456-7890'
    }
    schema = 'test_schema'

    add_botanist_to_db(botanist_data, schema,
                       mock_create_connection, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        f"INSERT INTO {
            schema}.botanists (first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s)",
        ('John', 'Doe', 'john.doe@example.com', '123-456-7890')
    )

    mock_create_connection.commit.assert_called_once()


def test_check_if_timezone_in_db_found(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    test_timezone = "Africa/Abidjan"
    test_schema = "test_schema"
    assert check_if_timezone_in_db(
        test_timezone, test_schema, mock_cursor) == (1,)

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT timezone_id FROM {test_schema}.timezones WHERE timezone=%s""", (test_timezone,))

    mock_cursor.fetchone.assert_called_once()


def test_check_if_timezone_in_db_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    test_timezone = "Africa/Abidjan"
    test_schema = "test_schema"
    assert check_if_timezone_in_db(
        test_timezone, test_schema, mock_cursor) == None

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT timezone_id FROM {test_schema}.timezones WHERE timezone=%s""", (test_timezone,))

    mock_cursor.fetchone.assert_called_once()


def test_add_timezone_to_db(mock_create_connection, mock_cursor):
    timezone_name = "Africa/Abidjan"
    schema = 'test_schema'

    add_timezone_to_db(timezone_name, schema,
                       mock_create_connection, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        f"""INSERT INTO {schema}.timezones (timezone) VALUES (%s)""", (timezone_name,))

    mock_create_connection.commit.assert_called_once()


def test_check_if_country_code_in_db_found(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    test_cc = "CI"
    test_schema = "test_schema"
    assert check_if_country_code_in_db(
        test_cc, test_schema, mock_cursor) == (1,)

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT country_code_id FROM {test_schema}.country_codes WHERE country_code=%s""", (test_cc,))

    mock_cursor.fetchone.assert_called_once()


def test_check_if_country_code_in_db_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    test_cc = "CI"
    test_schema = "test_schema"
    assert check_if_country_code_in_db(
        test_cc, test_schema, mock_cursor) == None

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT country_code_id FROM {test_schema}.country_codes WHERE country_code=%s""", (test_cc,))

    mock_cursor.fetchone.assert_called_once()


def test_add_country_code_to_db(mock_create_connection, mock_cursor):
    test_cc = "CI"
    test_schema = 'test_schema'

    add_country_code_to_db(test_cc, test_schema,
                           mock_create_connection, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        f"""INSERT INTO {test_schema}.country_codes (country_code) VALUES (%s)""", (test_cc,))

    mock_create_connection.commit.assert_called_once()


def test_check_if_location_in_db_found(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    test_city = "Bonoua"
    test_lat = 5.27247
    test_lon = -3.59625
    test_schema = "test_schema"
    assert check_if_location_in_db(
        test_city, test_lat, test_lon, test_schema, mock_cursor) == (1,)

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT location_id FROM {test_schema}.locations
            WHERE location_name=%s AND location_lat=%s AND location_lon=%s""", (test_city, test_lat, test_lon,))

    mock_cursor.fetchone.assert_called_once()


def test_check_if_location_in_db_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    test_city = "Bonoua"
    test_lat = 5.27247
    test_lon = -3.59625
    test_schema = "test_schema"
    assert check_if_location_in_db(
        test_city, test_lat, test_lon, test_schema, mock_cursor) == None

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT location_id FROM {test_schema}.locations
            WHERE location_name=%s AND location_lat=%s AND location_lon=%s""", (test_city, test_lat, test_lon,))

    mock_cursor.fetchone.assert_called_once()


@patch('load.check_if_country_code_in_db', return_value=(1,))
@patch('load.check_if_timezone_in_db', return_value=(2,))
def test_add_location_to_db(mock_create_connection, mock_cursor):
    test_location_data = (5.27247, -3.59625, "Bonoua", "CI", "Africa/Abidjan")
    test_city = "Bonoua"
    test_lat = 5.27247
    test_lon = -3.59625
    test_timezone_id = 2
    test_cc_id = 1
    test_schema = 'test_schema'

    add_location_to_db(test_location_data, test_schema,
                       mock_create_connection, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        f"""INSERT INTO {test_schema}.locations
                (location_name, location_lat, location_lon,
                 timezone_id, country_code_id)
                VALUES (%s, %s, %s, %s, %s)""", (test_city, test_lat, test_lon, test_timezone_id, test_cc_id,))
    mock_create_connection.commit.assert_called_once()


def test_check_if_species_in_db_found(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    test_schema = "test_schema"
    assert check_if_species_in_db(
        test_common_name, test_scientific_name, test_schema, mock_cursor) == (1,)

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT species_id FROM {test_schema}.plant_species WHERE common_name=%s AND scientific_name=%s""", (test_common_name, test_scientific_name,))

    mock_cursor.fetchone.assert_called_once()


def test_check_if_species_in_db_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    test_schema = "test_schema"
    assert check_if_species_in_db(
        test_common_name, test_scientific_name, test_schema, mock_cursor) == None

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT species_id FROM {test_schema}.plant_species WHERE common_name=%s AND scientific_name=%s""", (test_common_name, test_scientific_name,))

    mock_cursor.fetchone.assert_called_once()


def test_add_species_to_db(mock_create_connection, mock_cursor):
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    test_schema = 'test_schema'

    add_species_to_db(test_common_name, test_scientific_name, test_schema,
                      mock_create_connection, mock_cursor)

    mock_cursor.execute.assert_called_once_with(
        f"""INSERT INTO {
            test_schema}.plant_species (common_name, scientific_name) VALUES (%s, %s)""",
        (test_common_name, test_scientific_name))
    mock_create_connection.commit.assert_called_once()


def test_check_if_plant_in_db_found(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    test_plant_id = 1
    test_schema = "test_schema"
    assert check_if_plant_in_db(
        test_plant_id, test_schema, mock_cursor) == (1,)

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT plant_id FROM {
            test_schema}.plants WHERE plant_id = %s""", (test_plant_id,))
    mock_cursor.fetchone.assert_called_once()


def test_check_if_plant_in_db_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    test_plant_id = 1
    test_schema = "test_schema"
    assert check_if_plant_in_db(
        test_plant_id, test_schema, mock_cursor) == None

    mock_cursor.execute.assert_called_once_with(
        f"""SELECT plant_id FROM {
            test_schema}.plants WHERE plant_id = %s""", (test_plant_id,))
    mock_cursor.fetchone.assert_called_once()


@patch('load.check_if_species_in_db', return_value=(1,))
@patch('load.check_if_location_in_db', return_value=(2,))
def test_add_plant_to_db(mock_create_connection, mock_cursor):
    test_location_data = (5.27247, -3.59625, "Bonoua", "CI", "Africa/Abidjan")
    test_plant_species_id = 1
    test_location_id = 2
    test_plant_id = 3
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    test_schema = 'test_schema'

    assert (add_plant_to_db(test_plant_id, test_common_name, test_scientific_name, test_location_data, test_schema,
                            mock_create_connection, mock_cursor)) == None

    mock_cursor.execute.assert_called_once_with(
        f"""INSERT INTO {test_schema}.plants (plant_id, species_id, location_id) VALUES (%s, %s, %s)""", (test_plant_id, test_plant_species_id, test_location_id))

    mock_create_connection.commit.assert_called_once()


@patch('load.check_if_botanist_in_db', return_value=(1,))
def test_botanist_checks_found(mock_create_connection, mock_cursor):
    botanist_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '123-456-7890'
    }
    test_schema = "test_schema"
    assert botanist_checks(
        botanist_data, test_schema, mock_create_connection, mock_cursor) == 1


@patch('load.check_if_botanist_in_db', side_effect=[None, (1,)])
@patch('load.add_botanist_to_db')
def test_botanist_checks_not_found(mock_add_botanist_to_db, mock_create_connection, mock_cursor):
    botanist_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '123-456-7890'
    }
    test_schema = "test_schema"
    assert (botanist_checks(botanist_data, test_schema,
                            mock_create_connection, mock_cursor)) == 1
    mock_add_botanist_to_db.assert_called_once_with(
        botanist_data, test_schema, mock_create_connection, mock_cursor)


@patch('load.check_if_timezone_in_db', return_value=(1,))
@patch('load.add_timezone_to_db')
def test_timezone_checks_found(mock_add_timezone_to_db, mock_create_connection, mock_cursor):
    timezone_name = "Africa/Abidjan"
    test_schema = "test_schema"
    assert timezone_checks(timezone_name, test_schema,
                           mock_create_connection, mock_cursor) == None
    mock_add_timezone_to_db.assert_not_called()


@patch('load.check_if_timezone_in_db', return_value=None)
@patch('load.add_timezone_to_db')
def test_timezone_checks_not_found(mock_add_timezone_to_db, mock_create_connection, mock_cursor):
    timezone_name = "Africa/Abidjan"
    test_schema = "test_schema"
    timezone_checks(timezone_name, test_schema,
                    mock_create_connection, mock_cursor)
    mock_add_timezone_to_db.assert_called_once_with(timezone_name, test_schema,
                                                    mock_create_connection, mock_cursor)


@patch('load.check_if_country_code_in_db', return_value=(1,))
@patch('load.add_country_code_to_db')
def test_country_code_checks_found(mock_add_country_code_to_db, mock_create_connection, mock_cursor):
    cc = "CI"
    test_schema = "test_schema"
    assert country_code_checks(cc, test_schema,
                               mock_create_connection, mock_cursor) == None
    mock_add_country_code_to_db.assert_not_called()


@patch('load.check_if_country_code_in_db', return_value=None)
@patch('load.add_country_code_to_db')
def test_country_code_checks_not_found(mock_add_country_code_to_db, mock_create_connection, mock_cursor):
    cc = "CI"
    test_schema = "test_schema"
    assert country_code_checks(cc, test_schema,
                               mock_create_connection, mock_cursor) == None
    mock_add_country_code_to_db.assert_called_once_with(cc, test_schema,
                                                        mock_create_connection, mock_cursor)


@patch('load.check_if_location_in_db', return_value=(1,))
@patch('load.add_location_to_db')
def test_location_checks_found(mock_add_location_to_db, mock_create_connection, mock_cursor):
    location_data = (5.27247, -3.59625, "Bonoua", "CI", "Africa/Abidjan")
    test_schema = "test_schema"
    location_checks(location_data, test_schema,
                    mock_create_connection, mock_cursor)
    mock_add_location_to_db.assert_not_called()


@patch('load.check_if_location_in_db', return_value=None)
@patch('load.add_location_to_db')
def test_location_checks_not_found(mock_add_location_to_db, mock_create_connection, mock_cursor):
    location_data = (5.27247, -3.59625, "Bonoua", "CI", "Africa/Abidjan")
    test_schema = "test_schema"
    location_checks(location_data, test_schema,
                    mock_create_connection, mock_cursor)
    mock_add_location_to_db.assert_called_once_with(location_data, test_schema,
                                                    mock_create_connection, mock_cursor)


@patch('load.check_if_species_in_db', return_value=(1,))
@patch('load.add_species_to_db')
def test_plant_species_checks_found(mock_add_species_to_db, mock_create_connection, mock_cursor):
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    test_schema = "test_schema"
    plant_species_checks(test_common_name, test_scientific_name, test_schema,
                         mock_create_connection, mock_cursor)
    mock_add_species_to_db.assert_not_called()


@patch('load.check_if_species_in_db', return_value=None)
@patch('load.add_species_to_db')
def test_plant_species_checks_not_found(mock_add_species_to_db, mock_create_connection, mock_cursor):
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    test_schema = "test_schema"
    plant_species_checks(test_common_name, test_scientific_name, test_schema,
                         mock_create_connection, mock_cursor)
    mock_add_species_to_db.assert_called_once_with(test_common_name, test_scientific_name, test_schema,
                                                   mock_create_connection, mock_cursor)


@patch('load.check_if_plant_in_db', return_value=(1,))
@patch('load.add_plant_to_db')
def test_plant_checks_found(mock_add_plant_to_db, mock_create_connection, mock_cursor):
    plant_id = 1
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    location_data = (5.27247, -3.59625, "Bonoua", "CI", "Africa/Abidjan")
    test_schema = "test_schema"
    plant_checks(plant_id, test_common_name, test_scientific_name, location_data, test_schema,
                 mock_create_connection, mock_cursor)
    mock_add_plant_to_db.assert_not_called()


@patch('load.check_if_plant_in_db', return_value=None)
@patch('load.add_plant_to_db')
def test_plant_checks_not_found(mock_add_plant_to_db, mock_create_connection, mock_cursor):
    plant_id = 1
    test_common_name = "Bird of paradise"
    test_scientific_name = "Heliconia schiedeana 'Fire and Ice'"
    location_data = (5.27247, -3.59625, "Bonoua", "CI", "Africa/Abidjan")
    test_schema = "test_schema"
    plant_checks(plant_id, test_common_name, test_scientific_name, location_data, test_schema,
                 mock_create_connection, mock_cursor)
    mock_add_plant_to_db.assert_called_once_with(plant_id, test_common_name, test_scientific_name, location_data, test_schema,
                                                 mock_create_connection, mock_cursor)
