from app import db
from datetime import datetime

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    
    # Parâmetros Principais
    ph = db.Column(db.Float)
    phosphorus = db.Column(db.Float)  # Fósforo (P) - mg/dm³
    potassium = db.Column(db.Float)   # Potássio (K) - cmolc/dm³
    calcium = db.Column(db.Float)     # Cálcio (Ca) - cmolc/dm³
    magnesium = db.Column(db.Float)   # Magnésio (Mg) - cmolc/dm³
    
    # Parâmetros Adicionais
    aluminum = db.Column(db.Float, nullable=True)    # Alumínio (Al) - cmolc/dm³
    sulfur = db.Column(db.Float, nullable=True)      # Enxofre (S) - mg/dm³
    organic_matter = db.Column(db.Float, nullable=True)  # Matéria Orgânica (%) 
    cation_exchange = db.Column(db.Float, nullable=True) # CTC - cmolc/dm³
    base_saturation = db.Column(db.Float, nullable=True) # Saturação por Bases (%)
    
    # Observações
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Analysis {self.id}>' 