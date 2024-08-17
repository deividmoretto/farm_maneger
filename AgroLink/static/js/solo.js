document.addEventListener("DOMContentLoaded", function() {
    // Gráfico de Nível de Nitrogênio
    const nitrogenioCtx = document.getElementById('nitrogenioChart').getContext('2d');
    new Chart(nitrogenioCtx, {
        type: 'bar',
        data: {
            labels: ['Área 1', 'Área 2', 'Área 3', 'Área 4', 'Área 5'],
            datasets: [{
                label: 'Nível de Nitrogênio (%)',
                data: [12, 15, 8, 10, 13],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Gráfico de Necessidade de Calagem
    const calagemCtx = document.getElementById('calagemChart').getContext('2d');
    new Chart(calagemCtx, {
        type: 'pie',
        data: {
            labels: ['Necessário', 'Não Necessário'],
            datasets: [{
                label: 'Necessidade de Calagem',
                data: [35, 65],
                backgroundColor: ['rgba(255, 99, 132, 0.6)', 'rgba(75, 192, 192, 0.6)'],
                borderColor: ['rgba(255, 99, 132, 1)', 'rgba(75, 192, 192, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
    });

    // Gráfico de Precisão na Aplicação de Fertilizantes
    const fertilizantesCtx = document.getElementById('fertilizantesChart').getContext('2d');
    new Chart(fertilizantesCtx, {
        type: 'line',
        data: {
            labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho'],
            datasets: [{
                label: 'Quantidade Aplicada (kg/ha)',
                data: [30, 35, 33, 40, 45, 42, 38],
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Gráfico de Cuidados Essenciais Recomendados
    const cuidadosCtx = document.getElementById('cuidadosChart').getContext('2d');
    new Chart(cuidadosCtx, {
        type: 'radar',
        data: {
            labels: ['PH', 'Umidade', 'Nutrientes', 'Temperatura', 'Compactação'],
            datasets: [{
                label: 'Cuidados Recomendados',
                data: [4, 3, 4, 5, 2],
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
});
