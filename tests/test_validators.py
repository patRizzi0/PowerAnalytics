import pytest
from service.validators import check_input


class TestCheckInput:
    """Test della funzione check_input."""

    def test_input_valido(self):
        """Con input validi, deve restituire None."""
        result = check_input(n_persone=2, m_quadri=50)
        assert result is None

    def test_n_persone_zero(self):
        """Con n_persone = 0, deve restituire messaggio d'errore."""
        result = check_input(n_persone=0, m_quadri=50)
        assert result == "Il numero di persone deve essere maggiore di zero."

    def test_n_persone_negativo(self):
        """Con n_persone negativo, deve restituire messaggio d'errore."""
        result = check_input(n_persone=-5, m_quadri=50)
        assert result == "Il numero di persone deve essere maggiore di zero."

    def test_m_quadri_sotto_soglia(self):
        """Con m_quadri < 20, deve restituire messaggio d'errore."""
        result = check_input(n_persone=2, m_quadri=19)
        assert result == "I metri quadri devono essere almeno 20."

    def test_m_quadri_esattamente_20(self):
        """Con m_quadri = 20 (limite inferiore), deve essere valido."""
        result = check_input(n_persone=2, m_quadri=20)
        assert result is None

    def test_n_persone_invalido_prioritario(self):
        """Se n_persone è invalido, l'errore su n_persone ha priorità."""
        result = check_input(n_persone=0, m_quadri=15)
        assert result == "Il numero di persone deve essere maggiore di zero."
