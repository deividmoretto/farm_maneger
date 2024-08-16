function gerarChecklist() {
    const equipamento = document.getElementById('equipamento').value;
    const horasOperacao = document.getElementById('horasOperacao').value;
    const checklist = document.getElementById('checklist').value;
    const status = document.getElementById('status').value;

    // Exemplo de alertas de manutenção
    let alerta = '';
    if (horasOperacao > 100) {
        alerta = `O equipamento ${equipamento} excedeu 100 horas de operação. É necessário realizar a manutenção preventiva.`;
    } else {
        alerta = `O equipamento ${equipamento} está dentro do limite de horas de operação.`;
    }

    // Exibição do checklist gerado
    document.getElementById('checklistGerado').innerText = `Checklist de Manutenção para ${equipamento}:\n${checklist}`;
    document.getElementById('alerta').innerText = alerta;
    document.getElementById('result').style.display = 'block';

    // Simulação de envio para banco de dados (pode ser adaptado para um envio real via API)
    console.log("Checklist enviado para o banco de dados.");
}
