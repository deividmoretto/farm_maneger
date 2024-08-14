from . import db
from flask_login import UserMixin

"""Modelo de usuário que representa os usuários no banco de dados. """
class User(UserMixin, db.Model):
    
    # Definição das colunas da tabela 'User' no banco de dados

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

 #Modelo de cultura que representa as culturas no banco de dados.
class Crop(db.Model):
   
    # Definição das colunas da tabela 'Crop' no banco de dados

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    #Retorna uma representação em string da instância de Crop. 
    def __repr__(self):
        return f"Crop('{self.name}', '{self.description}')"
