import pytest
from unittest.mock import MagicMock, patch

from load import check_if_botanist_in_db


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
