class Rule:
    def __init__(self, condizione, gruppo, descrizione, score):
        self.condizione = condizione
        self.gruppo = gruppo
        self.descrizione = descrizione
        self.score = score
    
    # Valuta la regola in base ai parametri forniti
    def evaluate(self, **kwargs):
        if self.condizione(**kwargs):
            return True, self.descrizione(**kwargs)
        return False, None
