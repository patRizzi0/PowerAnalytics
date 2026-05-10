def multiplier_consumi(n_persone: int) -> float:
    """Restituisce il moltiplicatore dei consumi in base al nucleo familiare.

    Args:
        n_persone: Numero di persone che vivono nell'abitazione.

    Returns:
        Moltiplicatore dei consumi da applicare al consumo base.
    """
    if n_persone == 1:
        return 1.00
    if n_persone == 2:
        return 1.20
    if n_persone <= 4:
        return 1.35
    if n_persone <= 6:
        return 1.50
    return 1.65
