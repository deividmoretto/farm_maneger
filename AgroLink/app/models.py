from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def current_user(user_id):
    return usuario.query.get(user_id)

class usuario(db.Model, UserMixin):
    __tablename__ = "usuario" # alteracao de usuarios
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    nome = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    agro = db.Column(db.String(255), nullable=False)
    prod = db.Column(db.String(255), nullable=False)

# Tabela para armazenar informações do solo
class informacao_solo(db.Model):
    __tablename__ = "informacao_solo"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Referência ao agrônomo
    area = db.Column(db.Float, nullable=False)  # Ex: 1.2 hectares
    tipo_solo = db.Column(db.String(255), nullable=False)  # Ex: Arenoso, Argiloso, Siltoso
    ph_solo = db.Column(db.Float, nullable=False)  # Ex: 6.5
    materia_organica = db.Column(db.Float, nullable=False)  # Ex: 3.2%
    ctc = db.Column(db.Float, nullable=False)  # Capacidade de Troca Catiônica (%)
    nivel_nitrogenio = db.Column(db.Float, nullable=False)  # Ex: 5.3%
    nivel_fosforo = db.Column(db.Float, nullable=False)  # Ex: 4.5%
    nivel_potassio = db.Column(db.Float, nullable=False)  # Nível de Potássio
    aplicacao_recomendada = db.Column(db.Text, nullable=False)  # Instruções para o produtor

    # Relacionamento com a tabela "usuario"
    usuario = db.relationship('usuario', backref=db.backref('informacoes_solo', lazy=True))