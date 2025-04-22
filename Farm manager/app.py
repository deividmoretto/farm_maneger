from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    areas = db.relationship('Area', backref='owner', lazy=True)
    silos = db.relationship('Silo', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    polygon_points = db.Column(db.Text, nullable=True)  # Para armazenar os pontos do polígono como JSON
    crop_type = db.Column(db.String(100), nullable=True)  # Tipo de cultura plantada
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analyses = db.relationship('Analysis', backref='area', lazy=True)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    ph = db.Column(db.Float)
    phosphorus = db.Column(db.Float)  # Fósforo (P) - mg/dm³
    potassium = db.Column(db.Float)   # Potássio (K) - cmolc/dm³
    calcium = db.Column(db.Float)     # Cálcio (Ca) - cmolc/dm³
    magnesium = db.Column(db.Float)   # Magnésio (Mg) - cmolc/dm³
    aluminum = db.Column(db.Float, nullable=True)    # Alumínio (Al) - cmolc/dm³
    sulfur = db.Column(db.Float, nullable=True)      # Enxofre (S) - mg/dm³
    organic_matter = db.Column(db.Float, nullable=True)  # Matéria Orgânica (%)
    cation_exchange = db.Column(db.Float, nullable=True) # CTC - cmolc/dm³
    base_saturation = db.Column(db.Float, nullable=True) # Saturação por Bases (%)
    notes = db.Column(db.Text, nullable=True)        # Observações

class Silo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Float, nullable=False)   # Capacidade em toneladas
    location = db.Column(db.String(200))
    type = db.Column(db.String(50))                  # Tipo: Metálico, Concreto, Bolsa, etc.
    diameter = db.Column(db.Float, nullable=True)    # Diâmetro em metros
    height = db.Column(db.Float, nullable=True)      # Altura em metros
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    armazenamentos = db.relationship('Armazenamento', backref='silo', lazy=True)

class Armazenamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    silo_id = db.Column(db.Integer, db.ForeignKey('silo.id'), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False) # Tipo de grão
    quantity = db.Column(db.Float, nullable=False)      # Quantidade em toneladas
    humidity = db.Column(db.Float, nullable=True)       # Umidade %
    impurity = db.Column(db.Float, nullable=True)       # Impureza %
    entry_date = db.Column(db.DateTime, nullable=False)
    exit_date = db.Column(db.DateTime, nullable=True)   # Data de saída (se já foi retirado)
    price_per_ton = db.Column(db.Float, nullable=True)  # Preço por tonelada
    notes = db.Column(db.Text, nullable=True)          # Observações

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Formulário para a calculadora de solo
class SoilCalculatorForm(FlaskForm):
    ph = FloatField('pH', validators=[DataRequired(), NumberRange(min=3.0, max=9.0)], default=5.5)
    fosforo = FloatField('Fósforo (P) mg/dm³', validators=[DataRequired(), NumberRange(min=0)], default=10.0)
    potassio = FloatField('Potássio (K) cmolc/dm³', validators=[DataRequired(), NumberRange(min=0)], default=0.15)
    calcio = FloatField('Cálcio (Ca) cmolc/dm³', validators=[DataRequired(), NumberRange(min=0)], default=2.0)
    magnesio = FloatField('Magnésio (Mg) cmolc/dm³', validators=[DataRequired(), NumberRange(min=0)], default=0.8)
    aluminio = FloatField('Alumínio (Al) cmolc/dm³', validators=[NumberRange(min=0)], default=0.0)
    hidrogenio = FloatField('Hidrogênio + Al (H+Al) cmolc/dm³', validators=[NumberRange(min=0)], default=3.0)
    tipo_solo = SelectField('Tipo de Solo', choices=[
        ('arenoso', 'Arenoso'), 
        ('medio', 'Textura Média'), 
        ('argiloso', 'Argiloso')
    ], default='medio')
    prnt = FloatField('PRNT do Calcário (%)', validators=[NumberRange(min=0, max=100)], default=85.0)
    v_desejado = FloatField('Saturação por Bases Desejada (V%)', validators=[NumberRange(min=0, max=100)], default=70.0)
    cultura = SelectField('Cultura', choices=[
        ('milho', 'Milho'),
        ('soja', 'Soja'),
        ('cafe', 'Café'),
        ('frutas', 'Fruticultura'),
        ('hortalicas', 'Hortaliças'),
        ('pastagem', 'Pastagem'),
        ('outros', 'Outros')
    ], default='soja')
    area = FloatField('Área (hectares)', validators=[NumberRange(min=0)], default=1.0)
    submit = SubmitField('Calcular')

