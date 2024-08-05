# API de Previsão do Tempo

## Descrição

Esta API fornece previsões do tempo para cidades pré-definidas. Os dados são obtidos a partir do serviço OpenWeatherMap.

## Endpoints

### /cities

Retorna a lista de cidades disponíveis.

**Exemplo de Resposta:**
```json
[
    {"id": 1, "name": "London", "country": "UK"},
    {"id": 2, "name": "New York", "country": "USA"}
]
