import json
from service.converts_paese_eurostat import converts_paese_eurostat

with open("data/abitazioni.json", encoding="utf-8") as f:
    abitazioni = json.load(f)


def media_mq(tipo):
    dati = abitazioni[tipo]
    return (dati["min_mq"] + dati["max_mq"]) / 2


def extra_consumo_persone(n_persone):
    tabella = {
        1: 250,
        2: 450,
        3: 650,
        4: 850,
        5: 1050
    }
    return tabella.get(n_persone, 1050 + max(0, n_persone - 5) * 150)


def calcola_consumo_abitazione(paese, n_persone, m_quadri, stagione, tipo_abitazione):
    dati_prezzo = converts_paese_eurostat(paese)

    if "errore" in dati_prezzo:
        return dati_prezzo

    prezzo_kwh = dati_prezzo["prezzo_kwh"]

    coeff_stagione = {
        "primavera": 1.00,
        "estate": 0.95,
        "autunno": 1.08,
        "inverno": 1.20
    }

    coeff_tipo = {
        "studio": 0.85,
        "appart_piccolo": 0.92,
        "appart_medio": 1.00,
        "appart_grande": 1.10,
        "colocation": 1.08,
        "casa_schiera": 1.18,
        "casa_semindipendente": 1.28,
        "casa_indipendente": 1.40
    }

    coeff_mq = 24

    consumo_superficie = m_quadri * coeff_mq
    consumo_persone = extra_consumo_persone(n_persone)

    consumo_totale = (
        consumo_superficie * coeff_tipo[tipo_abitazione] * coeff_stagione[stagione]
    ) + consumo_persone

    costo_stimato = consumo_totale * prezzo_kwh

    return {
    "consumo_totale_kwh": round(consumo_totale, 2),
    "prezzo_kwh": round(prezzo_kwh, 4),
    "costo_stimato": round(costo_stimato, 2),
    "anno": dati_prezzo["anno"],
    "paese": dati_prezzo["paese"],
    "fonte": dati_prezzo["fonte"]
}