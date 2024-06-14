from datetime import datetime

from transform import format_phone_number, format_recording_taken, format_watered_at, apply_transformations


def test_formatting_phone_number():
    assert format_phone_number("(868)123-456x789") == "868123456789"


def test_formatting_recording_taken_value():
    test_date = "2024-06-13 20:59:29"
    expected_value = datetime.strptime(test_date, '%Y-%m-%d %H:%M:%S')
    assert format_recording_taken(
        test_date) == expected_value.strftime("%Y-%m-%d %H:%M:%S")


def test_formatting_watered_at_value():
    test_watered_at_value = "Thu, 13 Jun 2024 13:04:57 GMT"
    expected_value = datetime.strptime(
        test_watered_at_value, '%a, %d %b %Y %H:%M:%S %Z')
    assert format_watered_at(
        test_watered_at_value) == expected_value.strftime("%Y-%m-%d %H:%M:%S")


def test_applying_transformations():
    example_data = [{"botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "001-481-273-3691x127"}, "last_watered": "Thu, 13 Jun 2024 13:04:57 GMT", "name": "Dragon tree,",
                     "origin_location": ["43.50891", "16.43915", "Split", "HR", "Europe/Zagreb"], "plant_id": 10, "recording_taken": "2024-06-13 20:59:29", "soil_moisture": 72.543334729026, "temperature": 14.007480779956},
                    {"botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "001-481-273-3691x127"},
                     "images": {"license": 451, "license_name": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
                                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "medium_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                                "original_url": "https://perenual.com/storage/image/upgrade_access.jpg", "regular_url": "https://perenual.com/storage/image/upgrade_access.jpg",
                                "small_url": "https://perenual.com/storage/image/upgrade_access.jpg", "thumbnail": "https://perenual.com/storage/image/upgrade_access.jpg"},
                     "last_watered": "Thu, 13 Jun 2024 13:05:43 GMT", "name": "Sansevieria Trifasciata", "origin_location": ["23.29549", "113.82465", "Licheng", "CN", "Asia/Shanghai"],
                     "plant_id": 31, "recording_taken": "2024-06-13 21:23:08", "scientific_name": ["Sansevieria trifasciata"], "soil_moisture": 71.3028826740385, "temperature": 13.3688828085612}]

    expected_output = [{"plant_id": 10, "name": "dragon tree,", "scientific_name": None, "last_watered": "2024-06-13 13:04:57", "temperature": 14.007480779956,
                        "soil_moisture": 72.543334729026, "reading_at": "2024-06-13 20:59:29", "origin_location": [43.50891, 16.43915, "Split", "HR", "Europe/Zagreb"],
                        "botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "0014812733691127"}}, {"plant_id": 31, "name": "sansevieria trifasciata",
                                                                                                                                       "scientific_name": "sansevieria trifasciata", "last_watered": "2024-06-13 13:05:43", "temperature": 13.3688828085612, "soil_moisture": 71.3028826740385,
                                                                                                                                       "reading_at": "2024-06-13 21:23:08", "origin_location": [23.29549, 113.82465, "Licheng", "CN", "Asia/Shanghai"], "botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "0014812733691127"}}]

    assert apply_transformations(example_data) == expected_output
