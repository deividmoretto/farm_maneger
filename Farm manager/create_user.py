from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

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

@app.route('/')
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
            new_user = User(username=username, email=email, is_admin=False)
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
        new_user = User(username=username, email=email, is_admin=False)
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Certifique-se de que a tabela existe
    app.run(debug=True, port=5001)  # Usando porta diferente para não conflitar com a aplicação principal 