import logging
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests import Session

logger = logging.getLogger(__name__)


def extract_city_data(
    session: Session, base_url: str, town_name: str, href: str
) -> list[dict[str, Any]]:
    city_url = f"{base_url}{href}"

    try:
        response = session.get(city_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accediendo a {town_name}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id=lambda x: x and "GridView" in x)
    if not table:
        return []

    rows = table.find_all("tr")
    if len(rows) < 2:
        return []

    headers = [
        th.get_text(strip=True).lower().replace(" ", "_").replace(".", "")
        for th in rows[0].find_all(["th", "td"])
    ]

    foreclosures: list[dict[str, Any]] = []

    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) == len(headers):
            row_data = {}
            for i, cell in enumerate(cells):
                row_data[headers[i]] = cell.get_text(strip=True)
            foreclosures.append(row_data)

    return foreclosures
