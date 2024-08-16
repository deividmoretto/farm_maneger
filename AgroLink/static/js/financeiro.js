function mostrarDetalhes() {
    const financiamento = document.getElementById('financiamento').value;
    const detalhesFinanciamento = document.getElementById('detalhesFinanciamento');

    if (financiamento === 'banco1') {
        detalhesFinanciamento.innerText = "Bradesco oferece uma taxa de 3.5% ao ano.";
    } else if (financiamento === 'banco2') {
        detalhesFinanciamento.innerText = "Itau oferece uma taxa de 4.0% ao ano.";
    } else if (financiamento === 'banco3') {
        detalhesFinanciamento.innerText = "Santander oferece uma taxa de 4.2% ao ano.";
    } else {
        detalhesFinanciamento.innerText = "";
    }
}

function calcularAplicacao() {
    const areaSafra = document.getElementById('areaSafra').value;
    const recursoNecessario = document.getElementById('recursoNecessario').value;
    const financiamento = document.getElementById('financiamento').value;

    if (!financiamento) {
        alert("Por favor, selecione um financiamento.");
        return;
    }

    // Exemplo de cálculo de aplicação financeira
    const valorPorMetro = recursoNecessario / areaSafra;
    let alerta = '';

    if (valorPorMetro > 10) { // Limite arbitrário para demonstração
        alerta = `O valor aplicado por metro quadrado (${valorPorMetro.toFixed(2)} R$/m²) é alto. Considere revisar o plano financeiro.`;
    } else {
        alerta = `O valor aplicado por metro quadrado (${valorPorMetro.toFixed(2)} R$/m²) está dentro do aceitável.`;
    }

    // Exibição dos resultados
    document.getElementById('valorAplicado').innerText = `Valor aplicado por metro quadrado: R$ ${valorPorMetro.toFixed(2)}`;
    document.getElementById('alertaFinanceiro').innerText = alerta;
    document.getElementById('result').style.display = 'block';
}
