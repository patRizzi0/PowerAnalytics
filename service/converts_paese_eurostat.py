import math
import re
import unicodedata

from service.eurostat_service import EurostatService


CODICI_PAESE = {
    "belgio": "BE",
    "be": "BE",
    "belgium": "BE",
    "lussemburgo": "LU",
    "lu": "LU",
    "luxembourg": "LU",
    "italia": "IT",
    "repubblica italiana": "IT",
    "italy": "IT",
    "it": "IT",
    "ita": "IT",
    "spagna": "ES",
    "regno di spagna": "ES",
    "spain": "ES",
    "es": "ES",
    "esp": "ES",
    "germania": "DE",
    "repubblica federale tedesca": "DE",
    "repubblica federale di germania": "DE",
    "rft": "DE",
    "germany": "DE",
    "deutschland": "DE",
    "de": "DE",
    "deu": "DE",
    "ger": "DE",
    "paesi bassi": "NL",
    "paesibassi": "NL",
    "olanda": "NL",
    "regno dei paesi bassi": "NL",
    "regno d olanda": "NL",
    "netherlands": "NL",
    "nederland": "NL",
    "holland": "NL",
    "nl": "NL",
    "nld": "NL",
}


def _normalizza_testo(valore):
    """Normalizza input utente rendendo coerenti spazi, accenti e maiuscole."""
    testo = str(valore or "").strip().lower()
    testo = testo.replace("-", " ").replace("_", " ")
    testo = testo.replace("'", " ")
    testo = unicodedata.normalize("NFKD", testo)
    testo = "".join(char for char in testo if not unicodedata.combining(char))
    testo = re.sub(r"[^a-z0-9]+", " ", testo)
    return " ".join(testo.split())


def normalizza_codice_paese(paese):
    """Converte i nomi del form nei codici ISO richiesti da Eurostat."""
    paese_norm = _normalizza_testo(paese)
    if not paese_norm:
        raise RuntimeError("Paese non valido.")
    return CODICI_PAESE.get(paese_norm, paese_norm.upper())


def _to_float(valore):
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


def _indice_tempo_da_osservazione(indice_osservazione, data):
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


def _storico_da_eurostat(data):
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

    storico = {}
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


def converts_paese_eurostat(paese, banda="KWH2500-4999"):
    """Restituisce prezzo kWh e metadati Eurostat per paese e fascia consumo."""
    codice_paese = normalizza_codice_paese(paese)
    data = EurostatService.prendi_dati_grezzi(codice_paese, banda)

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
