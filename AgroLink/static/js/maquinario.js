function gerarChecklist() {
    const equipamento = document.getElementById('equipamento').value;
    const horasOperacao = document.getElementById('horasOperacao').value;
    const status = document.getElementById('status').value;
    const checklistItems = Array.from(document.querySelectorAll('#checklistOptions input:checked'))
                                .map(item => item.value);

    let alerta = '';
    if (horasOperacao > 100) {
        alerta = `O equipamento ${equipamento} excedeu 100 horas de operação. É necessário realizar a manutenção preventiva.`;
    } else {
        alerta = `O equipamento ${equipamento} está dentro do limite de horas de operação.`;
    }

    document.getElementById('checklistGerado').innerText = `Checklist de Manutenção para ${equipamento}:\n${checklistItems.join('\n')}`;
    document.getElementById('alerta').innerText = alerta;
    document.getElementById('result').style.display = 'block';

    console.log("Checklist enviado para o banco de dados.");
}
