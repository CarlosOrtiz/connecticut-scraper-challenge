import os


def set_downloads_dir(base_dir: str, folder: str = "downloads") -> str:
    downloads_dir = os.path.join(base_dir, folder)
    os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir


def download_pdf(session, pdf_url: str, downloads_dir: str) -> dict:
    filename = pdf_url.split("/")[-1]
    file_path = os.path.join(downloads_dir, filename)

    if os.path.exists(file_path):
        return {
            "pdf_url": pdf_url,
            "pdf_filename": filename,
            "pdf_local_path": file_path,
            "downloaded": False,
        }

    response = session.get(pdf_url, timeout=30)
    response.raise_for_status()

    with open(file_path, "wb") as file:
        file.write(response.content)

    return {
        "pdf_url": pdf_url,
        "pdf_filename": filename,
        "pdf_local_path": file_path,
        "downloaded": True,
    }
