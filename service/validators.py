def check_input(n_persone, m_quadri):
    """Valida i valori numerici del form consumi e restituisce un messaggio d'errore."""
    if n_persone <= 0:
        return "Il numero di persone deve essere maggiore di zero."

    if m_quadri < 20:
        return "I metri quadri devono essere almeno 20."

    return None
