from service.consumi_service import calcola_consumo_abitazione as calcola_consumo_abitazione_service


def calcola_consumo_abitazione(paese, n_persone, m_quadri, stagione, tipo_abitazione):
    """Compatibilita': la logica di calcolo vive in service.consumi_service."""
    return calcola_consumo_abitazione_service(
        paese,
        n_persone,
        m_quadri,
        stagione,
        tipo_abitazione,
    )
