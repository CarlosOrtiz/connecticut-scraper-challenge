import os
from pathlib import Path
from typing import Any

from requests import Session


LOCAL_DOWNLOADS_DIR = Path(__file__).resolve().parent / "downloads"
LAMBDA_DOWNLOADS_DIR = Path("/tmp/downloads")


def set_downloads_dir() -> str:
    is_lambda = "AWS_LAMBDA_FUNCTION_NAME" in os.environ
    downloads_dir = LAMBDA_DOWNLOADS_DIR if is_lambda else LOCAL_DOWNLOADS_DIR
    downloads_dir.mkdir(parents=True, exist_ok=True)
    return str(downloads_dir)


def download_pdf(
    session: Session,
    pdf_url: str,
    downloads_dir: str,
) -> dict[str, Any]:
    filename = pdf_url.split("/")[-1]
    file_path = Path(downloads_dir) / filename

    if file_path.exists():
        return {
            "pdf_url": pdf_url,
            "pdf_filename": filename,
            "pdf_local_path": str(file_path),
            "downloaded": False,
        }

    response = session.get(pdf_url, timeout=30)
    response.raise_for_status()

    file_path.write_bytes(response.content)

    return {
        "pdf_url": pdf_url,
        "pdf_filename": filename,
        "pdf_local_path": str(file_path),
        "downloaded": True,
    }