# Funções para a calculadora de solo
def calculate_ctc(ca, mg, k, h_al):
    """Calcula a CTC do solo"""
    return ca + mg + k + h_al

def calculate_base_saturation(ca, mg, k, ctc):
    """Calcula a saturação por bases (V%)"""
    sum_bases = ca + mg + k
    if ctc > 0:
        v_percent = (sum_bases / ctc) * 100
        return v_percent
    return 0

def calculate_aluminum_saturation(al, ca, mg, k):
    """Calcula a saturação por alumínio (m%)"""
    if al > 0 and (ca + mg + k + al) > 0:
        m_percent = (al / (ca + mg + k + al)) * 100
        return m_percent
    return 0

def calculate_lime_need(ctc, v_atual, v_desejado, prnt=100):
    """Calcula necessidade de calagem pelo método da saturação por bases"""
    if v_atual >= v_desejado:
        return 0
    
    # Fórmula: NC = (V2 - V1) * CTC / (10 * PRNT/100)
    nc = (v_desejado - v_atual) * ctc / (10 * prnt/100)
    return nc

def get_interpretation(value, parameter):
    """Obter interpretação textual para os valores do solo"""
    if parameter == 'ph':
        if value < 4.5:
            return "Muito Ácido"
        elif value < 5.5:
            return "Ácido"
        elif value < 6.5:
            return "Adequado"
        elif value < 7.5:
            return "Neutro"
        else:
            return "Alcalino"
    
    elif parameter == 'phosphorus':
        if value < 5.0:
            return "Muito Baixo"
        elif value < 10.0:
            return "Baixo"
        elif value < 15.0:
            return "Médio"
        elif value < 30.0:
            return "Bom"
        else:
            return "Muito Bom"
    
    elif parameter == 'potassium':
        if value < 0.08:
            return "Muito Baixo"
        elif value < 0.15:
            return "Baixo"
        elif value < 0.25:
            return "Médio"
        elif value < 0.40:
            return "Bom"
        else:
            return "Muito Bom"
    
    elif parameter == 'calcium':
        if value < 1.0:
            return "Muito Baixo"
        elif value < 2.0:
            return "Baixo"
        elif value < 4.0:
            return "Médio"
        elif value < 7.0:
            return "Bom"
        else:
            return "Muito Bom"
    
    elif parameter == 'magnesium':
        if value < 0.4:
            return "Muito Baixo"
        elif value < 0.8:
            return "Baixo"
        elif value < 1.5:
            return "Médio"
        elif value < 3.0:
            return "Bom"
        else:
            return "Muito Bom"
    
    return "Indeterminado"

