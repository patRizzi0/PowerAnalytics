function renderPrezzoKwhChart(canvasId, storico) {
    const canvas = document.getElementById(canvasId);

    if (!canvas || !storico) {
        return;
    }

    // Convertiamo il dizionario Python passato con tojson in array ordinati per Chart.js.
    const labels = Object.keys(storico).sort();
    const values = labels.map((label) => storico[label]);

    if (!labels.length) {
        return;
    }

    // Primo grafico lineare: semplice, leggibile e facilmente estendibile.
    new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Prezzo kWh",
                    data: values,
                    borderColor: "#198754",
                    backgroundColor: "rgba(25, 135, 84, 0.12)",
                    tension: 0.25,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Anno"
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "EUR/kWh"
                    }
                }
            }
        }
    });
}
