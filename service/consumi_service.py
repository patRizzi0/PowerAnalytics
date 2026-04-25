import json
import os

from service.converts_paese_eurostat import converts_paese_eurostat
from service.multiplier_consumi_service import multiplier_consumi


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COEFF_MQ = 24


def carica_coefficiente(nome_file):
    """Carica un file JSON dalla cartella data e restituisce i coefficienti."""
    path = os.path.join(BASE_DIR, "..", "data", nome_file)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


coeff_stagione = carica_coefficiente("coeff_stagione.json")
coeff_tipo = carica_coefficiente("coeff_appartamento.json")


def calcola_consumo_abitazione(paese, n_persone, m_quadri, stagione, tipo_abitazione):
    """Calcola consumo annuo e costo stimato partendo dai dati del form."""
    dati_prezzo = converts_paese_eurostat(paese)
    if "errore" in dati_prezzo:
        raise RuntimeError(dati_prezzo["errore"])

    if tipo_abitazione not in coeff_tipo:
        raise RuntimeError("Tipo di abitazione non valido.")

    if stagione not in coeff_stagione:
        raise RuntimeError("Stagione non valida.")

    prezzo_kwh = dati_prezzo["prezzo_kwh"]
    consumo_superficie = m_quadri * COEFF_MQ
    consumo_persone = multiplier_consumi(n_persone)

    consumo_totale = (
        consumo_superficie
        * coeff_tipo[tipo_abitazione]
        * coeff_stagione[stagione]
        * consumo_persone
    )
    costo_stimato = consumo_totale * prezzo_kwh

    return {
        "consumo_totale_kwh": round(consumo_totale, 2),
        "prezzo_kwh": round(prezzo_kwh, 4),
        "costo_stimato": round(costo_stimato, 2),
        "anno": dati_prezzo["anno"],
        "paese": dati_prezzo["paese"],
        "fonte": dati_prezzo["fonte"],
    }
