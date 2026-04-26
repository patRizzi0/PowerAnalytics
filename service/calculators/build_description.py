from service.calculators.key_precedent import _last_key, _latest_key
from service.calculators.variation_years import variations_years


def build_description(storico):
    if not storico:
        return "Nessun dato storico disponibile per generare una descrizione."

    ultima_chiave = _latest_key(storico)
    chiave_precedenza = _last_key(storico)

    if not ultima_chiave or chiave_precedenza not in storico:
        return "Dati storici insufficienti per generare una descrizione."

    variazione_percentuale = variations_years(storico)

    if variazione_percentuale is None:
        return (
            "Impossibile calcolare la variazione percentuale a causa di dati "
            "storici insufficienti o prezzo precedente pari a zero."
        )

    if variazione_percentuale > 0:
        return (
            f"Il prezzo del kWh e' aumentato del {variazione_percentuale}% "
            "rispetto all'anno precedente."
        )
    if variazione_percentuale < 0:
        return (
            f"Il prezzo del kWh e' diminuito del {abs(variazione_percentuale)}% "
            "rispetto all'anno precedente."
        )
    return "Il prezzo del kWh e' rimasto stabile rispetto all'anno precedente."
