import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("parse_tax_sales")


def parse_tax_sales(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="entry-content")

    if not content:
        return []

    results = []
    current_sale = None

    for item in content.find_all(["p", "hr"]):
        if item.name == "hr":
            if current_sale:
                results.append(current_sale)
                current_sale = None
            continue

        parts = [part.strip() for part in item.stripped_strings if part.strip()]
        if not parts:
            continue

        municipality_part = next(
            (part for part in parts if part.startswith("MUNICIPALITY:")),
            None,
        )

        if municipality_part:
            if current_sale:
                results.append(current_sale)

            municipality_text = municipality_part.replace("MUNICIPALITY:", "").strip()

            if "Town of" in municipality_text:
                municipality_text = municipality_text.split("Town of", 1)[1].strip()
            elif "City of" in municipality_text:
                municipality_text = municipality_text.split("City of", 1)[1].strip()

            if "(in " in municipality_text and ")" in municipality_text:
                start = municipality_text.find("(in ") + len("(in ")
                end = municipality_text.find(")", start)
                municipality_text = municipality_text[start:end].strip()

            current_sale = {
                "town": municipality_text.upper(),
                "auction_date": "",
                "location": "",
                "pdf_links": [],
            }

            for part in parts:
                if part.startswith("AUCTION DATE:"):
                    current_sale["auction_date"] = part.replace(
                        "AUCTION DATE:", ""
                    ).strip()
                elif part.startswith("LOCATION:"):
                    current_sale["location"] = part.replace("LOCATION:", "").strip()

        if not current_sale:
            continue

        links = item.find_all("a", href=True)
        for link in links:
            href = link["href"].strip()
            if href.endswith(".pdf") and href not in current_sale["pdf_links"]:
                current_sale["pdf_links"].append(href)

    if current_sale:
        results.append(current_sale)

    return results
