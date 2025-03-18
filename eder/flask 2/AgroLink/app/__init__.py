from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Inicialização de extensões
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="../public")
    
    # Configuração do banco de dados usando variáveis de ambiente
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/AgroLink')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações de segurança e JWT
    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'chave_temporaria_para_desenvolvimento')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'chave_jwt_temporaria_para_desenvolvimento')
    app.config['JWT_BLACKLIST_ENABLE'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora por padrão

    # Inicialização de extensões
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Configuração do login_manager
    login_manager.login_view = 'index'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # Rotas
    from app import routes
    routes.init_app(app)

    return app