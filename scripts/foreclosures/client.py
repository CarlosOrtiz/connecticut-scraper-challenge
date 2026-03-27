import requests
import urllib3
from requests.adapters import HTTPAdapter

from scripts.common.config import get_settings

settings = get_settings()

BASE_URL = (
    settings.BASE_URL_CT or "https://sso.eservices.jud.ct.gov/Foreclosures/Public/"
).rstrip("/") + "/"

INDEX_URL = f"{BASE_URL}PendPostbyTownList.aspx"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = urllib3.util.ssl_.create_urllib3_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super(LegacySSLAdapter, self).init_poolmanager(*args, **kwargs)


def get_session():
    session = requests.Session()
    session.mount("https://", LegacySSLAdapter())
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    return session
