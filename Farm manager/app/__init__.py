from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config=None):
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Importar blueprints
    from app.routes import auth, main, areas, analises
    
    # Registrar blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(areas.areas_bp)
    app.register_blueprint(analises.bp)
    
    # Criar tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    return app 