import logging
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from scripts.common.db import ForeclosuresRepository
from scripts.foreclosures.client import ForeclosuresClient
from scripts.foreclosures.normalize_property import normalize_property
from scripts.foreclosures.city_parser import extract_city_data

logger = logging.getLogger(__name__)


async def scrape_foreclosures() -> None:
    logger.info("Iniciando scraper de Foreclosures...")

    client = ForeclosuresClient()
    session = client.get_session()
    repo = ForeclosuresRepository()

    try:
        existing_towns = await repo.get_existing_towns()
        logger.info(
            f"Se encontraron {len(existing_towns)} towns ya guardados en MongoDB."
        )
    except Exception as e:
        logger.error(f"Error consultando towns existentes: {e}")
        return

    try:
        response = session.get(client.index_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error crítico conectando al índice: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    panel = soup.find("div", id="ctl00_cphBody_Panel1")

    if not panel:
        logger.error("No se encontró el panel de ciudades en la página principal.")
        return

    links = panel.find_all("a")
    logger.info(f"Se encontraron {len(links)} ciudades para procesar.")

    results = []

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
                    f"✅ Proceso terminado. Modificados/Nuevos: {result.modified_count + result.upserted_count}"
                )
        except Exception as e:
            logger.error(f"Error guardando en base de datos: {e}")
    else:
        logger.warning("No se encontraron towns nuevos para guardar.")
