from unittest.mock import MagicMock, patch
import pytest

from seeding import (
    get_unique_timezones, populate_timezones, get_unique_country_codes, populate_country_codes,
    get_unique_locations, populate_locations, extract_name_and_scientific_name, get_unique_plant_names,
    populate_plant_species, combine_plant_and_location_id, populate_plants, get_timezone_id_map,
    get_country_code_id_map, get_locations_id_map, get_plant_names_id_map
)


@pytest.fixture
def generate_response():
    return [
        {"botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "001-481-273-3691x127"}, "last_watered": "Tue, 11 Jun 2024 13:54:32 GMT", "name": "Venus flytrap", "origin_location": [
            "33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"], "plant_id": 1, "recording_taken": "2024-06-12 13:30:53", "soil_moisture": 16.356331333661416, "temperature": 12.036746782531676},
        {"botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"}, "last_watered": "Tue, 11 Jun 2024 14:10:54 GMT", "name": "Corpse flower", "origin_location": [
            "7.65649", "4.92235", "Efon-Alaaye", "NG", "Africa/Lagos"], "plant_id": 2, "recording_taken": "2024-06-12 13:31:22", "soil_moisture": 23.5408907297543, "temperature": 9.14518651262138},
        {"botanist": {"email": "eliza.andrews@lnhm.co.uk", "name": "Eliza Andrews", "phone": "(846)669-6651x75948"}, "last_watered": "Tue, 11 Jun 2024 14:50:16 GMT", "name": "Rafflesia arnoldii", "origin_location": [
            "-19.32556", "-41.25528", "Resplendor", "BR", "America/Sao_Paulo"], "plant_id": 3, "recording_taken": "2024-06-12 13:32:31", "soil_moisture": 21.483249727185395, "temperature": 10.012121459881186},
        {"botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"}, "last_watered": "Wed, 12 Jun 2024 13:16:25 GMT", "name": "Black bat flower", "origin_location": [
            "13.70167", "-89.10944", "Ilopango", "SV", "America/El_Salvador"], "plant_id": 4, "recording_taken": "2024-06-12 13:32:47", "soil_moisture": 99.02299588667992, "temperature": 11.336964503968225},
        {"botanist": {"email": "eliza.andrews@lnhm.co.uk", "name": "Eliza Andrews", "phone": "(846)669-6651x75948"}, "last_watered": "Tue, 11 Jun 2024 13:36:47 GMT", "name": "Canna \u2018Striata\u2019", "origin_location": [
            "49.68369", "8.61839", "Bensheim", "DE", "Europe/Berlin"], "plant_id": 13, "recording_taken": "2024-06-12 13:35:59", "soil_moisture": 20.850031831347394, "temperature": 25.935728846736353},
        {"error": "plant not found", "plant_id": 7},
        {"botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "001-481-273-3691x127"}, "images": {"license": 451, "license_name": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "medium_url": "https://perenual.com/storage/image/upgrade_access.jpg", "original_url": "https://perenual.com/storage/image/upgrade_access.jpg", "regular_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                                                                                                                                     "small_url": "https://perenual.com/storage/image/upgrade_access.jpg", "thumbnail": "https://perenual.com/storage/image/upgrade_access.jpg"}, "last_watered": "Tue, 11 Jun 2024 14:12:43 GMT", "name": "Cactus", "origin_location": ["50.9803", "11.32903", "Weimar", "DE", "Europe/Berlin"], "plant_id": 9, "recording_taken": "2024-06-12 13:35:42", "scientific_name": ["Pereskia grandifolia"], "soil_moisture": 18.667458803864733, "temperature": 10.611753219010195}
    ]


@pytest.fixture
def mock_create_connection():
    with patch('pymssql.connect') as mock:
        yield mock


@pytest.fixture
def mock_cursor_connection(mock_create_connection):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_create_connection.return_value = mock_conn
    return mock_cursor, mock_conn


def setup_mock(mock_cursor, fetchall_data):
    mock_cursor.fetchall.return_value = fetchall_data


@pytest.mark.parametrize("function, expected_length", [
    (get_unique_timezones, 5),
    (get_unique_country_codes, 5),
    (get_unique_plant_names, 6)
])
def test_getting_unique_values_functions(function, expected_length, generate_response):
    assert len(function(generate_response)) == expected_length


