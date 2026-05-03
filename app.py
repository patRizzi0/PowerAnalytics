import os
import logging

from flask import render_template, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from connection import app

from models.category_model import Category
from models.device_model import Device
from service.calculators.fetch_paese import fetch_paese
from service.consumi_service import calcola_consumo_abitazione
from service.converts_paese_eurostat import converts_paese_eurostat
from service.insights.insight_generator import generate_insight
from service.eurostat_service import EurostatService
from service.validators import check_input
from service.countries import SUPPORTED_COUNTRIES
from service.converts import *

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

@app.route("/francia_prova")
def francia_prova():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204?geo=FR&unit=KWH&currency=EUR&tax=I_TAX&nrg_cons=KWH2500-4999"
    dati_francia = prezzi_francia(url)
    print(dati_francia)
    return render_template("pages/francia_prova.html", dati_francia=dati_francia)



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
    return render_template("pages/consumi.html", paesi=SUPPORTED_COUNTRIES)


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


@app.route("/confronto", methods=["GET", "POST"])
def confronto():
    """Confronta il prezzo dell'energia tra due paesi."""
    paesi = {code: info["it"] for code, info in SUPPORTED_COUNTRIES.items()}
    dati_a = None
    dati_b = None
    errore_a = None
    errore_b = None
    paese_a = None
    paese_b = None
    storico_primo = {}
    storico_secondo = {}
    nome_primo = ""
    nome_secondo = ""

    if request.method == "POST":
        paese_a = request.form.get("paese_a", "").strip().lower()
        paese_b = request.form.get("paese_b", "").strip().lower()

        try:
            dati_a = fetch_paese(paese_a)
            if dati_a is not None and "errore" in dati_a:
                errore_a = dati_a["errore"]
                dati_a = None
        except Exception as e:
            logger.warning("Errore paese A (%s): %s", paese_a, e)
            errore_a = "Non riesco a recuperare i dati per questo paese."

        try:
            dati_b = fetch_paese(paese_b)
            if dati_b is not None and "errore" in dati_b:
                errore_b = dati_b["errore"]
                dati_b = None
        except Exception as e:
            logger.warning("Errore paese B (%s): %s", paese_b, e)
            errore_b = "Non riesco a recuperare i dati per questo paese."

        if dati_a:
            storico_primo = dati_a.get("storico", {})
            nome_primo = paesi.get(dati_a.get("paese"), paese_a.title())
        if dati_b:
            storico_secondo = dati_b.get("storico", {})
            nome_secondo = paesi.get(dati_b.get("paese"), paese_b.title())

        print(storico_primo)
        print(storico_secondo)

    return render_template(
        "pages/confronto.html",
        paesi=paesi,
        dati_a=dati_a,
        dati_b=dati_b,
        errore_a=errore_a,
        errore_b=errore_b,
        paese_a=paese_a,
        paese_b=paese_b,
        storico_primo=storico_primo,
        storico_secondo=storico_secondo,
        nome_primo=nome_primo,
        nome_secondo=nome_secondo,
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
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
