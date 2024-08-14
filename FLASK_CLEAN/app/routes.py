from flask import Blueprint, render_template, redirect, url_for
from .models import Crop, User
from .forms import AddCropForm
from . import db
from .utils import get_sensor_data  # Importe a função utilitária para obter dados do sensor

# Cria um blueprint chamado 'main' para agrupar rotas relacionadas
main = Blueprint('main', __name__)

# Rota principal da aplicação, associada à URL raiz
@main.route('/')
def home():
    """
    Exibe a página inicial da aplicação, listando todas as culturas registradas.

    Retorna:
        Um template HTML chamado 'index.html' com uma lista de culturas passadas como contexto.
    """
    # Consulta todas as culturas no banco de dados
    crops = Crop.query.all()
    # Renderiza o template 'index.html' com as culturas obtidas
    return render_template('index.html', crops=crops)

# Rota para adicionar uma nova cultura, aceita métodos GET e POST
@main.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    """
    Gerencia a adição de uma nova cultura ao banco de dados.

    Retorna:
        Se o formulário for validado e submetido, redireciona para a página inicial.
        Caso contrário, renderiza o template 'add_crop.html' com o formulário.
    """
    # Cria uma instância do formulário de adição de cultura
    form = AddCropForm()
    # Verifica se o formulário foi submetido e é válido
    if form.validate_on_submit():
        # Cria uma nova instância de Crop com os dados do formulário
        crop = Crop(name=form.name.data, description=form.description.data)
        # Adiciona a nova cultura à sessão do banco de dados
        db.session.add(crop)
        # Comita a transação no banco de dados para salvar a cultura
        db.session.commit()
        # Redireciona para a página inicial após adicionar a cultura
        return redirect(url_for('main.home'))
    # Renderiza o template 'add_crop.html' com o formulário para adicionar cultura
    return render_template('add_crop.html', form=form)

# Rota para exibir dados de sensores, como temperatura e umidade
@main.route('/sensor_data')
def sensor_data():
    """
    Obtém e exibe dados do sensor, como temperatura e umidade.

    Retorna:
        Um template HTML chamado 'sensor_data.html' com os dados do sensor.
    """
    # Obtém dados de temperatura e umidade utilizando a função utilitária
    temperature, humidity = get_sensor_data()
    # Renderiza o template 'sensor_data.html' com os dados do sensor
    return render_template('sensor_data.html', temperature=temperature, humidity=humidity)

# Função para registrar o blueprint na aplicação Flask
def init_app(app):
    """
    Inicializa a aplicação Flask com o blueprint principal.

    Args:
        app (Flask): Instância da aplicação Flask onde o blueprint será registrado.
    """
    # Registra o blueprint 'main' na aplicação
    app.register_blueprint(main)