def test_get_unique_locations(generate_response):
    test_timezone_map = {"America/Los_Angeles": 1, "Africa/Lagos": 2,
                         "America/Sao_Paulo": 3, "America/El_Salvador": 4, "Europe/Berlin": 5}
    test_country_code_map = {"US": 1, "NG": 2, "BR": 3, "SV": 4, "DE": 5}
    assert len(get_unique_locations(generate_response,
               test_timezone_map, test_country_code_map)) == 6
    assert len(get_unique_locations(
        generate_response, test_timezone_map, test_country_code_map)[0]) == 5


def test_extract_name_and_scientific_name():
    assert extract_name_and_scientific_name({"name": "test", "scientific_name": [
                                            "another_test_name"]}) == ("test", "another_test_name")


def test_extract_name_with_no_scientific_name():
    assert extract_name_and_scientific_name({"name": "test"}) == ("test", None)


def test_combine_plant_and_location_id(generate_response):
    plant_mapping = {
        ("venus flytrap", None): 1,
        ("corpse flower", None): 2,
        ("rafflesia arnoldii", None): 3,
        ("black bat flower", None): 4,
        ("canna ‘striata’", None): 5,
        ("cactus", "pereskia grandifolia"): 6
    }
    location_mapping = {
        (33.95015, -118.03917): 1,
        (7.65649, 4.92235): 2,
        (-19.32556, -41.25528): 3,
        (13.70167, -89.10944): 4,
        (49.68369, 8.61839): 5,
        (50.9803, 11.32903): 6
    }
    assert combine_plant_and_location_id(generate_response, plant_mapping, location_mapping) == [
        (13, 5, 5), (2, 2, 2), (9, 6, 6), (3, 3, 3), (4, 4, 4), (1, 1, 1)]


@pytest.mark.parametrize("function, data, schema, query", [
    (populate_timezones, [("America/Chicago",), ("America/Los_Angeles",), ("Europe/Berlin",)],
     "test_schema", "INSERT INTO test_schema.timezones (timezone) VALUES (%s)"),
    (populate_country_codes, [("UK",), ("DE",)], "test_schema",
     "INSERT INTO test_schema.country_codes (country_code) VALUES (%s)"),
    (populate_locations, [("Brunswick", 43.9145200, -69.9653300, 19, 17), ("El Achir", 36.0638600, 4.6274400, 26, 24), ("Magomeni", -6.8000000, 39.2500000, 7, 5)],
     "test_schema", "INSERT INTO test_schema.locations (location_name, location_lat, location_lon, timezone_id, country_code_id) VALUES (%s, %s, %s, %s, %s)"),
    (populate_plant_species, [("test", "test1"), ("testt", "test2")], "test_schema",
     "INSERT INTO test_schema.plant_species (common_name, scientific_name) VALUES (%s, %s)"),
    (populate_plants, [[(13, 5, 5), (2, 2, 2), (9, 6, 6), (3, 3, 3), (4, 4, 4), (1, 1, 1)]], "test_schema",
     "INSERT INTO test_schema.plants (plant_id, naming_id, location_id) VALUES (%s, %s, %s)")
])
def test_populate_functions(function, data, schema, query, mock_cursor_connection):
    mock_cursor, mock_conn = mock_cursor_connection
    function(data, schema)
    mock_cursor.executemany.assert_called_once_with(query, data)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@pytest.mark.parametrize("function, fetchall_data, expected_map", [
    (get_timezone_id_map, [[1, "America/Los_Angeles"], [2,
     "Africa/Lagos"]], {"America/Los_Angeles": 1, "Africa/Lagos": 2}),
    (get_country_code_id_map, [[1, "UK"], [2, "ID"]], {"UK": 1, "ID": 2}),
    (get_locations_id_map, [[1, 123.12345, 23.12345], [2, 12.123456, 11.12345]], {
     (123.12345, 23.12345): 1, (12.123456, 11.12345): 2}),
    (get_plant_names_id_map, [[1, "example", None], [2, "test", "scientific test name"]], {
     ("example", None): 1, ("test", "scientific test name"): 2})
])
def test_get_id_map_functions(function, fetchall_data, expected_map, mock_cursor_connection):
    mock_cursor, _ = mock_cursor_connection
    setup_mock(mock_cursor, fetchall_data)
    assert function("test_schema") == expected_map
