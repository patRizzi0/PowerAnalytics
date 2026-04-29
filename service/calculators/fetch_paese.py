import logging
from service.converts_paese_eurostat import converts_paese_eurostat

logger = logging.getLogger(__name__)


def fetch_paese(paese):
    try:
        return converts_paese_eurostat(paese)
    except Exception as e:
        logger.warning("Errore durante fetch_paese per %s: %s", paese, e)
        return {"errore": "Dati non disponibili per questo paese."}
    