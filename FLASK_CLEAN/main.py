from flask import Flask, render_template

# Cria uma instância da aplicação Flask
app = Flask(__name__)

@app.route('/')
def home():
    """
    Rota para a página inicial da aplicação.

    Returns:
        str: O conteúdo do template 'base.html'.
    """
    return render_template('base.html')

@app.route('/sensor')
def sensor_data():
    """
    Rota para a página de dados do sensor.

    Returns:
        str: O conteúdo do template 'sensor_data.html'.
    """
    return render_template('sensor_data.html')

@app.route('/index')
def index_page():
    """
    Rota para a página de índice da aplicação.

    Returns:
        str: O conteúdo do template 'index.html'.
    """
    return render_template('index.html')

if __name__ == '__main__':
    """
    Executa a aplicação Flask em modo de depuração se o script for executado diretamente.
    """
    app.run(debug=True)
