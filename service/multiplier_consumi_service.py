COEFF_PERSONE = {
    1: 1.00,
    2: 1.20,
    5: 1.35,
    8: 1.50,
}


def multiplier_consumi(n_persone):
    """Restituisce il moltiplicatore dei consumi in base alla dimensione del nucleo."""
    return COEFF_PERSONE.get(n_persone, 1.00)
