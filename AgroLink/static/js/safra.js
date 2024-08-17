// Função para exibir as informações inseridas
function exibirInformacoes() {
    const tipoCultivo = document.getElementById('tipoCultivo').value;
    const dataPlantio = document.getElementById('dataPlantio').value;
    const dataColheita = document.getElementById('dataColheita').value;
    const areaPlantada = parseFloat(document.getElementById('areaPlantada').value);
    const rendimentoEsperado = parseFloat(document.getElementById('rendimentoEsperado').value);
    
    // Verificação básica para garantir que todos os campos estejam preenchidos
    if (!tipoCultivo || !dataPlantio || !dataColheita || isNaN(areaPlantada) || isNaN(rendimentoEsperado)) {
        alert("Por favor, preencha todos os campos corretamente.");
        return;
    }

    // Calcular o rendimento por hectare
    const rendimentoPorHectare = (rendimentoEsperado / areaPlantada).toFixed(2);

    // Exibir os dados calculados
    const resultadoDiv = document.getElementById('resultado');
    resultadoDiv.innerHTML = `
        <h3>Informações da Safra</h3>
        <p><strong>Tipo de Cultivo:</strong> ${tipoCultivo}</p>
        <p><strong>Data de Plantio:</strong> ${new Date(dataPlantio).toLocaleDateString()}</p>
        <p><strong>Data da Colheita:</strong> ${new Date(dataColheita).toLocaleDateString()}</p>
        <p><strong>Área Plantada:</strong> ${areaPlantada} hectares</p>
        <p><strong>Rendimento Esperado:</strong> ${rendimentoEsperado} toneladas</p>
        <p><strong>Rendimento por Hectare:</strong> ${rendimentoPorHectare} toneladas/hectare</p>
    `;
}

// Exemplo de funcionalidades adicionais para as abas
document.querySelectorAll('.tabcontent').forEach(tab => {
    tab.style.display = 'none'; // Esconde todas as abas inicialmente
});

function abrirAba(abaId) {
    document.querySelectorAll('.tabcontent').forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(abaId).style.display = 'block';
}

// Suponha que ao carregar a página, a primeira aba deva ser exibida
document.addEventListener('DOMContentLoaded', () => {
    abrirAba('Pragas');
});
