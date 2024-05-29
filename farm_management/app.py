from flask import Flask, render_template, request
from weather import get_weather_forecast

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resources')
def resources():
    resources_data = [
        {'name': 'Water', 'quantity': '200 liters'},
        {'name': 'Fertilizer', 'quantity': '50 kg'},
        {'name': 'Seeds', 'quantity': '100 packets'}
    ]
    return render_template('resources.html', resources=resources_data)

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

@app.route('/planning', methods=['GET', 'POST'])
def planning():
    if request.method == 'POST':
        # Obter dados do formulário
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        start = request.form.get('start')
        end = request.form.get('end')

        # Chamar a função para obter previsão do tempo
        weather_forecast = get_weather_forecast(lat, lon, start, end)
        
        if weather_forecast:
            return render_template('planning.html', weather=weather_forecast)
        else:
            error_message = "Could not retrieve weather data"
            return render_template('planning.html', error=error_message)
    else:
        return render_template('planning.html')

@app.route('/automation')
def automation():
    return render_template('automation.html')

if __name__ == '__main__':
    app.run(debug=True)
