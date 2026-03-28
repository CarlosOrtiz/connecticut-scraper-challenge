import logging
import os
from datetime import datetime, timezone

import requests

from scripts.common.gemini import extract_pdf_data
from scripts.common.db import PromptsRepository, TaxSalesRepository
from scripts.tax_sales.client import TaxSalesClient
from scripts.tax_sales.downloader import set_downloads_dir, download_pdf
from scripts.tax_sales.parser import parse_tax_sales

logger = logging.getLogger("scrape_tax_sales")


async def scrape_tax_sales() -> list[dict]:
    client = TaxSalesClient()
    session = client.get_session()

    try:
        response = session.get(client.base_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error(f"Error consultando tax sales: {exc}")
        return []

    results = parse_tax_sales(response.text)
    if not results:
        logger.warning("No se encontraron tax sales en la página.")
        return []

    downloads_dir = set_downloads_dir(os.path.dirname(__file__), "downloads")
    prompts_repo = PromptsRepository()
    tax_sales_repo = TaxSalesRepository()

    try:
        active_prompts = await prompts_repo.get_prompts()
        logger.info("Se encontraron %s prompts activos.", len(active_prompts))
    except Exception as exc:
        logger.error("Error consultando prompts activos: %s", exc)
        return []

    documents_to_store = []

    for sale in results:
        town = sale["town"]

        document = {
            "town": town,
            "auction_date": sale["auction_date"],
            "location": sale["location"],
            "extracted_data": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if not sale["pdf_links"]:
            logger.warning("Sin PDFs: %s", town)
            documents_to_store.append(document)
            try:
                await tax_sales_repo.upsert_tax_sale(document)
            except Exception as exc:
                logger.error("Error guardando tax sale %s: %s", town, exc)
            continue

        for pdf_url in sale["pdf_links"]:
            try:
                pdf_meta = download_pdf(session, pdf_url, downloads_dir)
                logger.info(
                    "PDF %s [%s]: %s",
                    "descargado" if pdf_meta["downloaded"] else "omitido",
                    town,
                    pdf_meta["pdf_filename"],
                )
            except Exception as exc:
                logger.error("Error descargando PDF %s: %s", pdf_url, exc)
                continue

            gemini_fields = {}

            for prompt in active_prompts:
                try:
                    gemini_result = extract_pdf_data(
                        pdf_meta["pdf_local_path"],
                        prompt,
                    )
                    gemini_fields.update(gemini_result)
                except Exception as exc:
                    logger.error(
                        "Error ejecutando prompt %s para %s: %s",
                        prompt.get("key"),
                        pdf_meta["pdf_filename"],
                        exc,
                    )

            document["extracted_data"].append(
                {
                    "pdf_url": pdf_meta["pdf_url"],
                    "pdf_local_path": pdf_meta["pdf_local_path"],
                    "pdf_filename": pdf_meta["pdf_filename"],
                    **gemini_fields,
                }
            )

            documents_to_store.append(document)

            try:
                await tax_sales_repo.upsert_tax_sale(document)
            except Exception as exc:
                logger.error(
                    "Error guardando tax sale %s: %s", pdf_meta["pdf_filename"], exc
                )

    return documents_to_store
