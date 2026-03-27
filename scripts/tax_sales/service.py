import logging
import os

import requests

from bs4 import BeautifulSoup
from scripts.tax_sales.client import TaxSalesClient

logger = logging.getLogger("scrape_tax_sales")


def scrape_tax_sales() -> list[dict]:
    folder_name = "downloads"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    client = TaxSalesClient()
    session = client.get_session()

    try:
        response = session.get(client.base_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error(f"Error consultando tax sales: {exc}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
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

    for sale in results:
        town = sale["town"]

        if not sale["pdf_links"]:
            logger.warning(f"Sin PDFs: {town}")
            continue

        for pdf_url in sale["pdf_links"]:
            response = session.get(pdf_url, timeout=30)
            response.raise_for_status()

            filename = pdf_url.split("/")[-1]
            file_path = os.path.join("downloads", filename)

            if os.path.exists(file_path):
                logger.warning(f"Ya existe, se omite [{town}]: {filename}")
                continue

            with open(file_path, "wb") as file:
                file.write(response.content)

        logger.info(f"Descargado [{town}]: {filename}")

    return results
