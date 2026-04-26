from models.Rule import Rule
from service.build_dict_rule import build_dict_rule
from service.calculators.media_nazionale import get_national_average

regole = [
    Rule(
        condizione = lambda consumo, **kw: consumo > 5000,
        gruppo = "consumo",
        descrizione = lambda consumo, **kw: f"Il tuo consumo annuo di {consumo} kWh è superiore alla media nazionale.",
        score = 10
    ),
    Rule(
        condizione = lambda costo, **kw: costo > 1000,
        gruppo = "costo",
        descrizione = lambda costo, **kw: f"Il tuo costo annuo stimato di {costo} EUR è superiore alla media nazionale.",
        score = 10
    ),
    Rule(
        condizione = lambda paese, consumo, **kw: consumo > get_national_average(paese)["prezzo_kwh"],
        gruppo = "rischio",
        descrizione = lambda consumo, **kw: f"Il tuo consumo annuo di {consumo} kWh è superiore alla media nazionale.",
        score = 10
    )
]

building_dict = build_dict_rule(regole)

def generate_insight(**kwargs):
    insights = []

    for gruppo, regole in building_dict.items():
        for regola in sorted(regole, key=lambda r: r["score"], reverse=True):
            valutazione = regola["condizione"](**kwargs)
            if valutazione:
                descrizione = regola["descrizione"](**kwargs)
                insights.append({
                    "gruppo": gruppo,
                    "descrizione": descrizione
                })
                break  # Esce dopo aver valutato il primo gruppo di regole


    return insights

