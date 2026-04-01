import requests

def converts_paese_eurostat(paese, banda="KWH2500-4999"):
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204"

    country_codes = {
        "belgio": "BE",
        "belgium": "BE",
        "be": "BE",

        "lussemburgo": "LU",
        "luxembourg": "LU",
        "lu": "LU",

        "italia": "IT",
        "italy": "IT",
        "it": "IT",

        "spagna": "ES",
        "spain": "ES",
        "es": "ES",

        "germania": "DE",
        "germany": "DE",
        "de": "DE",

        "paesi bassi": "NL",
        "paesi_bassi": "NL",
        "netherlands": "NL",
        "nl": "NL"
    }

    country_names = {
        "BE": "Belgium",
        "LU": "Luxembourg",
        "IT": "Italy",
        "ES": "Spain",
        "DE": "Germany",
        "NL": "Netherlands"
    }

    paese_norm = paese.strip().lower()
    geo = country_codes.get(paese_norm)

    if not geo:
        return {"errore": f"Paese non supportato: {paese}"}

    params = {
        "geo": geo,
        "unit": "KWH",
        "nrg_cons": banda,
        "tax": "I_TAX",
        "currency": "EUR"
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"errore": f"Errore API: {e}"}

    valori = data.get("value", {})
    if not valori:
        return {"errore": "Nessun dato disponibile"}

    time_labels = data.get("dimension", {}).get("time", {}).get("category", {}).get("label", {})

    ultimo_index = list(valori.keys())[-1]
    prezzo_kwh = valori[ultimo_index]
    if isinstance(prezzo_kwh, str):
        prezzo_kwh = prezzo_kwh.replace(",", ".")
        prezzo_kwh = float(prezzo_kwh)
    anno = time_labels.get(ultimo_index, "N/A")

    return {
    "codice": geo,
    "paese": country_names.get(geo, geo),
    "prezzo_kwh": prezzo_kwh,
    "unita": "€/kWh",
    "fascia_consumo": banda,
    "tipo_prezzo": "Tasse incluse",
    "anno": anno,
    "fonte": "Eurostat"
}