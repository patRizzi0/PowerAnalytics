import copy
import logging
import os
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models.country_model import Country


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    data: dict
    expires_at: float
    stale_until: float


class EurostatService:
    BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204"
    CACHE_TTL_SECONDS = int(os.getenv("EUROSTAT_CACHE_TTL_SECONDS", "21600"))
    STALE_TTL_SECONDS = int(os.getenv("EUROSTAT_STALE_TTL_SECONDS", "86400"))
    CACHE_MAX_ITEMS = int(os.getenv("EUROSTAT_CACHE_MAX_ITEMS", "128"))
    REQUEST_TIMEOUT_SECONDS = float(os.getenv("EUROSTAT_TIMEOUT_SECONDS", "10"))
    RETRY_TOTAL = int(os.getenv("EUROSTAT_RETRY_TOTAL", "3"))
    RETRY_BACKOFF_FACTOR = float(os.getenv("EUROSTAT_RETRY_BACKOFF_FACTOR", "0.4"))
    RETRY_STATUS_CODES = (429, 500, 502, 503, 504)

    _cache = OrderedDict()
    _lock = threading.RLock()
    _inflight = {}
    _session = None

    @classmethod
    def prendi_dati_grezzi(cls, codice_paese, banda="KWH2500-4999"):
        """Restituisce i dati Eurostat usando cache TTL thread-safe."""
        chiave_cache = cls._cache_key(codice_paese, banda)
        dati_cache = cls._get_from_cache(chiave_cache)
        if dati_cache is not None:
            return dati_cache

        should_fetch = cls._register_inflight_request(chiave_cache)
        if not should_fetch:
            return cls._wait_for_inflight_request(chiave_cache)

        try:
            data = cls._fetch_from_eurostat(codice_paese, banda)
            cls._save_in_cache(chiave_cache, data)
            return copy.deepcopy(data)
        except requests.RequestException as e:
            logger.warning("Errore durante la richiesta a Eurostat: %s", e)
            return cls._get_from_cache(chiave_cache, allow_stale=True)
        except ValueError as e:
            logger.warning("Risposta Eurostat non valida: %s", e)
            return cls._get_from_cache(chiave_cache, allow_stale=True)
        finally:
            if should_fetch:
                cls._release_inflight_request(chiave_cache)

    @classmethod
    def svuota_cache(cls):
        """Svuota la cache in memoria, utile per debug o test controllati."""
        with cls._lock:
            cls._cache.clear()

    @classmethod
    def cache_info(cls):
        """Restituisce metriche leggere sullo stato della cache."""
        with cls._lock:
            now = time.monotonic()
            fresh_items = sum(1 for entry in cls._cache.values() if entry.expires_at > now)
            return {
                "items": len(cls._cache),
                "fresh_items": fresh_items,
                "max_items": cls.CACHE_MAX_ITEMS,
                "ttl_seconds": cls.CACHE_TTL_SECONDS,
                "stale_ttl_seconds": cls.STALE_TTL_SECONDS
            }

    @classmethod
    def _cache_key(cls, codice_paese, banda):
        paese = str(codice_paese or "").strip().upper()
        fascia = str(banda or "").strip().upper()
        return paese, fascia

    @classmethod
    def _get_from_cache(cls, chiave_cache, allow_stale=False):
        with cls._lock:
            entry = cls._cache.get(chiave_cache)
            if entry is None:
                return None

            now = time.monotonic()
            if entry.expires_at > now or (allow_stale and entry.stale_until > now):
                cls._cache.move_to_end(chiave_cache)
                return copy.deepcopy(entry.data)

            if entry.stale_until <= now:
                cls._cache.pop(chiave_cache, None)

            return None

    @classmethod
    def _save_in_cache(cls, chiave_cache, data):
        now = time.monotonic()
        entry = CacheEntry(
            data=copy.deepcopy(data),
            expires_at=now + cls.CACHE_TTL_SECONDS,
            stale_until=now + cls.CACHE_TTL_SECONDS + cls.STALE_TTL_SECONDS
        )

        with cls._lock:
            cls._cache[chiave_cache] = entry
            cls._cache.move_to_end(chiave_cache)

            while len(cls._cache) > cls.CACHE_MAX_ITEMS:
                cls._cache.popitem(last=False)

    @classmethod
    def _register_inflight_request(cls, chiave_cache):
        with cls._lock:
            if chiave_cache in cls._inflight:
                return False

            cls._inflight[chiave_cache] = threading.Event()
            return True

    @classmethod
    def _wait_for_inflight_request(cls, chiave_cache):
        with cls._lock:
            event = cls._inflight.get(chiave_cache)

        if event is None:
            return cls._get_from_cache(chiave_cache)

        event.wait(timeout=cls.REQUEST_TIMEOUT_SECONDS + 2)
        return cls._get_from_cache(chiave_cache, allow_stale=True)

    @classmethod
    def _release_inflight_request(cls, chiave_cache):
        with cls._lock:
            event = cls._inflight.pop(chiave_cache, None)

        if event is not None:
            event.set()

    @classmethod
    def _fetch_from_eurostat(cls, codice_paese, banda):
        parametri = {
            "geo": str(codice_paese or "").strip().upper(),
            "unit": "KWH",
            "nrg_cons": str(banda or "").strip().upper(),
            "tax": "I_TAX",
            "currency": "EUR"
        }

        response = cls._get_session().get(
            cls.BASE_URL,
            params=parametri,
            timeout=cls.REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def _get_session(cls):
        with cls._lock:
            if cls._session is None:
                cls._session = cls._build_session()
            return cls._session

    @staticmethod
    def _build_session():
        retry_strategy = EurostatService._build_retry_strategy()
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,
            pool_maxsize=50
        )
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @classmethod
    def _build_retry_strategy(cls):
        retry_strategy = Retry(
            total=cls.RETRY_TOTAL,
            connect=cls.RETRY_TOTAL,
            read=cls.RETRY_TOTAL,
            status=cls.RETRY_TOTAL,
            backoff_factor=cls.RETRY_BACKOFF_FACTOR,
            status_forcelist=cls.RETRY_STATUS_CODES,
            allowed_methods=("GET",),
            respect_retry_after_header=True,
            raise_on_status=False
        )
        return retry_strategy


country_data = {
    "BE": Country("BE", "Belgio", "Belgium"),
    "LU": Country("LU", "Lussemburgo", "Luxembourg"),
    "IT": Country("IT", "Italia", "Italy"),
    "ES": Country("ES", "Spagna", "Spain"),
    "DE": Country("DE", "Germania", "Germany"),
    "NL": Country("NL", "Paesi Bassi", "Netherlands")
}


def get_country_by_code(iso_code):
    paese = country_data.get(iso_code.upper())
    if not paese:
        return None
    return {
        "iso_code": paese.iso_code,
        "name_it": paese.name_it,
        "name_en": paese.name_en
    }
