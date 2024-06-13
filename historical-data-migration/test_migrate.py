# pylint: skip-file
from migrate import fetch_historical_readings, remove_historical_readings, DATE_CONSTRAINT
from migrate import get_prefix, create_reading_file
from unittest.mock import MagicMock
import pytest
import datetime


@pytest.fixture
def fake_readings():
    return [(1, 5, "2024-06-12 18:38:08",
             81.2054315735587, 11.5725865367479, 2, "2024-06-12 15:38:08"),
            (2, 9, "2024-06-10 18:38:08",
             81.2054315735587, 11.5725865367479, 2, "2024-06-10 15:38:08")]


@pytest.fixture
def fake_csv_output():
    return """reading_id,plant_id,reading_at,moisture,temp,botanist_id,watered_at
1,5,2024-06-12 18:38:08,81.2054315735587,11.5725865367479,2,2024-06-12 15:38:08
2,9,2024-06-10 18:38:08,81.2054315735587,11.5725865367479,2,2024-06-10 15:38:08
"""


def test_fetch_historical_readings():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    fetch_historical_readings(mock_conn, DATE_CONSTRAINT)

    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT * FROM gamma.readings" in call_args[0]
    assert "WHERE reading_at <= %s" in call_args[0]


def test_remove_historical_readings():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    remove_historical_readings(mock_conn, DATE_CONSTRAINT)

    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "DELETE FROM gamma.readings" in call_args[0]
    assert "WHERE reading_at <= %s" in call_args[0]


def test_get_prefix():
    input = datetime.date(2020, 5, 17)

    assert get_prefix(input) == "wc-11-05-2020/"


def test_create_reading_file(fake_readings, fake_csv_output):
    input = fake_readings
    output = fake_csv_output

    buffer = create_reading_file(input)
    buffer.seek(0)
    actual_csv = buffer.read().decode('utf-8')

    assert actual_csv == output