def evaluate_soil(form_data):
    """Avalia os parâmetros do solo e calcula as recomendações"""
    # Extrair valores do formulário
    ph = form_data.get('ph')
    phosphorus = form_data.get('fosforo')
    potassium = form_data.get('potassio')
    calcium = form_data.get('calcio')
    magnesium = form_data.get('magnesio')
    aluminum = form_data.get('aluminio')
    h_al = form_data.get('hidrogenio')
    soil_type = form_data.get('tipo_solo')
    prnt = form_data.get('prnt')
    v_desejado = form_data.get('v_desejado')
    cultura = form_data.get('cultura')
    area = form_data.get('area')
    
    # Cálculos
    ctc = calculate_ctc(calcium, magnesium, potassium, h_al)
    v_atual = calculate_base_saturation(calcium, magnesium, potassium, ctc)
    m = calculate_aluminum_saturation(aluminum, calcium, magnesium, potassium)
    
    # Cálculo da necessidade de calagem
    nc = calculate_lime_need(ctc, v_atual, v_desejado, prnt)
    
    # Cálculo da relação Ca/Mg
    ca_mg_ratio = calcium / magnesium if magnesium > 0 else 0
    
    # Interpretações
    interpretacao_ph = get_interpretation(ph, 'ph')
    interpretacao_p = get_interpretation(phosphorus, 'phosphorus')
    interpretacao_k = get_interpretation(potassium, 'potassium')
    interpretacao_ca = get_interpretation(calcium, 'calcium')
    interpretacao_mg = get_interpretation(magnesium, 'magnesium')
    
    # Resultados
    resultados = {
        'ctc': round(ctc, 2),
        'v': round(v_atual, 2),
        'm': round(m, 2),
        'relacao_ca_mg': round(ca_mg_ratio, 2),
        'nc': round(nc, 2),
        'prnt': prnt,
        'v_desejado': v_desejado,
        'cultura': cultura,
        'area': area,
        'interpretacao_ph': interpretacao_ph,
        'interpretacao_p': interpretacao_p,
        'interpretacao_k': interpretacao_k,
        'interpretacao_ca': interpretacao_ca,
        'interpretacao_mg': interpretacao_mg
    }
    
    return resultados

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user_public():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Verificar se usuário já existe
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Erro - Criar Usuário</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }}
                        .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                        h2 {{ color: #d9534f; }}
                        .btn {{ display: inline-block; padding: 8px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Erro ao criar usuário</h2>
                        <p>Usuário <strong>{username}</strong> já existe no sistema.</p>
                        <p><a href="/login" class="btn">Ir para login</a> <a href="/create_user" class="btn">Tentar novamente</a></p>
                    </div>
                </body>
                </html>
                """
            
            # Criar novo usuário
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Usuário Criado</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }}
                    .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                    h2 {{ color: #28a745; }}
                    .user-info {{ background-color: #e9f7ef; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .btn {{ display: inline-block; padding: 8px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Usuário criado com sucesso!</h2>
                    <div class="user-info">
                        <p><strong>Nome de usuário:</strong> {username}</p>
                        <p><strong>Email:</strong> {email}</p>
                    </div>
                    <p>Agora você pode fazer login com essas credenciais.</p>
                    <p><a href="/login" class="btn">Ir para login</a></p>
                </div>
            </body>
            </html>
            """
        except Exception as e:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Erro - Criar Usuário</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }}
                    .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                    h2 {{ color: #d9534f; }}
                    .error {{ background-color: #f8d7da; padding: 10px; border-radius: 5px; }}
                    .btn {{ display: inline-block; padding: 8px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Erro ao criar usuário</h2>
                    <div class="error">
                        <p>Ocorreu um erro: {str(e)}</p>
                    </div>
                    <p><a href="/create_user" class="btn">Tentar novamente</a></p>
                </div>
            </body>
            </html>
            """
    
    # Método GET - mostrar formulário
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Criar Novo Usuário</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h2 { color: #333; text-align: center; margin-bottom: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], input[type="email"], input[type="password"] { 
                width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; 
            }
            button { 
                background-color: #28a745; color: white; border: none; padding: 10px 15px; 
                border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; 
            }
            button:hover { background-color: #218838; }
            .footer { text-align: center; margin-top: 15px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Criar Novo Usuário</h2>
            <form method="POST" action="/create_user">
                <div class="form-group">
                    <label for="username">Nome de usuário:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="email">E-mail:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Senha:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit">Criar Usuário</button>
            </form>
            
            <div class="footer">
                <p>Já tem uma conta? <a href="/login">Faça login</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/create_user/<username>/<email>/<password>')
def create_user_direct(username, email, password):
    try:
        # Verificar se usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return f"""
            <h2>Erro ao criar usuário</h2>
            <p>Usuário {username} já existe no sistema.</p>
            <p><a href="/login">Ir para login</a></p>
            """
        
        # Criar novo usuário
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return f"""
        <h2>Usuário criado com sucesso!</h2>
        <p>Username: {username}</p>
        <p>Email: {email}</p>
        <p>Agora você pode fazer <a href="/login">login</a> com essas credenciais.</p>
        """
    except Exception as e:
        return f"""
        <h2>Erro ao criar usuário</h2>
        <p>Ocorreu um erro: {str(e)}</p>
        """

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/areas')
@login_required
def areas():
    user_areas = Area.query.filter_by(user_id=current_user.id).all()
    return render_template('areas/listar_areas.html', areas=user_areas)

@app.route('/excluir_area/<int:id>', methods=['POST'])
@login_required
def excluir_area(id):
    area = Area.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(area)
    db.session.commit()
    flash('Área excluída com sucesso!', 'success')
    return redirect(url_for('areas'))

@app.route('/nova_area', methods=['GET', 'POST'])
@login_required
def nova_area():
    if request.method == 'POST':
        # Capturar e converter latitude e longitude
        latitude = None
        longitude = None
        if request.form.get('latitude') and request.form.get('longitude'):
            try:
                latitude = float(request.form.get('latitude'))
                longitude = float(request.form.get('longitude'))
            except ValueError:
                pass
                
        # Capturar os pontos do polígono
        polygon_points = request.form.get('polygon_points')
                
        area = Area(
            name=request.form.get('name'),
            size=float(request.form.get('size')),
            location=request.form.get('location'),
            latitude=latitude,
            longitude=longitude,
            polygon_points=polygon_points,
            crop_type=request.form.get('crop_type'),
            user_id=current_user.id
        )
        db.session.add(area)
        db.session.commit()
        flash('Área cadastrada com sucesso!', 'success')
        return redirect(url_for('areas'))
    
    return render_template('areas/nova_area_simple.html')

@app.route('/analises')
@login_required
def analises():
    areas = Area.query.filter_by(user_id=current_user.id).all()
    analyses = []
    for area in areas:
        analyses.extend(area.analyses)
    
    # Verificar se há análises com matéria orgânica ou saturação de bases
    any_organic_matter = any(analysis.organic_matter is not None for analysis in analyses)
    any_base_saturation = any(analysis.base_saturation is not None for analysis in analyses)
    
    # Obter dados para gráficos
    datas = [analise.date.strftime('%d/%m/%Y') for analise in analyses]
    valores_ph = [analise.ph for analise in analyses]
    valores_p = [analise.phosphorus for analise in analyses]
    valores_k = [analise.potassium for analise in analyses]
    valores_ca = [analise.calcium for analise in analyses]
    valores_mg = [analise.magnesium for analise in analyses]
    
    # Verificar se há dados da calculadora na sessão
    resultados_calculadora = session.get('resultados_calculadora')
    if resultados_calculadora:
        session.pop('resultados_calculadora')  # Limpar da sessão após uso
    
    # Coletar valores opcionais
    if analyses:
        organic_matter_values = [float(analise.organic_matter) if analise.organic_matter is not None else None for analise in analyses]
        base_saturation_values = [float(analise.base_saturation) if analise.base_saturation is not None else None for analise in analyses]
    else:
        organic_matter_values = []
        base_saturation_values = []
    
    return render_template('analises.html', 
                          analyses=analyses, 
                          resultados_calculadora=resultados_calculadora,
                          datas=datas,
                          valores_ph=valores_ph,
                          valores_p=valores_p,
                          valores_k=valores_k,
                          valores_ca=valores_ca,
                          valores_mg=valores_mg,
                          organic_matter_values=organic_matter_values,
                          base_saturation_values=base_saturation_values,
                          any_organic_matter=any_organic_matter, 
                          any_base_saturation=any_base_saturation)

@app.route('/nova_analise', methods=['GET', 'POST'])
@login_required
def nova_analise():
    if request.method == 'POST':
        # Processar parâmetros obrigatórios
        analysis = Analysis(
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            area_id=request.form.get('area_id'),
            ph=float(request.form.get('ph')),
            phosphorus=float(request.form.get('phosphorus')),
            potassium=float(request.form.get('potassium')),
            calcium=float(request.form.get('calcium')),
            magnesium=float(request.form.get('magnesium'))
        )
        
        # Processar parâmetros opcionais
        if request.form.get('aluminum'):
            analysis.aluminum = float(request.form.get('aluminum'))
        if request.form.get('sulfur'):
            analysis.sulfur = float(request.form.get('sulfur'))
        if request.form.get('organic_matter'):
            analysis.organic_matter = float(request.form.get('organic_matter'))
            
        db.session.add(analysis)
        db.session.commit()
        flash('Análise de solo cadastrada com sucesso!', 'success')
        return redirect(url_for('analises'))
    areas = Area.query.filter_by(user_id=current_user.id).all()
    return render_template('analises/nova_analise.html', areas=areas, now=datetime.now())

@app.route('/calculadora', methods=['GET', 'POST'])
@login_required
def calculadora():
    form = SoilCalculatorForm()
    resultados = None
    
    if request.method == 'POST' and form.validate_on_submit():
        # Obter dados do formulário
        form_data = {
            'ph': form.ph.data,
            'fosforo': form.fosforo.data,
            'potassio': form.potassio.data,
            'calcio': form.calcio.data,
            'magnesio': form.magnesio.data,
            'aluminio': form.aluminio.data,
            'hidrogenio': form.hidrogenio.data,
            'tipo_solo': form.tipo_solo.data,
            'prnt': form.prnt.data,
            'v_desejado': form.v_desejado.data,
            'cultura': form.cultura.data,
            'area': form.area.data
        }
        
        # Avaliar solo
        resultados = evaluate_soil(form_data)
        
        # Se o usuário escolheu salvar, armazenar na sessão para exibir na página de análises
        if 'salvar' in request.form:
            session['resultados_calculadora'] = resultados
            return redirect(url_for('analises'))
    
    return render_template('soil_calculator.html', form=form, resultados=resultados)

@app.route('/salvar_calculo', methods=['POST'])
@login_required
def salvar_calculo():
    """Salvar os resultados da calculadora como uma análise de solo"""
    try:
        # Obter dados do formulário
        area_id = request.form.get('area_id')
        ph = float(request.form.get('ph'))
        phosphorus = float(request.form.get('fosforo'))
        potassium = float(request.form.get('potassio'))
        calcium = float(request.form.get('calcio'))
        magnesium = float(request.form.get('magnesio'))
        
        # Verificar se a área existe
        area = Area.query.filter_by(id=area_id, user_id=current_user.id).first()
        if not area:
            flash('Área não encontrada.', 'danger')
            return redirect(url_for('analises'))
        
        # Criar nova análise
        analysis = Analysis(
            date=datetime.now(),
            area_id=area_id,
            ph=ph,
            phosphorus=phosphorus,
            potassium=potassium,
            calcium=calcium,
            magnesium=magnesium
        )
        
        # Adicionar campos opcionais se disponíveis
        if request.form.get('aluminio'):
            analysis.aluminum = float(request.form.get('aluminio'))
        if request.form.get('enxofre'):
            analysis.sulfur = float(request.form.get('enxofre'))
        if request.form.get('materia_organica'):
            analysis.organic_matter = float(request.form.get('materia_organica'))
        
        db.session.add(analysis)
        db.session.commit()
        
        flash('Resultado da calculadora salvo como análise com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao salvar análise: {str(e)}', 'danger')
    
    return redirect(url_for('analises'))

@app.route('/precos')
def precos():
    return render_template('precos.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_users():
    # Verificar se o usuário atual é administrador
    if not current_user.is_admin:
        flash('Acesso negado: você não tem permissões de administrador.', 'danger')
        return redirect(url_for('index'))
    
    # Processar ações do formulário
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Criar novo usuário
        if action == 'create':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            is_admin = 'is_admin' in request.form
            
            # Verificar se usuário já existe
            if User.query.filter_by(username=username).first():
                flash(f'Usuário {username} já existe.', 'danger')
                return redirect(url_for('admin_users'))
            
            # Criar novo usuário
            user = User(username=username, email=email, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'Usuário {username} criado com sucesso.', 'success')
        
        # Editar usuário existente
        elif action == 'edit':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            
            if user:
                # Atualizar campos
                user.username = request.form.get('username')
                user.email = request.form.get('email')
                user.is_admin = 'is_admin' in request.form
                
                # Atualizar senha se fornecida
                password = request.form.get('password')
                if password:
                    user.set_password(password)
                
                db.session.commit()
                flash(f'Usuário {user.username} atualizado com sucesso.', 'success')
        
        # Excluir usuário
        elif action == 'delete':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            
            if user:
                username = user.username
                
                # Não permitir que um usuário exclua a si mesmo
                if user.id == current_user.id:
                    flash('Você não pode excluir seu próprio usuário.', 'danger')
                else:
                    db.session.delete(user)
                    db.session.commit()
                    flash(f'Usuário {username} excluído com sucesso.', 'success')
        
        return redirect(url_for('admin_users'))
    
    # Obter todos os usuários do sistema
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# Rota para silos
@app.route('/silos')
@login_required
def silos():
    silos = Silo.query.filter_by(user_id=current_user.id).all()
    
    # Calcular estatísticas
    total_silos = len(silos)
    total_capacidade = sum(silo.capacity for silo in silos)
    capacidade_utilizada = 0
    total_armazenado = 0
    
    silos_info = []
    tipos_graos = {}
    
    for silo in silos:
        # Filtrar apenas armazenamentos ativos (sem data de saída)
        armazenamentos_ativos = [a for a in silo.armazenamentos if a.exit_date is None]
        
        # Calcular ocupação atual
        ocupacao = sum(a.quantity for a in armazenamentos_ativos)
        percentual = (ocupacao / silo.capacity * 100) if silo.capacity > 0 else 0
        
        # Somar ao total
        total_armazenado += ocupacao
        
        # Contar grãos por tipo
        for armazenamento in armazenamentos_ativos:
            if armazenamento.crop_type in tipos_graos:
                tipos_graos[armazenamento.crop_type] += armazenamento.quantity
            else:
                tipos_graos[armazenamento.crop_type] = armazenamento.quantity
        
        # Adicionar informações para a tabela
        silos_info.append({
            'silo': silo,
            'ocupacao': ocupacao,
            'percentual': percentual,
            'armazenamentos': armazenamentos_ativos
        })
    
    # Calcular percentual total de utilização
    if total_capacidade > 0:
        capacidade_utilizada = (total_armazenado / total_capacidade) * 100
    
    return render_template('silos/listar_silos.html', 
                          silos=silos,
                          silos_info=silos_info,
                          total_silos=total_silos,
                          total_capacidade=total_capacidade,
                          total_armazenado=total_armazenado,
                          capacidade_utilizada=capacidade_utilizada,
                          tipos_graos=tipos_graos)

@app.route('/silos/novo', methods=['GET', 'POST'])
@login_required
def novo_silo():
    if request.method == 'POST':
        try:
            nome = request.form.get('name')
            capacidade = float(request.form.get('capacity'))
            local = request.form.get('location')
            tipo = request.form.get('type')
            
            # Campos opcionais
            diametro = None
            altura = None
            descricao = request.form.get('description', '')
            
            if request.form.get('diameter'):
                diametro = float(request.form.get('diameter'))
            
            if request.form.get('height'):
                altura = float(request.form.get('height'))
            
            # Criar novo silo
            silo = Silo(
                name=nome,
                capacity=capacidade,
                location=local,
                type=tipo,
                diameter=diametro,
                height=altura,
                description=descricao,
                user_id=current_user.id
            )
            
            db.session.add(silo)
            db.session.commit()
            
            flash(f'Silo "{nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('silos'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar silo: {str(e)}', 'danger')
    
    return render_template('silos/novo_silo.html')

@app.route('/silos/<int:id>')
@login_required
def detalhes_silo(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Filtrar apenas armazenamentos ativos (sem data de saída)
    armazenamentos_ativos = [a for a in silo.armazenamentos if a.exit_date is None]
    armazenamentos_finalizados = [a for a in silo.armazenamentos if a.exit_date is not None]
    
    # Calcular ocupação atual
    ocupacao = sum(a.quantity for a in armazenamentos_ativos)
    percentual = (ocupacao / silo.capacity * 100) if silo.capacity > 0 else 0
    
    # Calcular informações de tipos de grãos
    tipos_graos = {}
    for armazenamento in armazenamentos_ativos:
        if armazenamento.crop_type in tipos_graos:
            tipos_graos[armazenamento.crop_type] += armazenamento.quantity
        else:
            tipos_graos[armazenamento.crop_type] = armazenamento.quantity
    
    return render_template('silos/detalhes_silo.html', 
                          silo=silo,
                          ocupacao=ocupacao,
                          percentual=percentual,
                          armazenamentos_ativos=armazenamentos_ativos,
                          armazenamentos_finalizados=armazenamentos_finalizados,
                          tipos_graos=tipos_graos)

@app.route('/silos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_silo(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Verificar se existem armazenamentos ativos
    armazenamentos_ativos = [a for a in silo.armazenamentos if a.exit_date is None]
    if armazenamentos_ativos:
        flash('Não é possível excluir o silo pois há armazenamentos ativos.', 'danger')
        return redirect(url_for('detalhes_silo', id=id))
    
    # Remover todos os armazenamentos antigos
    for armazenamento in silo.armazenamentos:
        db.session.delete(armazenamento)
    
    # Remover o silo
    nome_silo = silo.name
    db.session.delete(silo)
    db.session.commit()
    
    flash(f'Silo "{nome_silo}" excluído com sucesso!', 'success')
    return redirect(url_for('silos'))

@app.route('/silos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_silo(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            silo.name = request.form.get('name')
            silo.capacity = float(request.form.get('capacity'))
            silo.location = request.form.get('location')
            silo.type = request.form.get('type')
            silo.description = request.form.get('description', '')
            
            # Campos opcionais
            if request.form.get('diameter'):
                silo.diameter = float(request.form.get('diameter'))
            else:
                silo.diameter = None
                
            if request.form.get('height'):
                silo.height = float(request.form.get('height'))
            else:
                silo.height = None
            
            db.session.commit()
            flash(f'Silo "{silo.name}" atualizado com sucesso!', 'success')
            return redirect(url_for('detalhes_silo', id=id))
            
        except Exception as e:
            flash(f'Erro ao atualizar silo: {str(e)}', 'danger')
    
    return render_template('silos/novo_silo.html', silo=silo, edit_mode=True)

@app.route('/silos/<int:id>/armazenar', methods=['GET', 'POST'])
@login_required
def novo_armazenamento(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Verificar ocupação atual do silo
    armazenamentos_ativos = [a for a in silo.armazenamentos if a.exit_date is None]
    ocupacao_atual = sum(a.quantity for a in armazenamentos_ativos)
    
    if request.method == 'POST':
        try:
            quantidade = float(request.form.get('quantity'))
            tipo_grao = request.form.get('crop_type')
            
            # Verificar se há espaço suficiente
            if ocupacao_atual + quantidade > silo.capacity:
                flash('A quantidade excede a capacidade disponível do silo!', 'danger')
                return redirect(url_for('novo_armazenamento', id=id))
            
            # Processar campos de data
            data_entrada = datetime.strptime(request.form.get('entry_date'), '%Y-%m-%d')
            
            # Campos opcionais
            umidade = None
            impureza = None
            preco = None
            observacoes = request.form.get('notes', '')
            
            if request.form.get('humidity'):
                umidade = float(request.form.get('humidity'))
                
            if request.form.get('impurity'):
                impureza = float(request.form.get('impurity'))
                
            if request.form.get('price_per_ton'):
                preco = float(request.form.get('price_per_ton'))
            
            # Criar novo armazenamento
            armazenamento = Armazenamento(
                silo_id=silo.id,
                crop_type=tipo_grao,
                quantity=quantidade,
                humidity=umidade,
                impurity=impureza,
                entry_date=data_entrada,
                price_per_ton=preco,
                notes=observacoes
            )
            
            db.session.add(armazenamento)
            db.session.commit()
            
            flash(f'Armazenamento de {quantidade} toneladas de {tipo_grao} registrado com sucesso!', 'success')
            return redirect(url_for('detalhes_silo', id=id))
            
        except Exception as e:
            flash(f'Erro ao registrar armazenamento: {str(e)}', 'danger')
    
    # Calcular espaço disponível
    espaco_disponivel = silo.capacity - ocupacao_atual
    
    return render_template('silos/novo_armazenamento.html', 
                          silo=silo, 
                          ocupacao_atual=ocupacao_atual, 
                          espaco_disponivel=espaco_disponivel)

@app.route('/armazenamentos/<int:id>')
@login_required
def detalhes_armazenamento(id):
    armazenamento = Armazenamento.query.join(Silo).filter(
        Armazenamento.id == id,
        Silo.user_id == current_user.id
    ).first_or_404()
    
    silo = armazenamento.silo
    
    # Calcular valor total
    valor_total = None
    if armazenamento.price_per_ton:
        valor_total = armazenamento.price_per_ton * armazenamento.quantity
    
    return render_template('silos/detalhes_armazenamento.html', 
                          armazenamento=armazenamento,
                          silo=silo,
                          valor_total=valor_total)

@app.route('/armazenamentos/<int:id>/finalizar', methods=['POST'])
@login_required
def finalizar_armazenamento(id):
    armazenamento = Armazenamento.query.join(Silo).filter(
        Armazenamento.id == id,
        Silo.user_id == current_user.id
    ).first_or_404()
    
    # Verificar se já está finalizado
    if armazenamento.exit_date:
        flash('Este armazenamento já foi finalizado.', 'warning')
        return redirect(url_for('detalhes_armazenamento', id=id))
    
    # Registrar data de saída
    armazenamento.exit_date = datetime.now()
    db.session.commit()
    
    flash('Armazenamento finalizado com sucesso!', 'success')
    return redirect(url_for('detalhes_silo', id=armazenamento.silo_id))

@app.route('/armazenamentos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_armazenamento(id):
    armazenamento = Armazenamento.query.join(Silo).filter(
        Armazenamento.id == id,
        Silo.user_id == current_user.id
    ).first_or_404()
    
    silo_id = armazenamento.silo_id
    db.session.delete(armazenamento)
    db.session.commit()
    
    flash('Armazenamento excluído com sucesso!', 'success')
    return redirect(url_for('detalhes_silo', id=silo_id))

@app.context_processor
def inject_blueprint_url():
    return {
        'areas_url': lambda: url_for('areas'),
        'analises_url': lambda: url_for('analises'),
        'silos_url': lambda: url_for('silos')
    }

@app.context_processor
def inject_crop_helpers():
    crop_names = {
        'soja': 'Soja',
        'milho': 'Milho',
        'cana': 'Cana-de-açúcar',
        'cafe': 'Café',
        'algodao': 'Algodão',
        'feijao': 'Feijão',
        'arroz': 'Arroz',
        'trigo': 'Trigo',
        'pastagem': 'Pastagem',
        'outros': 'Outros'
    }
    
    crop_colors = {
        'soja': '#8BC34A',
        'milho': '#FFEB3B',
        'cana': '#4CAF50',
        'cafe': '#795548',
        'algodao': '#FFFFFF',
        'feijao': '#9C27B0',
        'arroz': '#03A9F4',
        'trigo': '#FFC107',
        'pastagem': '#00BCD4',
        'outros': '#9E9E9E'
    }
    
    def get_crop_name(crop_type):
        return crop_names.get(crop_type, 'Outros')
    
    def get_crop_color(crop_type):
        return crop_colors.get(crop_type, '#9E9E9E')
    
    return {
        'get_crop_name': get_crop_name,
        'get_crop_color': get_crop_color
    }

@app.context_processor
def inject_grain_helpers():
    grain_names = {
        'soja': 'Soja',
        'milho': 'Milho',
        'trigo': 'Trigo',
        'arroz': 'Arroz',
        'feijao': 'Feijão',
        'sorgo': 'Sorgo',
        'aveia': 'Aveia',
        'cevada': 'Cevada',
        'girassol': 'Girassol',
        'outros': 'Outros'
    }
    
    grain_colors = {
        'soja': '#8BC34A',  # Verde claro
        'milho': '#FFEB3B',  # Amarelo
        'trigo': '#FFC107',  # Âmbar
        'arroz': '#E0E0E0',  # Cinza claro
        'feijao': '#9C27B0',  # Roxo
        'sorgo': '#F44336',  # Vermelho
        'aveia': '#BDBDBD',  # Cinza
        'cevada': '#D7CCC8',  # Marrom claro
        'girassol': '#FFEB3B',  # Amarelo
        'outros': '#9E9E9E'   # Cinza médio
    }
    
    # Tipos de silos e suas cores
    silo_types = {
        'metalico': 'Metálico',
        'concreto': 'Concreto',
        'bolsa': 'Silo-bolsa',
        'aerado': 'Aerado',
        'vertical': 'Vertical',
        'horizontal': 'Horizontal',
        'outros': 'Outros'
    }
    
    silo_colors = {
        'metalico': '#B0BEC5',  # Azul acinzentado
        'concreto': '#78909C',  # Cinza azulado
        'bolsa': '#FFFFFF',     # Branco
        'aerado': '#CFD8DC',    # Cinza claro
        'vertical': '#90A4AE',  # Azul acinzentado médio
        'horizontal': '#607D8B', # Azul acinzentado escuro
        'outros': '#455A64'     # Azul acinzentado muito escuro
    }
    
    def get_grain_name(grain_type):
        return grain_names.get(grain_type, 'Outros')
    
    def get_grain_color(grain_type):
        return grain_colors.get(grain_type, '#9E9E9E')
    
    def get_silo_type_name(silo_type):
        return silo_types.get(silo_type, 'Outros')
    
    def get_silo_color(silo_type):
        return silo_colors.get(silo_type, '#9E9E9E')
    
    return {
        'get_grain_name': get_grain_name,
        'get_grain_color': get_grain_color,
        'get_silo_type_name': get_silo_type_name,
        'get_silo_color': get_silo_color,
        'grain_types': list(grain_names.items()),
        'silo_types': list(silo_types.items())
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 