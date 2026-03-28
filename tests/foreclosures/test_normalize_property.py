from scripts.foreclosures.normalize_property import normalize_property


def test_normalize_property_splits_main_fields():
    raw_item = {
        "#": "1",
        "sale_date": "03/28/202612:00PM",
        "docket_number": "TTDCV256034812S",
        "type_of_sale_&_property_address": "PUBLIC AUCTION FORECLOSURE SALE:ResidentialADDRESS: 39 Gilead Road, Andover, CT",
    }

    result = normalize_property(raw_item)

    assert result["index"] == "1"
    assert result["sale_date"] == "03/28/2026"
    assert result["sale_time"] == "12:00PM"
    assert result["sale_type"] == "Residential"
    assert result["property_address"] == "39 Gilead Road, Andover, CT"
