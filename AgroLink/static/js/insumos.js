function calculate() {
    const area = document.getElementById('area').value;
    const insumo = document.getElementById('insumo').value;
    const consumoMensal = document.getElementById('consumoMensal').value;
    const estoqueAtual = document.getElementById('estoqueAtual').value;
    const validade = document.getElementById('validade').value;

    // Cálculo da quantidade necessária de insumo
    const insumoPorMetro = insumo === 'fertilizer' ? 0.1 : 0.05; // kg/m², exemplo
    const quantidadeNecessaria = area * insumoPorMetro;

    // Preço baseado em lojas (simulação)
    const precoPorKg = 20; // Exemplo de preço por kg
    const precoTotal = quantidadeNecessaria * precoPorKg;

    // Cálculo de reabastecimento
    const mesesRestantes = estoqueAtual / consumoMensal;
    const precisaReabastecer = mesesRestantes < validade;

    // Exibição dos resultados
    document.getElementById('quantidade').innerText = `Quantidade necessária: ${quantidadeNecessaria.toFixed(2)} kg`;
    document.getElementById('preco').innerText = `Preço total estimado: R$ ${precoTotal.toFixed(2)}`;
    document.getElementById('reabastecimento').innerText = precisaReabastecer ? 
        `Você precisará reabastecer em breve!` : 
        `Seu estoque é suficiente para os próximos meses.`;
    
    document.getElementById('result').style.display = 'block';
}
