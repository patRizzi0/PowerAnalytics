import os
import json


def carica_dati_contesto():
    path = os.path.join("data", "energia.json")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


DATI_CONTESTO = carica_dati_contesto()


def genera_insight_generali_belgio():
    insights = []
    dati = DATI_CONTESTO.get("belgio")

    if not dati:
        return []

    prezzo_kwh = dati.get("prezzo_kwh")
    media_ue = dati.get("media_ue_prezzo_kwh")
    rank_alto = dati.get("rank_alto")
    descrizione_rank = dati.get("descrizione_rank")
    variazione_annua = dati.get("variazione_annua_percento")
    share_tasse_ue = dati.get("share_tasse_ue")
    note = dati.get("note")

    if prezzo_kwh is not None:
        insights.append({
            "categoria": "generale",
            "titolo": "Prezzo medio dell’energia",
            "testo": f"Per i consumatori domestici di fascia media, il prezzo dell’elettricità in Belgio è di circa {prezzo_kwh:.4f} €/kWh nel primo semestre 2025.",
            "score": 80
        })

    if prezzo_kwh is not None and media_ue is not None:
        diff_percent = ((prezzo_kwh - media_ue) / media_ue) * 100

    if diff_percent > 0:
        testo_confronto = f"Il prezzo in Belgio è superiore di circa {diff_percent:.1f}% rispetto alla media UE di {media_ue:.4f} €/kWh."
    else:
        testo_confronto = f"Il prezzo in Belgio è inferiore di circa {abs(diff_percent):.1f}% rispetto alla media UE di {media_ue:.4f} €/kWh."

        insights.append({
            "categoria": "generale",
            "titolo": "Confronto con la media UE",
            "testo": testo_confronto,
            "score": 88
        })

    if rank_alto and descrizione_rank:
        insights.append({
            "categoria": "generale",
            "titolo": "Paese ad alto costo energetico",
            "testo": f"Il Belgio risulta {descrizione_rank} per l’elettricità domestica nel primo semestre 2025.",
            "score": 85
        })

    if variazione_annua is not None:
        insights.append({
            "categoria": "generale",
            "titolo": "Variazione annuale rilevante",
            "testo": f"Nel primo semestre 2025, i prezzi dell’elettricità per famiglie in Belgio sono aumentati di circa {variazione_annua:.1f}% rispetto allo stesso periodo del 2024.",
            "score": 84
        })

    if share_tasse_ue is not None:
        insights.append({
            "categoria": "generale",
            "titolo": "Peso di tasse e oneri",
            "testo": f"Nell’UE, tasse e oneri rappresentano in media circa il {share_tasse_ue:.1f}% del prezzo finale dell’elettricità domestica.",
            "score": 70
        })

    if note:
        insights.append({
            "categoria": "generale",
            "titolo": "Contesto normativo",
            "testo": note,
            "score": 60
        })

    return insights


