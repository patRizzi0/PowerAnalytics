from models.Rule import Rule
from service.build_dict_rule import build_dict_rule
from service.calculators.build_description import build_description
from service.calculators.key_precedent import _last_key


def _storico_con_precedente(storico):
    """Verifica che esistano ultimo periodo e corrispondente anno precedente."""
    if not storico:
        return False
    previous_key = _last_key(storico)
    return previous_key in storico


regole = [
    Rule(
        condizione=lambda consumo, **kw: consumo > 5000,
        gruppo="consumo",
        descrizione=lambda consumo, **kw: (
            f"Il tuo consumo annuo di {consumo} kWh e' superiore alla soglia di attenzione."
        ),
        score=10,
    ),
    Rule(
        condizione=lambda costo, **kw: costo > 1000,
        gruppo="costo",
        descrizione=lambda costo, **kw: (
            f"Il tuo costo annuo stimato di {costo} EUR e' superiore alla soglia di attenzione."
        ),
        score=10,
    ),
    Rule(
        condizione=lambda storico, **kw: _storico_con_precedente(storico),
        gruppo="tendenza",
        descrizione=lambda storico, **kw: (
            build_description(storico)
        ),
        score=10,
    )
]

building_dict = build_dict_rule(regole)


def _destinazione_insight(gruppo):
    """Mantiene compatibile l'output con il template esistente."""
    if gruppo in ("generale", "generali"):
        return "generali"
    return "personali"


def generate_insight(**kwargs):
    """Valuta le regole e restituisce insight divisi per sezione del template."""
    insights = {"generali": [], "personali": []}

    for gruppo, regole_gruppo in building_dict.items():
        for rule in sorted(regole_gruppo, key=lambda r: r.score, reverse=True):
            valutazione, descrizione = rule.evaluate(**kwargs)
            if valutazione:
                destinazione = _destinazione_insight(gruppo)
                insights[destinazione].append({
                    "titolo": gruppo.capitalize(),
                    "testo": descrizione
                })
                break

    return insights
