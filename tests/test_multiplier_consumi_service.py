from service.multiplier_consumi_service import multiplier_consumi


class TestMultiplierConsumi:
    """Test della funzione multiplier_consumi."""

    def test_una_persona(self):
        """Con 1 persona, restituisce moltiplicatore base."""
        result = multiplier_consumi(1)
        assert result == 1.00

    def test_due_persone(self):
        """Con 2 persone, restituisce moltiplicatore dedicato."""
        result = multiplier_consumi(2)
        assert result == 1.20

    def test_da_tre_a_quattro_persone(self):
        """Con 3 o 4 persone, restituisce lo stesso moltiplicatore."""
        assert multiplier_consumi(3) == 1.35
        assert multiplier_consumi(4) == 1.35

    def test_da_cinque_a_sei_persone(self):
        """Con 5 o 6 persone, restituisce lo stesso moltiplicatore."""
        assert multiplier_consumi(5) == 1.50
        assert multiplier_consumi(6) == 1.50

    def test_piu_di_sei_persone(self):
        """Con piu' di 6 persone, restituisce il moltiplicatore massimo."""
        result = multiplier_consumi(7)
        assert result == 1.65
