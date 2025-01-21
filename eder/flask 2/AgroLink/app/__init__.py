from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Inicialização de extensões
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="../public")
    
    # Configuração do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:incorreta@localhost/AgroLink'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações de segurança e JWT
    app.config["SECRET_KEY"] = 'secret'
    app.config['JWT_SECRET_KEY'] = 'secret'
    app.config['JWT_BLACKLIST_ENABLE'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

    # Inicialização de extensões
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Rotas
    from app import routes
    routes.init_app(app)

    return app