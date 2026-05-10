from typing import Any, Callable


class Rule:
    """Rappresenta una regola di insight valutabile sui dati disponibili."""

    def __init__(
        self,
        condizione: Callable[..., bool],
        gruppo: str,
        descrizione: Callable[..., str],
        score: int,
    ) -> None:
        """Inizializza condizione, gruppo, descrizione e punteggio della regola."""
        self.condizione = condizione
        self.gruppo = gruppo
        self.descrizione = descrizione
        self.score = score

    def evaluate(self, **kwargs: Any) -> tuple[bool, str | None]:
        """Valuta la regola con i dati disponibili e restituisce l'eventuale testo."""
        try:
            if self.condizione(**kwargs):
                return True, self.descrizione(**kwargs)
        except (KeyError, TypeError, ValueError):
            return False, None

        return False, None
