from unittest.mock import patch

import pytest

from service.converts_paese_eurostat import (
    converts_paese_eurostat,
    normalizza_codice_paese,
)


class TestNormalizzaCodicePaese:
    """Test della normalizzazione del paese per Eurostat."""

    def test_nome_paese_italiano(self):
        """Con un nome italiano supportato, restituisce il codice ISO."""
        result = normalizza_codice_paese("Italia")

        assert result == "IT"

    def test_codice_paese_minuscolo(self):
        """Con un codice ISO minuscolo, restituisce il codice maiuscolo."""
        result = normalizza_codice_paese("fr")

        assert result == "FR"

    def test_paese_vuoto(self):
        """Con paese vuoto, solleva un errore gestibile."""
        with pytest.raises(RuntimeError, match="Paese non valido."):
            normalizza_codice_paese("")


class TestConvertsPaeseEurostat:
    """Test della conversione dei dati Eurostat in formato applicativo."""

    @patch("service.converts_paese_eurostat.EurostatService.prendi_dati_grezzi")
    def test_converte_risposta_eurostat_valida(self, mock_prendi_dati):
        """Con dati Eurostat validi, restituisce prezzo e storico normalizzati."""
        mock_prendi_dati.return_value = {
            "id": ["geo", "time"],
            "size": [1, 2],
            "dimension": {
                "time": {
                    "category": {
                        "index": {"2023": 0, "2024": 1},
                        "label": {"2023": "2023", "2024": "2024"},
                    }
                }
            },
            "value": {"0": "0,30", "1": 0.25},
        }

        result = converts_paese_eurostat("Italia", "KWH2500-4999")

        assert result == {
            "paese": "IT",
            "prezzo_kwh": 0.25,
            "unita": "EUR/kWh",
            "fascia_consumo": "KWH2500-4999",
            "tipo_prezzo": "Tasse incluse",
            "anno": "2024",
            "fonte": "Eurostat",
            "storico": {"2023": 0.30, "2024": 0.25},
        }
        mock_prendi_dati.assert_called_once_with("IT", "KWH2500-4999")

    @patch("service.converts_paese_eurostat.EurostatService.prendi_dati_grezzi")
    def test_dati_temporaneamente_non_disponibili(self, mock_prendi_dati):
        """Se Eurostat non risponde, restituisce un dizionario di errore."""
        mock_prendi_dati.return_value = None

        result = converts_paese_eurostat("IT")

        assert result == {"errore": "Dati Eurostat temporaneamente non disponibili"}

    @patch("service.converts_paese_eurostat.EurostatService.prendi_dati_grezzi")
    def test_risposta_senza_storico(self, mock_prendi_dati):
        """Se non ci sono osservazioni valide, restituisce un errore."""
        mock_prendi_dati.return_value = {"value": {}}

        result = converts_paese_eurostat("IT")

        assert result == {"errore": "Nessun dato disponibile"}
