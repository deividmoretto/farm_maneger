document.addEventListener("DOMContentLoaded", function() {
    // Simulação de notícias
    const noticias = [
        { titulo: "Aumento na produção de soja impulsiona preços", data: "15/08/2024" },
        { titulo: "Clima adverso afeta safra de milho", data: "14/08/2024" },
        { titulo: "Novo acordo comercial pode favorecer exportações", data: "13/08/2024" },
    ];

    const newsContainer = document.querySelector(".news-container");
    noticias.forEach(noticia => {
        const newsItem = document.createElement("div");
        newsItem.className = "news-item";
        newsItem.innerHTML = `<strong>${noticia.data}</strong> - ${noticia.titulo}`;
        newsContainer.appendChild(newsItem);
    });

    // Simulação de projeção de preços (utilizando Chart.js)
    const ctx = document.createElement("canvas");
    document.querySelector(".chart-container").appendChild(ctx);

    const data = {
        labels: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
        datasets: [{
            label: 'Preço da Cultura (R$/saca)',
            data: [50, 55, 53, 60, 65, 63, 68, 70, 72, 74, 73, 75],
            borderColor: 'rgba(0, 128, 0, 0.6)',
            backgroundColor: 'rgba(0, 128, 0, 0.1)',
            borderWidth: 2,
            fill: true,
        }]
    };

    const options = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: false,
                suggestedMin: 50,
                suggestedMax: 80,
            }
        }
    };

    new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
});
