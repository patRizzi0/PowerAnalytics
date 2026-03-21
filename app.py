from flask import render_template, jsonify, request
from connection import app
import requests

from models.category_model import Category
from models.device_model import Device

from service.converts import converts_json_eurostat

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/calcolo_elettrodomestico", methods=["GET", "POST"])
def elettrodomestici():
    all_devices = Device.query.all()
    all_categories = Category.query.all()

    return render_template(
"calcolo_elettrodomestico.html",
devices=all_devices,
categories=all_categories
)


@app.route("/device/<int:device_id>")
def get_device(device_id):
    device = Device.query.get_or_404(device_id)

    return jsonify({
"id": device.id,
"name": device.name,
"average_watts": device.average_watts,
"standby_watts": device.standby_watts
})


@app.route("/consumi")
def consumi():
    return render_template("consumi.html")

@app.route("/eurostat")
def statistiche():
    return render_template("eurostat.html")

@app.route("/filtro")
def filtra_dati_eurostat():
    anno = request.args.get("data_bilan", default="2022")

    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ten00121"

    params = {
        "time": anno,
        "lang": "EN"
    }

    response = requests.get(url, params=params, timeout=20)
    data = response.json()

    dati_filtrati= converts_json_eurostat(data)


    return render_template("filtro.html", data=dati_filtrati, anno=anno)



if __name__ == "__main__":
    app.run(debug=True)