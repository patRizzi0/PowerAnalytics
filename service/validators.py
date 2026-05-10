def check_input(n_persone: int, m_quadri: int) -> str | None:
    """Valida i parametri del form consumi.

    Args:
        n_persone: Numero di persone, deve essere maggiore di zero.
        m_quadri: Metri quadri, devono essere almeno 20.

    Returns:
        Messaggio d'errore se l'input non e' valido, altrimenti None.
    """
    if n_persone <= 0:
        return "Il numero di persone deve essere maggiore di zero."

    if m_quadri < 20:
        return "I metri quadri devono essere almeno 20."

    return None
