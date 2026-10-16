from src.scrapers.tkpi_scraper import _first_number


def test_first_number_keeps_decimals_after_thousands_separator():
    assert _first_number("2,522.6 mg") == "2,522.6"
    assert _first_number("4,303.45 mg") == "4,303.45"
    assert _first_number("1,044.20 mg") == "1,044.20"
    assert _first_number("3,784 mcg") == "3,784"


def test_first_number_simple_values():
    assert _first_number("0.58 mg") == "0.58"
    assert _first_number("347 Kal") == "347"
    assert _first_number("12,5 g") == "12,5"
    assert _first_number("1234,5 g") == "1234,5"
    assert _first_number("-") is None
