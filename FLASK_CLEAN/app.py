from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Cria uma instância da aplicação Flask
app = Flask(__name__)

# Configura a URI do banco de dados, conectando a um banco de dados PostgreSQL local
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:incorreta@localhost/dbname'

# Desativa o recurso de monitoramento de modificações de objetos do SQLAlchemy, pois não é necessário neste contexto
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cria uma instância do SQLAlchemy, passando a aplicação Flask para integrar o banco de dados com a aplicação
db = SQLAlchemy(app)