def genera_insight_personali_belgio(
    consumo,
    costo,
    prezzo_kwh,
    media_consumo=3500,
    n_persone=None,
    m_quadri=None,
    stagione=None
):
    insights = []

    # Consumo vs media
    if consumo > media_consumo:
        diff = consumo - media_consumo
        insights.append({
            "categoria": "personale",
            "titolo": "Sopra la media",
            "testo": f"Il tuo consumo stimato supera di circa {diff:.0f} kWh la media di riferimento.",
            "score": 95
        })
    else:
        diff = media_consumo - consumo
        insights.append({
            "categoria": "personale",
            "titolo": "Consumo efficiente",
            "testo": f"Il tuo consumo stimato è inferiore di circa {diff:.0f} kWh rispetto alla media di riferimento.",
            "score": 92
        })

    # Costo annuale
    if costo >= 1200:
        insights.append({
            "categoria": "personale",
            "titolo": "Spesa annuale elevata",
            "testo": f"La tua spesa stimata è di circa {costo:.2f} € all’anno, un livello piuttosto alto.",
            "score": 93
        })
    elif costo <= 700:
        insights.append({
            "categoria": "personale",
            "titolo": "Costo contenuto",
            "testo": f"La tua spesa annua stimata, pari a circa {costo:.2f} €, resta in una fascia contenuta.",
            "score": 75
        })

    # Risparmio potenziale
    risparmio_10 = costo * 0.10
    insights.append({
        "categoria": "personale",
        "titolo": "Potenziale di risparmio",
        "testo": f"Riducendo il consumo del 10%, potresti risparmiare circa {risparmio_10:.2f} € all’anno.",
        "score": 98
    })

    # Numero persone
    if n_persone is not None:
        if n_persone >= 5:
            insights.append({
                "categoria": "personale",
                "titolo": "Famiglia numerosa",
                "testo": "Con 5 o più persone in casa, i consumi aumentano soprattutto per cucina, acqua calda e dispositivi usati in parallelo.",
                "score": 82
            })
        elif n_persone == 1:
            insights.append({
                "categoria": "personale",
                "titolo": "Profilo individuale",
                "testo": "Per una sola persona, il livello di consumo dipende molto dall’uso degli elettrodomestici e dal tempo trascorso in casa.",
                "score": 65
            })

    # Superficie
    if m_quadri is not None:
        if m_quadri >= 120:
            insights.append({
                "categoria": "personale",
                "titolo": "Superficie elevata",
                "testo": "Una superficie abitativa ampia tende a richiedere più energia per mantenere comfort e temperatura.",
                "score": 80
            })
        elif m_quadri <= 45:
            insights.append({
                "categoria": "personale",
                "titolo": "Abitazione compatta",
                "testo": "Le abitazioni più piccole tendono ad avere un fabbisogno energetico più facile da contenere.",
                "score": 66
            })

            consumo_mq = consumo / m_quadri
            insights.append({
                "categoria": "personale",
                "titolo": "Consumo per metro quadro",
                "testo": f"Il tuo profilo corrisponde a circa {consumo_mq:.1f} kWh per metro quadro all’anno.",
                "score": 90
            })

    # Stagione
    if stagione == "inverno":
        insights.append({
            "categoria": "personale",
            "titolo": "Effetto inverno",
            "testo": "La simulazione invernale tende ad aumentare i consumi per riscaldamento, illuminazione e comfort domestico.",
            "score": 86
        })
    elif stagione == "estate":
        insights.append({
            "categoria": "personale",
            "titolo": "Effetto estate",
            "testo": "Tenere acceso un ventilatore per 6–10 ore al giorno comporta in media un consumo aggiuntivo modesto, spesso nell’ordine di alcune decine di kWh al mese.",
            "score": 64
        })

        insights.append({
            "categoria": "personale",
            "titolo": "Climatizzatore ad alto impatto",
            "testo": "Un climatizzatore usato molte ore al giorno in estate può incidere sensibilmente sulla bolletta mensile, molto più di un ventilatore.",
            "score": 90
        })

    # Prezzo kWh
    if prezzo_kwh >= 0.35:
        insights.append({
            "categoria": "personale",
            "titolo": "Prezzo unitario elevato",
            "testo": "Il costo per kWh nel tuo contesto è alto: anche piccoli aumenti di consumo incidono molto sulla spesa finale.",
            "score": 89
        })

    return insights


def genera_insight_belgio(
    prezzo_kwh,
    consumo,
    costo,
    media_consumo=3500,
    n_persone=None,
    m_quadri=None,
    stagione=None
):
    generali = genera_insight_generali_belgio() or []
    personali = genera_insight_personali_belgio(
        consumo=consumo,
        costo=costo,
        prezzo_kwh=prezzo_kwh,
        media_consumo=media_consumo,
        n_persone=n_persone,
        m_quadri=m_quadri,
        stagione=stagione
    ) or []

    generali_sorted = sorted(generali, key=lambda x: x["score"], reverse=True)
    personali_sorted = sorted(personali, key=lambda x: x["score"], reverse=True)

    return {
"generali": generali_sorted[:3],
"personali": personali_sorted[:4]
}