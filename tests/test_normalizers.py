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
