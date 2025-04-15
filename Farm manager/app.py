from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
from flask import Blueprint

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
    
    return render_template('analises.html', 
                          analyses=analyses, 
                          resultados_calculadora=resultados_calculadora,
                          datas=datas,
                          valores_ph=valores_ph,
                          valores_p=valores_p,
                          valores_k=valores_k,
                          valores_ca=valores_ca,
                          valores_mg=valores_mg)

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

@app.context_processor
def inject_blueprint_url():
    return {
        'areas_url': lambda: url_for('areas.listar_areas'),
        'analises_url': lambda: url_for('analises.listar_analises')
    }

# Adicionar funções para lidar com culturas nos templates
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

# Verificar se analises_bp está definido, caso contrário, definir
try:
    analises_bp
except NameError:
    analises_bp = Blueprint('analises', __name__)

@analises_bp.route('/analises')
def listar_analises():
    analyses = Analysis.query.order_by(Analysis.date).all()
    
    # Verificar se há análises com matéria orgânica ou saturação de bases
    any_organic_matter = any(analysis.organic_matter is not None for analysis in analyses)
    any_base_saturation = any(analysis.base_saturation is not None for analysis in analyses)
    
    # Preparar dados para o gráfico
    if len(analyses) > 1:
        dates = [analysis.date.strftime('%d/%m/%Y') for analysis in analyses]
        ph_values = [float(analysis.ph) for analysis in analyses]
        phosphorus_values = [float(analysis.phosphorus) for analysis in analyses]
        potassium_values = [float(analysis.potassium) for analysis in analyses]
        calcium_values = [float(analysis.calcium) for analysis in analyses]
        magnesium_values = [float(analysis.magnesium) for analysis in analyses]
        
        # Coletar valores opcionais
        organic_matter_values = [float(analysis.organic_matter) if analysis.organic_matter is not None else None for analysis in analyses]
        base_saturation_values = [float(analysis.base_saturation) if analysis.base_saturation is not None else None for analysis in analyses]
        
        return render_template('analises/listar_analises.html', analyses=analyses, 
                              dates=dates, ph_values=ph_values, phosphorus_values=phosphorus_values,
                              potassium_values=potassium_values, calcium_values=calcium_values, 
                              magnesium_values=magnesium_values, organic_matter_values=organic_matter_values,
                              base_saturation_values=base_saturation_values,
                              any_organic_matter=any_organic_matter, any_base_saturation=any_base_saturation)
    
    return render_template('analises/listar_analises.html', analyses=analyses,
                          any_organic_matter=any_organic_matter, any_base_saturation=any_base_saturation)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 