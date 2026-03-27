import re


def normalize_property(raw_item):
    index = raw_item.get("#", "").strip()
    sale_datetime_raw = raw_item.get("sale_date", "").strip()
    docket_number = raw_item.get("docket_number", "").strip()
    sale_and_address_raw = raw_item.get("type_of_sale_&_property_address", "").strip()

    sale_date = sale_datetime_raw
    sale_time = ""
    sale_type = ""
    property_address = ""

    sale_datetime_match = re.match(
        r"^(\d{2}/\d{2}/\d{4})(\d{1,2}:\d{2}[AP]M)$", sale_datetime_raw
    )
    if sale_datetime_match:
        sale_date = sale_datetime_match.group(1)
        sale_time = sale_datetime_match.group(2)

    if "ADDRESS:" in sale_and_address_raw:
        sale_type_part, address_part = sale_and_address_raw.split("ADDRESS:", 1)
        sale_type = sale_type_part.replace(
            "PUBLIC AUCTION FORECLOSURE SALE:", ""
        ).strip()
        property_address = address_part.strip()
    else:
        sale_type = sale_and_address_raw

    return {
        "index": index,
        "sale_date": sale_date,
        "sale_time": sale_time,
        "docket_number": docket_number,
        "sale_type": sale_type,
        "property_address": property_address,
        # "raw": raw_item,
    }
