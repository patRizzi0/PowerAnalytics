class Rule:
    def __init__(self, condizione, gruppo, descrizione, score):
        self.condizione = condizione
        self.gruppo = gruppo
        self.descrizione = descrizione
        self.score = score

    def evaluate(self, **kwargs):
        """Valuta la regola con i dati disponibili e restituisce l'eventuale testo."""
        try:
            if self.condizione(**kwargs):
                return True, self.descrizione(**kwargs)
        except (KeyError, TypeError, ValueError):
            return False, None

        return False, None
