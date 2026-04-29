function grafico_due_linee(canvasId, storicoPrimo, storicoSecondo, nomePrimo, nomeSecondo) {
    const canvas = document.getElementById(canvasId);   //Imposta canvas

    if (!canvas || !storicoPrimo || !storicoSecondo) {
        return; //Se manca canvas, se mancano i data, blocca tutto
    }

    const labels = Array.from(
        new Set([
            ...Object.keys(storicoPrimo),
            ...Object.keys(storicoSecondo)
        ])
    ).sort();

    if (!labels.length) {
        return;
    }

    const valoriPrimo = labels.map((label) => storicoPrimo[label] ?? null);
    const valoriSecondo = labels.map((label) => storicoSecondo[label] ?? null);

    new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: nomePrimo || "Primo paese",
                    data: valoriPrimo,
                    borderColor: "#198754",
                    backgroundColor: "rgba(25, 135, 84, 0.10)",
                    tension: 0.25,
                    fill: false,
                    spanGaps: true
                },
                {
                    label: nomeSecondo || "Secondo paese",
                    data: valoriSecondo,
                    borderColor: "#0d6efd",
                    backgroundColor: "rgba(13, 110, 253, 0.10)",
                    tension: 0.25,
                    fill: false,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500
            },
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = Number(context.raw);
                            const formattedValue = Number.isFinite(value) ? value.toFixed(4) : context.raw;
                            return `${context.dataset.label}: ${formattedValue} EUR/kWh`;
                        }
                    }
                },
                legend: {
                    position: "top"
                },
                title: {
                    display: true,
                    text: "Storico prezzi dell'energia (EUR/kWh)",
                    color: "#198754",
                    font: {size: 18, weight: "bold", family: "Arial"},
                    position: "top"
                }
            },  
            scales: {
                x: {
                    ticks: {
                        font: {
                            size: 11
                        },
                        minRotation: 45,
                        maxRotation: 50,
                        autoSkip: false,
                        callback: function(value, index) {
                            return index % 3 === 0 ? this.getLabelForValue(value) : "";
                        }
                    },
                    title: {
                        display: true,
                        text: "Periodo"
                    }
                },
                y: {
                    ticks: {
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        display: true,
                        color: "rgba(0, 0, 0, 0.12)",
                        lineWidth: 1
                    },
                    title: {
                        display: true,
                        text: "EUR/kWh"
                    },
                    beginAtZero: false
                }
            }
        }
    });
}

function renderConfrontoPrezziChart(canvasId, storicoPrimo, storicoSecondo, nomePrimo, nomeSecondo) {
    grafico_due_linee(canvasId, storicoPrimo, storicoSecondo, nomePrimo, nomeSecondo);
}
