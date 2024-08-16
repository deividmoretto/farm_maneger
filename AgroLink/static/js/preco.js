// Suponha que você tenha uma variável "noticias" que contenha um array de objetos com as notícias
const noticias = [
  { titulo: "Notícia 1", descricao: "Descrição da notícia 1" },
  { titulo: "Notícia 2", descricao: "Descrição da notícia 2" },
  { titulo: "Notícia 3", descricao: "Descrição da notícia 3" },
  // ...
];

// Seleciona o elemento "news-container"
const newsContainer = document.querySelector(".news-container");

// Loop through each news item and create an HTML element for it
noticias.forEach((noticia) => {
  const newsItem = document.createElement("div");
  newsItem.className = "news-item";
  newsItem.innerHTML = `
    <h2>${noticia.titulo}</h2>
    <p>${noticia.descricao}</p>
  `;
  newsContainer.appendChild(newsItem);
});

// Gráfico de Projeção de Preços
const nomeProduto = 'Milho';
const precosHistoricos = [
    { data: '2024-01-01', preco: 100 },
    { data: '2024-01-15', preco: 105 },
    { data: '2024-02-01', preco: 110 },
    { data: '2024-02-15', preco: 115 },
    // Adicione mais preços históricos aqui
];

function calcularPrecosProjetados() {
    const precosProjetados = [];
    for (let i = 0; i < 6; i++) {
        const data = new Date(precosHistoricos[precosHistoricos.length - 1].data);
        data.setDate(data.getDate() + (i + 1) * 15);
        const precoProjetado = precosHistoricos[precosHistoricos.length - 1].preco + (i + 1) * 5;
        precosProjetados.push({ data: data.toLocaleDateString(), preco: precoProjetado });
    }
    return precosProjetados;
}

function exibirGrafico() {
    const chartContainer = document.querySelector('.chart-container');
    const dadosGrafico = [...precosHistoricos, ...calcularPrecosProjetados()];
    const grafico = new Chart(chartContainer, {
        type: 'line',
        data: dadosGrafico,
        options: {
            title: {
                display: true,
                text: `Projeção de Preços para ${nomeProduto}`
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

exibirGrafico();