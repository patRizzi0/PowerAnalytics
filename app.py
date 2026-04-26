from flask import render_template, jsonify, request
from connection import app

from models.category_model import Category
from models.device_model import Device
from service.consumi_service import calcola_consumo_abitazione
from service.converts_paese_eurostat import converts_paese_eurostat
from service.insights.insight_generator import generate_insight
from service.insights.router_insight import genera_insight_per_paese
from service.eurostat_service import EurostatService
from service.validators import check_input

@app.route("/home")
def home():
    """Mostra la pagina iniziale dell'applicazione."""
    return render_template("pages/home.html")


@app.route("/calcolo_elettrodomestico", methods=["GET", "POST"])
def elettrodomestici():
    """Carica dispositivi e categorie usati dal calcolo elettrodomestici."""
    all_devices = Device.query.all()
    all_categories = Category.query.all()

    return render_template(
        "pages/calcolo_elettrodomestico.html",
        devices=all_devices,
        categories=all_categories
    )


@app.route("/device/<int:device_id>")
def get_device(device_id):
    """Espone i dati di un singolo elettrodomestico in formato JSON."""
    device = Device.query.get_or_404(device_id)

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

    dato_normalizzato = converts_paese_eurostat(paese, banda)

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

        insights = generate_insight(
            paese = paese,
            n_persone = n_persone,
            m_quadri = m_quadri,
            stagione = stagione,
            tipo_abitazione = tipo_abitazione,
            consumi = consumi
        )

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


@app.route("/test_eurostat")
def test_eurostat():
    """Endpoint tecnico per verificare la risposta grezza di Eurostat."""
    dati = EurostatService.prendi_dati_grezzi("BE")
    return jsonify(dati)

if __name__ == "__main__":
    app.run(debug=True)
