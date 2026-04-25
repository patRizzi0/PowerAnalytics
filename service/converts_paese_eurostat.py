from service.eurostat_service import EurostatService


CODICI_PAESE = {
    "belgio": "BE",
    "be": "BE",
    "lussemburgo": "LU",
    "lu": "LU",
}


def normalizza_codice_paese(paese):
    """Converte i nomi del form nei codici ISO richiesti da Eurostat."""
    paese_norm = paese.strip().lower()
    return CODICI_PAESE.get(paese_norm, paese.strip().upper())


def converts_paese_eurostat(paese, banda="KWH2500-4999"):
    """Restituisce prezzo kWh e metadati Eurostat per paese e fascia consumo."""
    codice_paese = normalizza_codice_paese(paese)
    data = EurostatService.prendi_dati_grezzi(codice_paese, banda)

    valori = data.get("value", {})
    if not valori:
        return {"errore": "Nessun dato disponibile"}

    time_labels = data.get("dimension", {}).get("time", {}).get("category", {}).get("label", {})

    ultimo_index = list(valori.keys())[-1]
    prezzo_kwh = valori[ultimo_index]
    if isinstance(prezzo_kwh, str):
        prezzo_kwh = float(prezzo_kwh.replace(",", "."))

    anno = time_labels.get(ultimo_index, "N/A")

    return {
        "paese": codice_paese,
        "prezzo_kwh": prezzo_kwh,
        "unita": "EUR/kWh",
        "fascia_consumo": banda,
        "tipo_prezzo": "Tasse incluse",
        "anno": anno,
        "fonte": "Eurostat",
    }
