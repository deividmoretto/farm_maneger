from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import os
from cities import CITIES

app = Flask(__name__)
api = Api(app)

# Configurações de cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Limitação de requisições
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Chave de API e URLs base da API de dados meteorológicos
API_KEY = os.getenv('WEATHER_API_KEY', 'your_openweathermap_api_key')
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'

class Cities(Resource):
    def get(self):
        return jsonify(CITIES)

class Weather(Resource):
    @limiter.limit("10 per minute")
    @cache.cached(timeout=300, query_string=True)
    def get(self):
        city_id = request.args.get('city_id')
        lang = request.args.get('lang', 'en')

        if not city_id:
            return jsonify({"error": "O parâmetro 'city_id' é obrigatório."}), 400

        city = next((c for c in CITIES if c['id'] == int(city_id)), None)
        if not city:
            return jsonify({"error": "Cidade não encontrada."}), 404

        response = requests.get(BASE_URL, params={
            'q': city['name'],
            'appid': API_KEY,
            'lang': lang,
            'units': 'metric'
        })

        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "location": data["name"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "weather": data["weather"][0]["description"]
            })
        else:
            return jsonify({"error": "Não foi possível obter os dados meteorológicos"}), 500

class Forecast(Resource):
    @limiter.limit("10 per minute")
    @cache.cached(timeout=600, query_string=True)
    def get(self):
        city_id = request.args.get('city_id')
        lang = request.args.get('lang', 'en')

        if not city_id:
            return jsonify({"error": "O parâmetro 'city_id' é obrigatório."}), 400

        city = next((c for c in CITIES if c['id'] == int(city_id)), None)
        if not city:
            return jsonify({"error": "Cidade não encontrada."}), 404

        response = requests.get(FORECAST_URL, params={
            'q': city['name'],
            'appid': API_KEY,
            'lang': lang,
            'units': 'metric'
        })

        if response.status_code == 200:
            data = response.json()
            forecasts = []
            for forecast in data['list']:
                forecasts.append({
                    "datetime": forecast['dt_txt'],
                    "temperature": forecast['main']['temp'],
                    "weather": forecast['weather'][0]['description']
                })
            return jsonify(forecasts)
        else:
            return jsonify({"error": "Não foi possível obter os dados da previsão"}), 500

# Registro dos recursos
api.add_resource(Cities, '/cities')
api.add_resource(Weather, '/weather')
api.add_resource(Forecast, '/forecast')

if __name__ == '__main__':
    app.run(debug=True)
