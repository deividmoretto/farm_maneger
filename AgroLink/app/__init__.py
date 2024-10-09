from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message
#from flask_bootstrap import Bootstrap

# Instâncias globais
db = SQLAlchemy()  
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="app/template", static_folder="app/static")

    # Configurações de banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:incorreta@localhost/AgroLink'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = 'secret'  # Configuração de chave secreta
    app.config['JWT_SECRET_KEY'] = 'secret'  # Configuração do JWT
    app.config['JWT_BLACKLIST_ENABLE'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token sem expiração
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    # bootstrap.init_app(app)  # Caso queira usar o Bootstrap, descomente isso.

    # Importa e registra as rotas
    from app import routes
    routes.init_app(app)

    return app