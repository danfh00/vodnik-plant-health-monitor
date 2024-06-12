from unittest.mock import MagicMock, patch
from seeding import get_unique_timezones, populate_timezones
import pytest


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


def test_get_unique_timezones(generate_response):
    assert len(get_unique_timezones(generate_response)) == 5


def test_populate_timezones(mock_create_connection):
    timezone_names = [("America/Chicago",),
                      ("America/Los_Angeles",), ("Europe/Berlin",)]
    test_schema = "test_schema"

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_create_connection.return_value = mock_conn

    populate_timezones(timezone_names, test_schema)

    mock_cursor.executemany.assert_called_once_with(
        f"INSERT INTO {test_schema}.timezones (timezone) VALUES (%s)", timezone_names)

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
