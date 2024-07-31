document.addEventListener('DOMContentLoaded', () => {
    // Inicializa a funcionalidade quando o documento estiver carregado
});

function toggleNav() {
    const sideNav = document.getElementById("sideNav");
    const main = document.getElementById("main");
    const navTitle = document.getElementById("navTitle");
    const logo = sideNav.querySelector('.logo');
    const links = sideNav.querySelectorAll('a');

    if (sideNav.classList.contains('closed')) {
        sideNav.classList.remove('closed');
        sideNav.style.width = "250px";
        main.classList.remove('main-collapsed');
        main.classList.add('main-expanded');
        navTitle.innerHTML = "AgroVision";
        logo.style.maxWidth = "150px";
        links.forEach(link => link.style.opacity = 1);
    } else {
        sideNav.classList.add('closed');
        sideNav.style.width = "70px";
        main.classList.remove('main-expanded');
        main.classList.add('main-collapsed');
        navTitle.innerHTML = "AgrV";
        logo.style.maxWidth = "50px";
        links.forEach(link => link.style.opacity = 0);
    }
}

function fetchWeatherData() {
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;

    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener('readystatechange', function () {
        if (this.readyState === this.DONE) {
            if (this.status === 200) {
                const response = JSON.parse(this.responseText);
                console.log(response);
                displayData(response);
            } else {
                console.error('Erro ao buscar dados:', this.responseText);
                document.getElementById('api-content').innerHTML = '<p>Erro ao buscar dados da API.</p>';
            }
        }
    });

    xhr.open('GET', `https://open-weather13.p.rapidapi.com/city/${city}/${state}`);
    xhr.setRequestHeader('x-rapidapi-key', '98bac9efaemshbb492e7779f0433p18fe14jsna0a0f74a6c97');
    xhr.setRequestHeader('x-rapidapi-host', 'open-weather13.p.rapidapi.com');

    xhr.send(null);
}

function displayData(data) {
    const apiContent = document.getElementById('api-content');

    // Clear existing content
    apiContent.innerHTML = '';

    // Display the data received from the API
    if (data) {
        const itemElement = document.createElement('div');
        itemElement.className = 'api-item';
        itemElement.innerHTML = `
            <p><strong>Temperatura:</strong> ${data.current.temperature} °C</p>
            <p><strong>Umidade:</strong> ${data.current.humidity} %</p>
            <p><strong>Velocidade do vento:</strong> ${data.current.wind_speed} m/s</p>
        `;
        apiContent.appendChild(itemElement);
    } else {
        apiContent.innerHTML = '<p>Nenhum dado disponível</p>';
    }
}
