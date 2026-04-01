def genera_insight_lussemburgo(consumo, costo, prezzo_kwh, n_persone=None, m_quadri=None, stagione=None):
    insights_generali = []
    insights_personali = []

    # --- GENERALI ---
    insights_generali.append({
        "categoria": "generale",
        "titolo": "Aumento significativo dei prezzi",
        "testo": "Nel 2025 il Lussemburgo ha registrato uno degli aumenti più elevati dei prezzi dell’elettricità in Europa, con una crescita di circa il 31.3% rispetto all’anno precedente.",
        "score": 90
    })

    insights_generali.append({
        "categoria": "generale",
        "titolo": "Confronto con la media UE",
        "testo": "Nonostante l’aumento recente, il prezzo dell’elettricità in Lussemburgo resta generalmente vicino o inferiore alla media UE, pari a circa 0.2872 €/kWh.",
        "score": 80
    })

    insights_generali.append({
        "categoria": "generale",
        "titolo": "Peso di tasse e oneri",
        "testo": "Nell’Unione Europea, tasse e oneri rappresentano in media circa il 27.6% del prezzo finale dell’elettricità domestica.",
        "score": 70
    })

    insights_generali.append({
        "categoria": "generale",
        "titolo": "Contesto energetico",
        "testo": "Tra i paesi con il maggiore aumento annuale dei prezzi nel 2025, segnale di un mercato energetico in forte evoluzione.",
        "score": 75
    })

    # --- PERSONALI (riutilizzi logica base) ---
    # consumo vs media
    media_consumo = 3500

    if consumo > media_consumo:
        insights_personali.append({
            "categoria": "personale",
            "titolo": "Consumo sopra la media",
            "testo": f"Il tuo consumo stimato supera la media europea di circa {consumo - media_consumo:.0f} kWh.",
            "score": 95
        })
    else:
        insights_personali.append({
            "categoria": "personale",
            "titolo": "Consumo nella norma",
            "testo": "Il tuo consumo rientra in una fascia tipica per abitazioni simili in Europa.",
            "score": 85
        })

        # costo
    if costo >= 1200:
        insights_personali.append({
            "categoria": "personale",
            "titolo": "Spesa elevata",
            "testo": f"La tua spesa stimata di circa {costo:.2f} € annui è piuttosto alta e potrebbe essere influenzata dall’aumento recente dei prezzi.",
            "score": 90
        })

    # prezzo alto → impatto forte
    if prezzo_kwh >= 0.30:
        insights_personali.append({
            "categoria": "personale",
            "titolo": "Prezzo energetico sensibile",
            "testo": "Anche piccoli aumenti di consumo possono incidere molto sulla bolletta, dato il livello attuale dei prezzi.",
            "score": 88
        })

    # stagione estate
    if stagione == "estate":
        insights_personali.append({
            "categoria": "personale",
            "titolo": "Impatto climatizzazione",
            "testo": "L’uso del climatizzatore durante i mesi estivi può aumentare sensibilmente i consumi mensili rispetto a un ventilatore.",
            "score": 85
        })

    # inverno
    if stagione == "inverno":
        insights_personali.append({
            "categoria": "personale",
            "titolo": "Consumi invernali",
            "testo": "Durante l’inverno, il fabbisogno energetico aumenta per riscaldamento e illuminazione.",
            "score": 85
        })

    return {
        "generali": sorted(insights_generali, key=lambda x: x["score"], reverse=True)[:3],
        "personali": sorted(insights_personali, key=lambda x: x["score"], reverse=True)[:4]
            }