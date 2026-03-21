def converts_json_eurostat(data):
    geo_category = data["dimension"]["geo"]["category"]
    geo_index = geo_category["index"]      # es: {"BE": 4, "IT": 15, ...}
    geo_labels = geo_category["label"]     # es: {"BE": "Belgium", ...}

    values = data["value"]                 # es: {"0": 123, "1": 456, ...}

    dati_filtrati = []

    for codice, posizione in geo_index.items():
        if len(codice) == 2:  # tiene solo i paesi veri
            valore = values.get(str(posizione))  # attenzione: le chiavi di value sono stringhe

            dati_filtrati.append({
                "codice": codice,
                "nome_paese": geo_labels[codice],
                "dato": valore
            })

    return dati_filtrati