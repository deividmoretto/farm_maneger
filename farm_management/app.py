from flask import Flask, render_template, request
from weather import get_weather_forecast

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recursos')
def recursos():
    recursos_data = [
        {'name': 'Água', 'quantity': '200 litros'},
        {'name': 'Fertilizante', 'quantity': '50 kg'},
        {'name': 'Sementes', 'quantity': '100 pacotes'}
    ]
    return render_template('recursos.html', recursos=recursos_data)

@app.route('/monitoramento')
def monitoramento():
    return render_template('monitoramento.html')

@app.route('/planejamento', methods=['GET', 'POST'])
def planejamento():
    if request.method == 'POST':
        # Obter dados do formulário
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        start = request.form.get('start')
        end = request.form.get('end')

        # Chamar a função para obter previsão do tempo
        weather_forecast = get_weather_forecast(lat, lon, start, end)
        
        if weather_forecast:
            return render_template('planejamento.html', weather=weather_forecast)
        else:
            error_message = "Não foi possível obter os dados do tempo"
            return render_template('planejamento.html', error=error_message)
    else:
        return render_template('planejamento.html')

@app.route('/automacao')
def automacao():
    return render_template('automacao.html')

if __name__ == '__main__':
    app.run(debug=True)
