def build_dict_rule(regole):
    building_dict = {}
    for regola in regole:
        if regola.gruppo not in building_dict:
            building_dict[regola.gruppo] = []
        building_dict[regola.gruppo].append({
            "condizione": regola.condizione,
            "descrizione": regola.descrizione,
            "score": regola.score
        })
    return building_dict