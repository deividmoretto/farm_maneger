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

    // Safras e preços simulados
    const safras = [
        { nome: "Trigo", preco: "R$ 75,00/saca" },
        { nome: "Milho", preco: "R$ 65,00/saca" },
        { nome: "Soja", preco: "R$ 90,00/saca" },
        { nome: "Café", preco: "R$ 120,00/saca" }
    ];

    const cropList = document.getElementById("crop-list");
    const priceDisplay = document.getElementById("price-display");

    safras.forEach(safra => {
        const listItem = document.createElement("li");
        listItem.className = "crop-item";
        listItem.innerText = safra.nome;
        listItem.addEventListener("click", function() {
            priceDisplay.innerText = `Preço atual de ${safra.nome}: ${safra.preco}`;
        });
        cropList.appendChild(listItem);
    });
});
