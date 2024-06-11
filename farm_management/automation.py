from flask import Flask, render_template, request
from weather import get_weather_forecast

app = Flask(__name__)

def control_tractor(operation):
    if operation == "planting":
        print("Trator está plantando.")
        return "Trator está plantando."
    elif operation == "harvesting":
        print("Trator está colhendo.")
        return "Trator está colhendo."
    else:
        print("Operação desconhecida.")
        return "Operação desconhecida."

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
    return render_template('recursos.html', resources=recursos_data)

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
            return render_template('planejamento.html', weather_forecast=weather_forecast)
        else:
            error_message = "Não foi possível obter os dados do tempo"
            return render_template('planejamento.html', error_message=error_message)
    else:
        return render_template('planejamento.html')

@app.route('/automacao', methods=['GET', 'POST'])
def automacao():
    if request.method == 'POST':
        operation = request.form.get('operation')
        result = control_tractor(operation)
        return render_template('automacao.html', result=result)
    return render_template('automacao.html')

if __name__ == '__main__':
    app.run(debug=True)
