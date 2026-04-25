from models.country_model import Country
import requests





class EurostatService:
    BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204"

    @classmethod
    def prendi_dati_grezzi(cls, codice_paese, banda="KWH2500-4999"):
        parametri = {
            "geo": codice_paese,   # es: "BE"
            "unit": "KWH",
            "nrg_cons": banda,
            "tax": "I_TAX",
            "currency": "EUR"
        }

        try:
            response = requests.get(cls.BASE_URL, params=parametri, timeout=10)

            # Se Eurostat risponde con un errore (es. 404), questo solleva un'eccezione
            response.raise_for_status()

            # Restituiamo il JSON "grezzo"
            return response.json()

        except Exception as e:
            raise RuntimeError(f"Errore Eurostat: {e}")


country_data = {
    "BE": Country("BE", "Belgio", "Belgium"),
    "LU": Country("LU", "Lussemburgo", "Luxembourg"),
    "IT": Country("IT", "Italia", "Italy"),
    "ES": Country("ES", "Spagna", "Spain"),
    "DE": Country("DE", "Germania", "Germany"),
    "NL": Country("NL", "Paesi Bassi", "Netherlands")
}


def get_country_by_code(iso_code):
    paese = country_data.get(iso_code.upper())
    if not paese:
        return None
    return {
        "iso_code": paese.iso_code,
        "name_it": paese.name_it,
        "name_en": paese.name_en
    }

