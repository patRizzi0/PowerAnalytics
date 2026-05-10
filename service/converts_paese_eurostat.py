import math
import re
import unicodedata
from typing import Any, Dict, Optional, TypedDict, Union, cast

from service.eurostat_service import EurostatService
from service.countries import CODICI_PAESE


class ErroreEurostat(TypedDict):
    errore: str


class PrezzoEurostat(TypedDict):
    paese: str
    prezzo_kwh: float
    unita: str
    fascia_consumo: str
    tipo_prezzo: str
    anno: str
    fonte: str
    storico: Dict[str, float]


RisultatoEurostat = Union[PrezzoEurostat, ErroreEurostat]
JsonDict = Dict[str, Any]


def _normalizza_testo(valore: Any) -> str:
    """Normalizza input utente rendendo coerenti spazi, accenti e maiuscole."""
    testo = str(valore or "").strip().lower()
    testo = testo.replace("-", " ").replace("_", " ")
    testo = testo.replace("'", " ")
    testo = unicodedata.normalize("NFKD", testo)
    testo = "".join(char for char in testo if not unicodedata.combining(char))
    testo = re.sub(r"[^a-z0-9]+", " ", testo)
    return " ".join(testo.split())


def normalizza_codice_paese(paese: str) -> str:
    """Converte i nomi del form nei codici ISO richiesti da Eurostat."""
    paese_norm = _normalizza_testo(paese)
    if not paese_norm:
        raise RuntimeError("Paese non valido.")
    return CODICI_PAESE.get(paese_norm, paese_norm.upper())


def _to_float(valore: Any) -> Optional[float]:
    """Converte numeri Eurostat in float, gestendo stringhe con virgola."""
    if valore is None:
        return None
    if isinstance(valore, (int, float)):
        if isinstance(valore, float) and math.isnan(valore):
            return None
        return float(valore)
    try:
        return float(str(valore).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _indice_tempo_da_osservazione(
    indice_osservazione: int,
    data: JsonDict
) -> Optional[int]:
    """Ricava l'indice della dimensione time da un indice flat JSON-stat."""
    dimensioni = data.get("id", [])
    dimensioni_size = data.get("size", [])
    if "time" not in dimensioni or len(dimensioni_size) != len(dimensioni):
        return None

    posizione_tempo = dimensioni.index("time")
    passo = 1
    for size in dimensioni_size[posizione_tempo + 1:]:
        passo *= size

    return (indice_osservazione // passo) % dimensioni_size[posizione_tempo]


def _storico_da_eurostat(data: JsonDict) -> Dict[str, float]:
    """Costruisce uno storico {periodo: prezzo} dalla risposta JSON-stat."""
    valori = data.get("value", {})
    if not valori:
        return {}

    categoria_tempo = (
        data.get("dimension", {})
        .get("time", {})
        .get("category", {})
    )
    indici_tempo = categoria_tempo.get("index", {})
    label_tempo = categoria_tempo.get("label", {})
    tempo_per_indice = {indice: chiave for chiave, indice in indici_tempo.items()}

    storico: Dict[str, float] = {}
    for indice, valore in valori.items():
        try:
            indice_osservazione = int(indice)
        except (TypeError, ValueError):
            continue

        indice_tempo = _indice_tempo_da_osservazione(indice_osservazione, data)
        chiave_tempo = tempo_per_indice.get(indice_tempo)
        prezzo = _to_float(valore)
        if chiave_tempo and prezzo is not None:
            storico[label_tempo.get(chiave_tempo, chiave_tempo)] = prezzo

    return storico


def converts_paese_eurostat(
    paese: str,
    banda: str = "KWH2500-4999"
) -> RisultatoEurostat:
    """Restituisce prezzo kWh e metadati Eurostat per paese e fascia consumo.

    Args:
        paese: Nome o codice ISO del paese, per esempio "Italia" o "IT".
        banda: Fascia di consumo Eurostat.

    Raises:
        RuntimeError: Se il paese e' vuoto o non valido.

    Returns:
        Un dizionario con i dati normalizzati Eurostat oppure un dizionario
        {"errore": "..."} quando i dati non sono disponibili.
    """
    codice_paese = normalizza_codice_paese(paese)
    data = cast(Optional[JsonDict], EurostatService.prendi_dati_grezzi(codice_paese, banda))

    if data is None:
        return {"errore": "Dati Eurostat temporaneamente non disponibili"}

    storico = _storico_da_eurostat(data)
    if not storico:
        return {"errore": "Nessun dato disponibile"}

    anno = max(storico.keys())
    prezzo_kwh = storico[anno]

    return {
        "paese": codice_paese,
        "prezzo_kwh": prezzo_kwh,
        "unita": "EUR/kWh",
        "fascia_consumo": banda,
        "tipo_prezzo": "Tasse incluse",
        "anno": anno,
        "fonte": "Eurostat",
        "storico": storico
    }
