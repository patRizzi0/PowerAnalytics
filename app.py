import os
import logging

from flask import render_template, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from connection import app

from models.category_model import Category
from models.device_model import Device
from service.consumi_service import calcola_consumo_abitazione
from service.converts_paese_eurostat import converts_paese_eurostat
from service.insights.insight_generator import generate_insight
from service.eurostat_service import EurostatService
from service.validators import check_input

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def render_user_error(message, status_code=500, title="Qualcosa non ha funzionato"):
    """Mostra un errore leggibile invece di lasciare l'utente davanti a un crash."""
    return render_template(
        "pages/error.html",
        title=title,
        message=message,
        status_code=status_code
    ), status_code


@app.errorhandler(404)
def not_found_error(error):
    return render_user_error(
        "La pagina che stai cercando non esiste o e' stata spostata.",
        status_code=404,
        title="Pagina non trovata"
    )


@app.errorhandler(HTTPException)
def http_error(error):
    return render_user_error(
        error.description or "La richiesta non puo' essere completata.",
        status_code=error.code or 500,
        title=error.name or "Errore"
    )


@app.errorhandler(Exception)
def generic_error(error):
    logger.exception("Errore non gestito: %s", error)
    return render_user_error(
        "Si e' verificato un errore inatteso. Riprova tra poco.",
        status_code=500,
        title="Errore temporaneo"
    )


@app.route("/home")
def home():
    """Mostra la pagina iniziale dell'applicazione."""
    return render_template("pages/home.html")


@app.route("/calcolo_elettrodomestico", methods=["GET", "POST"])
def elettrodomestici():
    """Carica dispositivi e categorie usati dal calcolo elettrodomestici."""
    try:
        all_devices = Device.query.all()
        all_categories = Category.query.all()
    except SQLAlchemyError as e:
        logger.warning("Errore database nel caricamento elettrodomestici: %s", e)
        return render_template(
            "pages/calcolo_elettrodomestico.html",
            devices=[],
            categories=[],
            error="Non riesco a caricare gli elettrodomestici in questo momento. Riprova tra poco."
        ), 503

    return render_template(
        "pages/calcolo_elettrodomestico.html",
        devices=all_devices,
        categories=all_categories
    )


@app.route("/device/<int:device_id>")
def get_device(device_id):
    """Espone i dati di un singolo elettrodomestico in formato JSON."""
    try:
        device = Device.query.get_or_404(device_id)
    except SQLAlchemyError as e:
        logger.warning("Errore database nel recupero dispositivo %s: %s", device_id, e)
        return jsonify({
            "errore": "Non riesco a recuperare il dispositivo in questo momento."
        }), 503

    return jsonify({
        "id": device.id,
        "name": device.name,
        "average_watts": device.average_watts,
        "standby_watts": device.standby_watts
    })


@app.route("/consumi")
def consumi():
    """Mostra il form guidato per stimare i consumi domestici."""
    return render_template("pages/consumi.html")


@app.route("/eurostat")
def statistiche():
    """Mostra la pagina dedicata ai dati Eurostat."""
    return render_template("pages/eurostat.html")


@app.route("/filtro")
def filtra_dati_eurostat():
    """Normalizza i parametri query e recupera il dato Eurostat filtrato."""
    anno = request.args.get("data_bilan", default="2022")
    paese = request.args.get("paese", default="belgio").strip().lower()
    banda = request.args.get("banda", default="KWH2500-4999")

    try:
        dato_normalizzato = converts_paese_eurostat(paese, banda)
    except RuntimeError as e:
        dato_normalizzato = {"errore": str(e)}
    except Exception as e:
        logger.exception("Errore durante il filtro Eurostat: %s", e)
        dato_normalizzato = {
            "errore": "Non riesco a recuperare i dati Eurostat in questo momento. Riprova tra poco."
        }

    return render_template(
        "pages/filtro.html",
        data=dato_normalizzato,
        anno=anno,
        paese=paese,
        banda=banda
    )


@app.route("/calcolo_consumi", methods=["GET", "POST"])
def calcolo_consumi():
    """Gestisce il form di simulazione consumi e prepara risultati e insight."""
    consumi = None
    insights = {"generali": [], "personali": []}

    paese = None
    n_persone = None
    m_quadri = None
    stagione = None
    tipo_abitazione = None

    if request.method == "POST":
        paese = request.form.get("paese")

        try:
            n_persone = int(request.form.get("n_persone"))
            m_quadri = int(request.form.get("m_quadri"))
            errore = check_input(n_persone, m_quadri)
            if errore:
                return render_template("pages/calcolo_consumi.html", error=errore)
        except (ValueError, TypeError):
            return render_template(
                "pages/calcolo_consumi.html",
                error="Inserisci valori validi per persone e metri quadri."
            )

        stagione = request.form.get("stagione")
        tipo_abitazione = request.form.get("tipo_abitazione")

        try:
            consumi = calcola_consumo_abitazione(
                paese,
                n_persone,
                m_quadri,
                stagione,
                tipo_abitazione
            )
        except RuntimeError as e:
            return render_template(
                "pages/calcolo_consumi.html",
                error=f"Errore nel calcolo dei consumi: {e}"
            )
        except Exception as e:
            logger.exception("Errore inatteso nel calcolo consumi: %s", e)
            return render_template(
                "pages/calcolo_consumi.html",
                error="Non riesco a completare il calcolo in questo momento. Riprova tra poco."
            ), 500

        try:
            consumo = consumi["consumo_totale_kwh"]
            costo = consumi["costo_stimato"]
            prezzo_kwh = consumi["prezzo_kwh"]
            storico = consumi.get("storico", {})
        except KeyError as e:
            return render_template(
                "pages/calcolo_consumi.html",
                error=f"Dato mancante per generare gli insight: {e.args[0]}"
            )

        try:
            insights = generate_insight(
                paese=paese,
                consumo=consumo,
                costo=costo,
                prezzo_kwh=prezzo_kwh,
                n_persone=n_persone,
                m_quadri=m_quadri,
                stagione=stagione,
                tipo_abitazione=tipo_abitazione,
                storico=storico
            )
        except Exception as e:
            logger.warning("Errore nella generazione insight: %s", e)
            insights = {
                "generali": [],
                "personali": [{
                    "titolo": "Insight non disponibili",
                    "testo": "Il calcolo e' riuscito, ma non riesco a generare gli insight in questo momento."
                }]
            }

    return render_template(
        "pages/calcolo_consumi.html",
        consumi=consumi,
        insights=insights,
        paese=paese,
        n_persone=n_persone,
        m_quadri=m_quadri,
        stagione=stagione,
        tipo_abitazione=tipo_abitazione
        )


if os.getenv("FLASK_ENV") == "development" or os.getenv("FLASK_DEBUG") == "1":
    @app.route("/debug/test_eurostat")
    def test_eurostat():
        """Endpoint tecnico per verificare la risposta grezza di Eurostat."""
        dati = EurostatService.prendi_dati_grezzi("BE")
        if dati is None:
            return jsonify({
                "errore": "Dati Eurostat temporaneamente non disponibili"
            }), 503
        return jsonify(dati)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
