from service.insights.insight_belgio import genera_insight_belgio
from service.insights.insight_lussemburgo import genera_insight_lussemburgo

def genera_insight_per_paese(paese, **kwargs):
    paese = paese.lower()

    mapping = {
        "belgio": genera_insight_belgio,
        "lussemburgo": genera_insight_lussemburgo,
    }

    funzione = mapping.get(paese)
    if not funzione:
        return []

    return funzione(**kwargs)