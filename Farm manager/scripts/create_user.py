from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

def create_user(username, email, password):
    """Criar usuário normal"""
    with app.app_context():
        # Verificar se o usuário já existe
        user = User.query.filter_by(username=username).first()
        
        if user:
            return f"ERRO: Usuário '{username}' já existe!"
        else:
            # Criar novo usuário
            new_user = User(
                username=username,
                email=email,
                is_admin=False
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return f"Novo usuário '{username}' criado com sucesso!"

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description='Criar um novo usuário')
    parser.add_argument('--username', required=True, help='Nome de usuário')
    parser.add_argument('--email', required=True, help='Email')
    parser.add_argument('--password', required=True, help='Senha')
    
    args = parser.parse_args()
    
    try:
        with app.app_context():
            # Criar tabelas se não existirem
            db.create_all()
        
        result = create_user(args.username, args.email, args.password)
        print(result)
        
        if not result.startswith("ERRO"):
            print(f"Usuário: {args.username}")
            print(f"Email: {args.email}")
            print(f"Senha: {args.password}")
            print("Usuário criado sem permissões administrativas.")
        
    except Exception as e:
        print(f"Erro ao criar usuário: {str(e)}")

if __name__ == "__main__":
    main() 