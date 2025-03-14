from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def current_user(user_id):
    return usuario.query.get(user_id)

class usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    agro = db.Column(db.String(255), nullable=False)
    prod = db.Column(db.String(255), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    ativo = db.Column(db.Boolean, default=True)
    
    def json(self):
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'agro': self.agro,
            'prod': self.prod,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d %H:%M:%S') if self.data_cadastro else None,
            'ultimo_acesso': self.ultimo_acesso.strftime('%Y-%m-%d %H:%M:%S') if self.ultimo_acesso else None,
            'ativo': self.ativo                          
        }
    
    def atualizar_ultimo_acesso(self):
        self.ultimo_acesso = datetime.utcnow()
        db.session.commit()

class informacao_solo(db.Model):
    __tablename__ = "informacao_solo"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_analise = db.Column(db.DateTime, default=datetime.utcnow)
    area = db.Column(db.Float, nullable=True)  # Ex: 1.2 hectares
    tipo_solo = db.Column(db.String(255), nullable=True)  # Ex: Arenoso, Argiloso, Siltoso
    ph_solo = db.Column(db.Float, nullable=True)  # Ex: 6.5
    materia_organica = db.Column(db.Float, nullable=True)  # Ex: 3.2%
    ctc = db.Column(db.Float, nullable=True)  # Capacidade de Troca Catiônica (%)
    nivel_nitrogenio = db.Column(db.Float, nullable=True)  # Ex: 5.3%
    nivel_fosforo = db.Column(db.Float, nullable=True)  # Ex: 4.5%
    nivel_potassio = db.Column(db.Float, nullable=True)  # Nível de Potássio
    aplicacao_recomendada = db.Column(db.Text, nullable=True)  # Instruções para o produtor
    
    # Relacionamento com o usuário
    usuario = db.relationship('usuario', backref=db.backref('solos', lazy=True))
    
    def json(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'data_analise': self.data_analise.strftime('%Y-%m-%d %H:%M:%S') if self.data_analise else None,
            'area': self.area,
            'tipo_solo': self.tipo_solo,
            'ph_solo': self.ph_solo,
            'materia_organica': self.materia_organica,
            'ctc': self.ctc,
            'nivel_nitrogenio': self.nivel_nitrogenio,
            'nivel_fosforo': self.nivel_fosforo,
            'nivel_potassio': self.nivel_potassio,
            'aplicacao_recomendada': self.aplicacao_recomendada                            
        }

class Safra(db.Model):
    __tablename__ = "safras"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cultura = db.Column(db.String(50), nullable=False)
    area = db.Column(db.Float, nullable=False)  # Área total em hectares
    previsao_plantio = db.Column(db.Date, nullable=False)  # Data de previsão do plantio
    previsao_colheita = db.Column(db.Date, nullable=False)  # Data de previsão da colheita
    produtividade_estimada = db.Column(db.Float, nullable=False)  # Produtividade estimada em kg/ha
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com o usuário
    usuario = db.relationship('usuario', backref=db.backref('safras', lazy=True))
    
    def json(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nome': self.nome,
            'cultura': self.cultura,
            'area': self.area,
            'previsao_plantio': self.previsao_plantio.strftime('%Y-%m-%d') if self.previsao_plantio else None,
            'previsao_colheita': self.previsao_colheita.strftime('%Y-%m-%d') if self.previsao_colheita else None,
            'produtividade_estimada': self.produtividade_estimada,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d %H:%M:%S') if self.data_cadastro else None
        }