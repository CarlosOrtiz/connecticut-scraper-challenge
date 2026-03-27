import requests
import urllib3
from requests.adapters import HTTPAdapter

from scripts.common.config import get_settings

settings = get_settings()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = urllib3.util.ssl_.create_urllib3_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super(LegacySSLAdapter, self).init_poolmanager(*args, **kwargs)


class ScraperClient:
    def __init__(self, base_url: str, use_legacy_ssl: bool = False):
        self.base_url = base_url.rstrip("/") + "/"
        self.use_legacy_ssl = use_legacy_ssl

    def get_session(self) -> requests.Session:
        session = requests.Session()
        if self.use_legacy_ssl:
            session.mount("https://", LegacySSLAdapter())

        session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        return session
