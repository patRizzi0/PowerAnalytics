SUPPORTED_COUNTRIES = {
    "BE": {"it": "Belgio", "en": "Belgium"},
    "BG": {"it": "Bulgaria", "en": "Bulgaria"},
    "CZ": {"it": "Repubblica Ceca", "en": "Czech Republic"},
    "DK": {"it": "Danimarca", "en": "Denmark"},
    "DE": {"it": "Germania", "en": "Germany"},
    "EE": {"it": "Estonia", "en": "Estonia"},
    "IE": {"it": "Irlanda", "en": "Ireland"},
    "GR": {"it": "Grecia", "en": "Greece"},
    "ES": {"it": "Spagna", "en": "Spain"},
    "FR": {"it": "Francia", "en": "France"},
    "HR": {"it": "Croazia", "en": "Croatia"},
    "IT": {"it": "Italia", "en": "Italy"},
    "CY": {"it": "Cipro", "en": "Cyprus"},
    "LV": {"it": "Lettonia", "en": "Latvia"},
    "LT": {"it": "Lituania", "en": "Lithuania"},
    "LU": {"it": "Lussemburgo", "en": "Luxembourg"},
    "HU": {"it": "Ungheria", "en": "Hungary"},
    "MT": {"it": "Malta", "en": "Malta"},
    "NL": {"it": "Paesi Bassi", "en": "Netherlands"},
    "AT": {"it": "Austria", "en": "Austria"},
    "PL": {"it": "Polonia", "en": "Poland"},
    "PT": {"it": "Portogallo", "en": "Portugal"},
    "RO": {"it": "Romania", "en": "Romania"},
    "SI": {"it": "Slovenia", "en": "Slovenia"},
    "SK": {"it": "Slovacchia", "en": "Slovakia"},
    "FI": {"it": "Finlandia", "en": "Finland"},
    "SE": {"it": "Svezia", "en": "Sweden"},
    "NO": {"it": "Norvegia", "en": "Norway"},
}

CODICI_PAESE = {}

for code, names in SUPPORTED_COUNTRIES.items():
    CODICI_PAESE[names["it"].lower()] = code
    CODICI_PAESE[names["en"].lower()] = code
    CODICI_PAESE[code.lower()] = code
