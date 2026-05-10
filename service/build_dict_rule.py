from models.Rule import Rule


def build_dict_rule(regole: list[Rule]) -> dict[str, list[Rule]]:
    """Raggruppa le regole per gruppo di appartenenza."""
    building_dict: dict[str, list[Rule]] = {}
    for regola in regole:
        if regola.gruppo not in building_dict:
            building_dict[regola.gruppo] = []
        building_dict[regola.gruppo].append(regola)
    return building_dict
