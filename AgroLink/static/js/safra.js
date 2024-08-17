document.addEventListener('DOMContentLoaded', function () {
    // Dados fictícios para o gráfico de previsão climática
    const climateData = {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
            label: 'Precipitação (mm)',
            data: [120, 100, 140, 160, 150, 130],
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        },
        {
            label: 'Temperatura Média (°C)',
            data: [22, 24, 26, 28, 27, 25],
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    };

    const ctx = document.getElementById('climateChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: climateData,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Dados fictícios para resultados de pesquisas agrônomas
    const researchData = [
        { title: 'Efeito do Clima na Safra de Soja', summary: 'A pesquisa destaca os impactos do aumento de temperatura na produtividade da soja.' },
        { title: 'Uso de Fertilizantes na Safra de Milho', summary: 'Estudo sobre a aplicação de fertilizantes e seu efeito na produção de milho.' },
        { title: 'Rotação de Culturas para Aumentar a Produtividade', summary: 'Pesquisa sugere que a rotação de culturas pode melhorar a saúde do solo e aumentar a produtividade.' }
    ];

    const researchContainer = document.getElementById('research-container');
    researchData.forEach(item => {
        const researchElement = document.createElement('div');
        researchElement.classList.add('research-item');
        researchElement.innerHTML = `<h3>${item.title}</h3><p>${item.summary}</p>`;
        researchContainer.appendChild(researchElement);
    });
});
