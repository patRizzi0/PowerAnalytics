def multiplier_consumi(n_persone):
    """Restituisce il moltiplicatore dei consumi in base alla dimensione del nucleo."""
    if n_persone == 1:
        return 1.00
    if n_persone == 2:
        return 1.20
    if n_persone <= 4:
        return 1.35
    if n_persone <= 6:
        return 1.50
    return 1.65
