import logging
from typing import TypedDict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from src.repositories.foreclosures_repository import ForeclosuresRepository
from src.scrapers.foreclosures.client import ForeclosuresClient
from src.scrapers.foreclosures.normalize_property import normalize_property
from src.scrapers.foreclosures.city_parser import extract_city_data

logger = logging.getLogger(__name__)


class ScrapeForeclosuresResult(TypedDict):
    success: bool
    modified_count: int
    upserted_count: int


async def scrape_foreclosures() -> ScrapeForeclosuresResult | None:
    logger.info("Iniciando scraper de Foreclosures...")

    client = ForeclosuresClient()
    session = client.get_session()
    repo = ForeclosuresRepository()

    try:
        existing_towns = await repo.get_existing_towns()
        logger.info(
            "Se encontraron %s towns ya guardados en MongoDB: ", len(existing_towns)
        )
    except Exception as e:
        logger.error("Error consultando towns existentes: %s", e)
        return

    try:
        response = session.get(client.index_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Error crítico conectando al índice: %s", e)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    panel = soup.find("div", id="ctl00_cphBody_Panel1")

    if not panel:
        logger.error("No se encontró el panel de ciudades en la página principal.")
        return

    links = panel.find_all("a")
    logger.info("Se encontraron %s ciudades para procesar: ", len(links))

    results: list[dict] = []

    for link in links:
        town_name = link.get_text(strip=True).upper()
        href = link.get("href")

        if town_name in existing_towns:
            logger.info(f"Omitiendo {town_name}: ya existe en MongoDB.")
            continue

        logger.info(f"Extrayendo datos de: {town_name}...")
        properties = extract_city_data(session, client.base_url, town_name, href)

        normalized_properties = [normalize_property(city) for city in properties]

        if normalized_properties:
            results.append(
                {
                    "town": town_name,
                    "foreclosures": normalized_properties,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    if results:
        logger.info("Guardando datos en MongoDB...")
        try:
            result = await repo.bulk_upsert_towns(results)
            if result:
                logger.info(
                    "✅ Proceso terminado. Modificados/Nuevos: %s",
                    result.modified_count + result.upserted_count,
                )
                return {
                    "success": True,
                    "modified_count": result.modified_count,
                    "upserted_count": result.upserted_count,
                }

        except Exception as e:
            logger.error("Error guardando en base de datos: %s", e)
    else:
        logger.warning("No se encontraron towns nuevos para guardar.")
