from scripts.tax_sales.parser import parse_tax_sales


def test_parse_tax_sales_page_extracts_data():
    html = """
    <div class="entry-content">
        <p>
            MUNICIPALITY: Town of Woodstock<br>
            AUCTION DATE: 10:00 a.m. on April 21, 2026<br>
            LOCATION: Woodstock Town Hall, 415 Route 169, Woodstock CT
        </p>
        <p>
            <a href="https://example.com/test.pdf">Notice</a>
        </p>
        <hr>
    </div>
    """

    result = parse_tax_sales(html)

    assert len(result) == 1
    assert result[0]["town"] == "WOODSTOCK"
    assert result[0]["auction_date"] == "10:00 a.m. on April 21, 2026"
    assert result[0]["location"] == "Woodstock Town Hall, 415 Route 169, Woodstock CT"
    assert result[0]["pdf_links"] == ["https://example.com/test.pdf"]
