from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import requests
from flask import Blueprint

# Importar blueprints
from app.routes.areas import areas_bp
from app.routes.analises import bp as analises_bp
from app.routes.silos import silos_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Registrar blueprints
app.register_blueprint(areas_bp)
app.register_blueprint(analises_bp)
app.register_blueprint(silos_bp)

# Adicionar contexto para a barra lateral
@app.context_processor
def inject_blueprint_url():
    return {
        'areas_url': lambda: url_for('areas.listar_areas'),
        'analises_url': lambda: url_for('analises.listar_analises'),
        'silos_url': lambda: url_for('silos.listar_silos')
    }

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ph = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    potassium = db.Column(db.Float)
    calcium = db.Column(db.Float)
    magnesium = db.Column(db.Float)

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

# Decorator para verificar se o usuário é admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Função para resetar o banco de dados
def reset_database():
    with app.app_context():
        # Remover todas as tabelas
        db.drop_all()
        # Criar novas tabelas
        db.create_all()
        # Criar admin padrão
        create_initial_admin()

# Adicionar variáveis de contexto a todos os templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Rotas
@app.route('/test')
def test():
    return "<h1>Teste OK!</h1><p>O Flask está funcionando.</p>"

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/create-admin-now')
def create_admin_now():
    try:
        # Verificar se o banco de dados está configurado
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        
        # Criar tabelas se não existirem
        db.create_all()
        
        # Criar usuário admin diretamente
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.is_admin = True  # Garantir que é admin
            admin.set_password('admin')  # Resetar senha
            db.session.commit()
            result = "Usuário admin existente atualizado. Senha: admin"
        else:
            new_admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            new_admin.set_password('admin')
            db.session.add(new_admin)
            db.session.commit()
            result = "Novo usuário admin criado. Username: admin, Senha: admin"
        
        # Contar usuários para verificação
        user_count = User.query.count()
        
        html = f"""
        <html>
        <head>
            <title>Criação de Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .success {{ color: green; background: #e7f7e7; padding: 10px; border-radius: 5px; }}
                .info {{ background: #e7f7ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .btn {{ display: inline-block; background: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Manutenção de Usuário Admin</h1>
                
                <div class="success">
                    <strong>{result}</strong>
                </div>
                
                <div class="info">
                    <p><strong>Informações do banco de dados:</strong></p>
                    <ul>
                        <li>String de conexão: {db_url}</li>
                        <li>Total de usuários: {user_count}</li>
                    </ul>
                </div>
                
                <p>
                    Agora você pode fazer login com:
                    <ul>
                        <li><strong>Usuário:</strong> admin</li>
                        <li><strong>Senha:</strong> admin</li>
                    </ul>
                </p>
                
                <a href="/login" class="btn">Ir para página de login</a>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"""
        <h1>Erro na criação do admin</h1>
        <p style="color: red;">{str(e)}</p>
        <p>Tente executar o comando a seguir no console para identificar o problema:</p>
        <pre>flask shell</pre>
        <p>Em seguida, dentro do shell, execute:</p>
        <pre>
