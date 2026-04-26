from service.calculators.key_precedent import _last_key, _latest_key


def _to_float(valore):
    if valore is None:
        return None
    try:
        return float(str(valore).replace(",", "."))
    except (TypeError, ValueError):
        return None


def variations_years(storico):
    if not storico:
        return None

    last_year_key = _latest_key(storico)
    previous_key = _last_key(storico)
    if not last_year_key or previous_key not in storico:
        return None

    current_price = _to_float(storico.get(last_year_key))
    previous_price = _to_float(storico.get(previous_key))
    if current_price is None or previous_price in (None, 0):
        return None

    variazione_percentuale = ((current_price - previous_price) / previous_price) * 100
    return round(variazione_percentuale, 2)
