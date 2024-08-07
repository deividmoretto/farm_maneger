// Adiciona um ouvinte de evento que será executado quando o DOM (Document Object Model) estiver completamente carregado.
// Isso garante que todas as manipulações do DOM sejam feitas apenas depois que o documento está pronto.
document.addEventListener('DOMContentLoaded', () => {
    
});

 // Função para alternar a visibilidade e o estado da barra de navegação lateral.
function toggleNav() {
   
    const sideNav = document.getElementById("sideNav"); // Obtém o elemento da barra de navegação lateral pelo ID 'sideNav'.
    const main = document.getElementById("main"); // Obtém o elemento principal do documento pelo ID 'main'.
    const navTitle = document.getElementById("navTitle"); // Obtém o elemento do título da navegação pelo ID 'navTitle'.
    const logo = sideNav.querySelector('.logo'); // Obtém o elemento do logotipo dentro da barra de navegação.
    const links = sideNav.querySelectorAll('a'); // Seleciona todos os links <a> dentro da barra de navegação.

    // Se a barra de navegação está atualmente fechada:
    if (sideNav.classList.contains('closed')) {
        
        sideNav.classList.remove('closed'); // Remove a classe 'closed', abrindo a barra de navegação.
        sideNav.style.width = "250px"; // Define a largura da barra de navegação para 250 pixels.
        main.classList.remove('main-collapsed'); // Remove a classe que indica que o conteúdo principal está colapsado.
        main.classList.add('main-expanded'); // Adiciona a classe que indica que o conteúdo principal está expandido.
        navTitle.innerHTML = "AgroLink"; // Define o título completo "AgroLink" para a barra de navegação.
        logo.style.maxWidth = "150px"; // Define a largura máxima do logotipo para 150 pixels.
        links.forEach(link => link.style.opacity = 1); // Define a opacidade dos links para 1 (totalmente visível).
    } 
    
    // Se a barra de navegação está atualmente aberta:
    else {
        
        sideNav.classList.add('closed'); // Adiciona a classe 'closed', fechando a barra de navegação.
        sideNav.style.width = "70px"; // Define a largura da barra de navegação para 70 pixels (tamanho colapsado).
        main.classList.remove('main-expanded'); // Remove a classe que indica que o conteúdo principal está expandido.
        main.classList.add('main-collapsed'); // Adiciona a classe que indica que o conteúdo principal está colapsado.
        navTitle.innerHTML = "AgrL"; // Define um título reduzido "AgrL" para a barra de navegação quando está fechada.
        logo.style.maxWidth = "50px"; // Define a largura máxima do logotipo para 50 pixels.
        links.forEach(link => link.style.opacity = 0); // Define a opacidade dos links para 0 (invisível).
    }
}

// Função para buscar dados meteorológicos de uma API externa usando XMLHttpRequest.
function fetchWeatherData() {

    const city = document.getElementById('city').value; // Obtém o valor inserido no campo de entrada com ID 'city'.
    const state = document.getElementById('state').value; // Obtém o valor inserido no campo de entrada com ID 'state'.

    const xhr = new XMLHttpRequest(); // Cria uma nova instância de XMLHttpRequest para fazer requisições HTTP.
    xhr.withCredentials = true; // Define que as credenciais (cookies, etc.) serão enviadas com a requisição.

    // Adiciona um ouvinte de evento para monitorar mudanças no estado da requisição HTTP.
    xhr.addEventListener('readystatechange', function () {

        // Quando a requisição estiver completamente carregada (estado DONE):
        if (this.readyState === this.DONE) {

            // Se a resposta HTTP tiver um status de sucesso (200):
            if (this.status === 200) {

                const response = JSON.parse(this.responseText); // Converte a resposta JSON em um objeto JavaScript.
                console.log(response); // Exibe a resposta no console do navegador (útil para depuração).
                displayData(response); // Chama a função displayData() para exibir os dados recebidos na página.
            } 
            
            // Se houver um erro na requisição:
            else {
                
                console.error('Erro ao buscar dados:', this.responseText); // Exibe uma mensagem de erro no console com os detalhes.
                document.getElementById('api-content').innerHTML = '<p>Erro ao buscar dados da API.</p>'; // Exibe uma mensagem de erro na interface do usuário.
            }
        }
    });

    // Abre uma requisição HTTP do tipo GET para a URL da API, incluindo os parâmetros de cidade e estado.

    xhr.open('GET', `https://open-weather13.p.rapidapi.com/city/${city}/${state}`);

    // Define o cabeçalho da requisição com a chave de API fornecida (necessário para autenticação).
    xhr.setRequestHeader('x-rapidapi-key', '98bac9efaemshbb492e7779f0433p18fe14jsna0a0f74a6c97');

    // Define o cabeçalho da requisição com o host da API.
    xhr.setRequestHeader('x-rapidapi-host', 'open-weather13.p.rapidapi.com');

    // Envia a requisição HTTP. O parâmetro 'null' indica que não há corpo de requisição a ser enviado
    xhr.send(null);
}

    // Função para exibir os dados meteorológicos na página.
function displayData(data) {

    const apiContent = document.getElementById('api-content'); // Obtém o elemento que conterá os dados da API pelo ID 'api-content'.

    // Limpa o conteúdo existente
    apiContent.innerHTML = ''; // Remove qualquer conteúdo anterior para preparar o espaço para novos dados.

    // Exibe os dados recebidos da API
    if (data) {
        // Se os dados existem (ou seja, a resposta da API foi bem-sucedida):

        const itemElement = document.createElement('div'); // Cria um novo elemento <div> para conter os dados meteorológicos.
        itemElement.className = 'api-item'; // Define a classe do novo elemento como 'api-item' para estilização.

        itemElement.innerHTML = `
            <p><strong>Temperatura:</strong> ${data.current.temperature} °C</p>
            <p><strong>Umidade:</strong> ${data.current.humidity} %</p>
            <p><strong>Velocidade do vento:</strong> ${data.current.wind_speed} m/s</p>
        `;
        // Define o conteúdo HTML do elemento com os dados de temperatura, umidade e velocidade do vento obtidos da API.

        apiContent.appendChild(itemElement); // Adiciona o novo elemento com os dados à página dentro do 'api-content'.
    } 
    
    // Se não houver dados disponíveis:
    else {

        apiContent.innerHTML = '<p>Nenhum dado disponível</p>'; // Exibe uma mensagem indicando que não há dados disponíveis.
    }
}
