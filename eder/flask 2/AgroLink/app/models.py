from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def current_user(user_id):
    return usuario.query.get(user_id)

class usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    nome = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    agro = db.Column(db.String(255), nullable=False)
    prod = db.Column(db.String(255), nullable=False)
    data = db.Column(db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()) 
    def json(self):
        return{
            'id':self.id,
            'email':self.email,
            'nome':self.nome,
            'senha':self.senha,
            'agro':self.agro,
            'prod':self.prod                            
        }    
class informacao_solo(db.Model):
    __tablename__ = "informacao_solo"
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.Float, nullable=True)  # Ex: 1.2 hectares
    tipo_solo = db.Column(db.String(255), nullable=True)  # Ex: Arenoso, Argiloso, Siltoso
    ph_solo = db.Column(db.Float, nullable=True)  # Ex: 6.5
    materia_organica = db.Column(db.Float, nullable=True)  # Ex: 3.2%
    ctc = db.Column(db.Float, nullable=True)  # Capacidade de Troca Catiônica (%)
    nivel_nitrogenio = db.Column(db.Float, nullable=True)  # Ex: 5.3%
    nivel_fosforo = db.Column(db.Float, nullable=True)  # Ex: 4.5%
    nivel_potassio = db.Column(db.Float, nullable=True)  # Nível de Potássio
    aplicacao_recomendada = db.Column(db.Text, nullable=True)  # Instruções para o produtor
    #data = db.Column(db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()) 
    def json(self):
        return{
            'id':self.id,
            'area':self.area,
            'tipo_solo':self.tipo_solo,
            'ph_solo':self.ph_solo,
            'materia_organica':self.materia_organica,
            'ctc':self.ctc,
            'nivel_nitrogenio':self.nivel_nitrogenio,
            'nivel_fosforo':self.nivel_fosforo,
            'nivel_potassio':self.nivel_potassio,
            'aplicacao_recomendada':self.aplicacao_recomendada                            
        }    