import json
import os

from service.converts_paese_eurostat import converts_paese_eurostat
from service.multiplier_consumi_service import multiplier_consumi


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COEFF_MQ = 24


def carica_coefficiente(nome_file: str) -> dict:
    """Carica i coefficienti da un file JSON nella cartella data."""
    path = os.path.join(BASE_DIR, "..", "data", nome_file)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


coeff_stagione = carica_coefficiente("coeff_stagione.json")
coeff_tipo = carica_coefficiente("coeff_appartamento.json")


def calcola_consumo_abitazione(
    paese: str,
    n_persone: int,
    m_quadri: int,
    stagione: str,
    tipo_abitazione: str
) -> dict:
    """Stima consumo annuo e costo energetico di un'abitazione.

    Il calcolo combina superficie, numero di persone, stagione, tipo di
    abitazione e prezzo kWh recuperato da Eurostat per il paese indicato.

    Args:
        paese: Nome o codice del paese da usare per il prezzo Eurostat.
        n_persone: Numero di persone che vivono nell'abitazione.
        m_quadri: Superficie dell'abitazione in metri quadrati.
        stagione: Stagione della simulazione. Valori ammessi: "estate",
            "inverno", "primavera", "autunno".
        tipo_abitazione: Chiave del tipo abitazione presente in
            coeff_appartamento.json.

    Raises:
        RuntimeError: Se i valori numerici non sono validi, se il paese non
            ha dati disponibili, se stagione o tipo abitazione non sono
            supportati, o se il prezzo kWh non e' utilizzabile.

    Returns:
        Dizionario con consumo totale in kWh, prezzo kWh, costo stimato,
        anno, paese, fonte e storico dei prezzi.
    """
    try:
        n_persone = int(n_persone)
        m_quadri = float(m_quadri)
    except (TypeError, ValueError):
        raise RuntimeError("Persone e metri quadri devono essere valori numerici.")

    if n_persone <= 0:
        raise RuntimeError("Il numero di persone deve essere maggiore di zero.")

    if m_quadri < 20:
        raise RuntimeError("I metri quadri devono essere almeno 20.")

    dati_prezzo = converts_paese_eurostat(paese)

    if "errore" in dati_prezzo:
        raise RuntimeError(dati_prezzo["errore"])

    if tipo_abitazione not in coeff_tipo:
        raise RuntimeError("Tipo di abitazione non valido.")

    if stagione not in coeff_stagione:
        raise RuntimeError("Stagione non valida.")

    try:
        prezzo_kwh = float(dati_prezzo["prezzo_kwh"])
    except (KeyError, TypeError, ValueError):
        raise RuntimeError("Prezzo kWh non valido.")

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
        "storico": dati_prezzo["storico"]
    }
