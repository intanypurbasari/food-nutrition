from src.cleaning.normalizers import normalize_category, normalize_column_name, normalize_food_name, normalize_numeric


def test_normalize_numeric_edge_cases():
    assert normalize_numeric("12,5") == 12.5
    assert normalize_numeric("-") is None
    assert normalize_numeric("tr") is None
    assert normalize_numeric("NA") is None
    assert normalize_numeric("") is None
    assert normalize_numeric("100 mg") == 100.0


def test_name_normalizers():
    assert normalize_column_name("Vitamin C (mg)") == "vitamin_c_mg"
    assert normalize_food_name("  Nasi   Putih!  ") == "nasi putih"
    assert normalize_category(" Serealia ") == "serealia"


def test_normalize_numeric_thousands_separator():
    assert normalize_numeric("3,784") == 3784.0
    assert normalize_numeric("1,234.5") == 1234.5
    assert normalize_numeric("11,507") == 11507.0
    assert normalize_numeric("102,198.4") == 102198.4


def test_normalize_numeric_keeps_existing_formats():
    assert normalize_numeric("357.0") == 357.0
    assert normalize_numeric("0,5") == 0.5
    assert normalize_numeric("12,05") == 12.05
