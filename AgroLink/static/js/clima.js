// Função para obter dados de previsão do tempo de uma API
async function getWeatherData() {
    try {
       // const apiKey =  Substitua com sua chave API
      // const apiUrl =  Substitua 'Rio+de+Janeiro' com a cidade desejada
      const response = await fetch(apiUrl);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao obter dados da API:', error);
      return null;
    }
  }
  
  // Função para atualizar a previsão do tempo na página
  async function updateWeather() {
    const weatherData = await getWeatherData();
    if (weatherData) {
      document.getElementById('current-temperature').textContent = weatherData.main.temp.toFixed(0);
      document.getElementById('current-wind-speed').textContent = weatherData.wind.speed;
      // Atualizar outras informações do tempo aqui...
    }
  }
  
  // Chamar a função de atualização quando a página carregar
  window.onload = updateWeather;