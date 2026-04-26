def _periodo_sort_key(periodo):
    """Restituisce una chiave ordinabile per periodi Eurostat tipo 2025-S2."""
    testo = str(periodo)
    try:
        anno = int(testo[:4])
    except (TypeError, ValueError):
        return -1, 0
    semestre = 0
    if "-S" in testo:
        try:
            semestre = int(testo.split("-S", 1)[1])
        except ValueError:
            semestre = 0
    return anno, semestre


def _latest_key(storico):
    """Restituisce la chiave temporale piu' recente presente nello storico."""
    if not storico:
        return None
    return max(storico.keys(), key=_periodo_sort_key)


def _last_key(storico):
    """Restituisce la chiave dello stesso periodo nell'anno precedente."""
    ultima = _latest_key(storico)
    if ultima is None:
        return None

    ultima = str(ultima)
    try:
        last_year = str(int(ultima[:4]) - 1)
    except ValueError:
        return None
    return last_year + ultima[4:]