from app import db, User
db.create_all()
admin = User(username='admin', email='admin@example.com', is_admin=True)
admin.set_password('admin')
db.session.add(admin)
db.session.commit()
        </pre>
        """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Adicionar logs para diagnóstico
        print(f"Tentativa de login com usuário: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash(f'Usuário "{username}" não encontrado', 'danger')
            return render_template('login.html')
            
        if user and user.check_password(password):
            login_user(user)
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Senha incorreta', 'danger')
    
    # Criar admin se não existir (garantia extra)
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Se não houver usuário admin, cria um novo
        create_initial_admin()
        flash('Usuário admin foi criado. Usuário: admin, Senha: admin', 'info')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/reset_db', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_db():
    if request.method == 'POST':
        if request.form.get('confirm') == 'RESET':
            reset_database()
            flash('O banco de dados foi resetado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Confirmação incorreta', 'danger')
            
    return render_template('reset_db.html')

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
            new_user = User(
                username=username,
                email=email,
                is_admin=False
            )
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

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/analises')
@login_required
def analises():
    analyses = Analysis.query.filter_by(user_id=current_user.id).all()
    return render_template('analises.html', analyses=analyses)

@app.route('/nova_analise', methods=['GET', 'POST'])
@login_required
def nova_analise():
    if request.method == 'POST':
        analysis = Analysis(
            date=request.form.get('date'),
            user_id=current_user.id,
            ph=float(request.form.get('ph')),
            phosphorus=float(request.form.get('phosphorus')),
            potassium=float(request.form.get('potassium')),
            calcium=float(request.form.get('calcium')),
            magnesium=float(request.form.get('magnesium'))
        )
        db.session.add(analysis)
        db.session.commit()
        return redirect(url_for('analises'))
    return render_template('nova_analise.html')

@app.route('/debug/admin')
def debug_admin():
    """
    Rota de diagnóstico para forçar a criação do usuário admin e mostrar todos os usuários.
    """
    try:
        # Forçar criação do admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            message = 'Usuário admin criado com sucesso!'
        else:
            # Resetar senha do admin se já existir
            admin.set_password('admin')
            db.session.commit()
            message = 'Senha do usuário admin resetada para "admin"'
        
        # Listar todos os usuários
        users = User.query.all()
        user_list = [f"{u.id}: {u.username} (Admin: {u.is_admin})" for u in users]
        
        html = f"""
        <h1>Debug de Usuários</h1>
        <div style="padding: 15px; background: #eee; border-radius: 5px; margin: 20px 0;">
            <p><strong>{message}</strong></p>
            <p>Você pode fazer login com:</p>
            <ul>
                <li>Usuário: admin</li>
                <li>Senha: admin</li>
            </ul>
        </div>
        
        <h2>Lista de Usuários:</h2>
        <ul>
            {''.join([f'<li>{user}</li>' for user in user_list])}
        </ul>
        
        <p>
            <a href="{url_for('login')}" style="background: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Ir para Login</a>
        </p>
        """
        return html
        
    except Exception as e:
        return f"<h1>Erro:</h1><p>{str(e)}</p>"

@app.route('/emergency-login', methods=['GET', 'POST'])
def emergency_login():
    """Página de login de emergência que não depende do banco de dados"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verificação simplificada apenas para admin
        if username == 'admin' and password == 'admin':
            # Criar um objeto User temporário (não salvo no banco)
            temp_admin = User(id=999, username='admin', email='admin@example.com', is_admin=True)
            login_user(temp_admin)
            flash('Login de emergência bem-sucedido. Algumas funções podem estar limitadas.', 'warning')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Use admin/admin.', 'danger')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login de Emergência</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8d7da; padding: 40px 0; }
            .login-box { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .alert { margin-bottom: 20px; }
            h2 { color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="login-box">
                <h2 class="text-center mb-4">Login de Emergência</h2>
                
                <div class="alert alert-warning">
                    <strong>Atenção!</strong> Esta é uma página de login de emergência para quando o banco de dados não está funcionando.
                </div>
                
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Usuário</label>
                        <input type="text" class="form-control" id="username" name="username" value="admin" readonly>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Senha</label>
                        <input type="password" class="form-control" id="password" name="password" value="admin" readonly>
                    </div>
                    
                    <button type="submit" class="btn btn-danger w-100">Login de Emergência</button>
                </form>
                
                <div class="mt-3 text-center">
                    <a href="/login">Voltar para login normal</a> | 
                    <a href="/create-admin-now">Criar usuário admin</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin-test')
def admin_test():
    return """
    <h1>Teste de Rota do Admin</h1>
    <p>Esta rota está funcionando corretamente!</p>
    <p><a href="/create-admin-now">Tentar criar admin</a></p>
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
        new_user = User(
            username=username,
            email=email,
            is_admin=False
        )
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Inicialização do banco de dados e criação do admin padrão
def create_initial_admin():
    try:
        # Verifica se já existe algum admin
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print('Admin padrão criado: admin / admin')
        return True
    except Exception as e:
        print(f"Erro ao criar admin: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        with app.app_context():
            print("Inicializando o banco de dados...")
            db.create_all()
            print("Tabelas criadas com sucesso!")
            
            # Verificar se o admin existe
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"Usuário admin já existe (ID: {admin.id})")
            else:
                print("Criando usuário admin...")
                create_initial_admin()
                
        app.run(debug=True)
    except Exception as e:
        print(f"ERRO NA INICIALIZAÇÃO: {str(e)}")
        
        # Tentar novamente com uma nova conexão
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temporary.db'
        print("Tentando usar SQLite temporário...")
        with app.app_context():
            db.create_all()
            create_initial_admin()
        app.run(debug=True) 