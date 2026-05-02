import requests


def prezzi_francia(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    labels = data["dimension"]["time"]["category"]["label"]
    indici = data["dimension"]["time"]["category"]["index"]
    valori = data["value"]

    prezzi = {}

    for time_key, posizione in indici.items():
        label = labels.get(time_key, time_key)
        valore = valori.get(str(posizione))

        prezzi[label] = valore if valore is not None else None

    return prezzi