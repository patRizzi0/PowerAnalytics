from unittest.mock import patch

import pytest

from service.consumi_service import calcola_consumo_abitazione, carica_coefficiente


class TestCalcolaConsumoAbitazione:
    """Test della funzione calcola_consumo_abitazione."""

    @patch("service.consumi_service.converts_paese_eurostat")
    def test_calcolo_consumo_abitazione(self, mock_converts):
        """Con input validi, calcola consumo e costo stimato."""
        mock_converts.return_value = {
            "prezzo_kwh": 0.25,
            "anno": 2024,
            "paese": "IT",
            "fonte": "https://eurostat.it",
            "storico": {},
        }

        result = calcola_consumo_abitazione(
            paese="IT",
            n_persone=3,
            m_quadri=100,
            stagione="inverno",
            tipo_abitazione="appart_medio",
        )

        assert "consumo_totale_kwh" in result
        assert "costo_stimato" in result
        assert result["prezzo_kwh"] == 0.25
        assert result["anno"] == 2024

    @patch("service.consumi_service.converts_paese_eurostat")
    def test_n_persone_invalido(self, _mock_eurostat):
        """Con persone non positive, solleva RuntimeError."""
        with pytest.raises(
            RuntimeError,
            match="Il numero di persone deve essere maggiore di zero.",
        ):
            calcola_consumo_abitazione(
                paese="IT",
                n_persone=0,
                m_quadri=100.0,
                stagione="inverno",
                tipo_abitazione="appartamento",
            )

    @patch("service.consumi_service.converts_paese_eurostat")
    def test_metri_quadri_invalido(self, _mock_eurostat):
        """Con superficie sotto soglia, solleva RuntimeError."""
        with pytest.raises(RuntimeError, match="metri quadri devono essere almeno"):
            calcola_consumo_abitazione(
                paese="IT",
                n_persone=3,
                m_quadri=15,
                stagione="inverno",
                tipo_abitazione="appartamento",
            )


class TestCaricaCoefficiente:
    """Test della funzione carica_coefficiente."""

    def test_carica_coefficiente_stagione(self):
        """Test caricamento coefficienti stagione."""
        result = carica_coefficiente("coeff_stagione.json")

        assert result["inverno"] == 1.2
        assert result["primavera"] == 1.0
        assert result["estate"] == 0.8
        assert result["autunno"] == 1.0

    def test_carica_coefficiente_appartamento(self):
        """Test caricamento coefficienti appartamento."""
        result = carica_coefficiente("coeff_appartamento.json")

        assert result["studio"] == 0.85
        assert result["appart_piccolo"] == 0.92
        assert result["appart_medio"] == 1.00
        assert result["casa_indipendente"] == 1.40

    def test_file_non_esistente(self):
        """Test con file coefficiente non esistente."""
        with pytest.raises(FileNotFoundError):
            carica_coefficiente("file_non_esistente.json")
