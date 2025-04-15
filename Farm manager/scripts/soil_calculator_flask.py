from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ph = db.Column(db.Float)
    phosphorus = db.Column(db.Float)  # P (mg/dm³)
    potassium = db.Column(db.Float)   # K (cmolc/dm³)
    calcium = db.Column(db.Float)     # Ca (cmolc/dm³)
    magnesium = db.Column(db.Float)   # Mg (cmolc/dm³)

# Formulário para a calculadora de solo
class SoilCalculatorForm(FlaskForm):
    ph = FloatField('pH', validators=[DataRequired(), NumberRange(min=3.0, max=9.0)], default=5.5)
    fosforo = FloatField('Fósforo (P) mg/dm³', validators=[DataRequired(), NumberRange(min=0)], default=10.0)
    potassio = FloatField('Potássio (K) cmolc/dm³', validators=[DataRequired(), NumberRange(min=0)], default=0.15)
    calcio = FloatField('Cálcio (Ca) cmolc/dm³', validators=[DataRequired(), NumberRange(min=0)], default=2.0)
    magnesio = FloatField('Magnésio (Mg) cmolc/dm³', validators=[DataRequired(), NumberRange(min=0)], default=0.8)
    aluminio = FloatField('Alumínio (Al) cmolc/dm³', validators=[NumberRange(min=0)], default=0.0)
    hidrogenio = FloatField('Hidrogênio + Al (H+Al) cmolc/dm³', validators=[NumberRange(min=0)], default=3.0)
    tipo_solo = SelectField('Tipo de Solo', choices=[
        ('arenoso', 'Arenoso'), 
        ('medio', 'Textura Média'), 
        ('argiloso', 'Argiloso')
    ], default='medio')
    prnt = FloatField('PRNT do Calcário (%)', validators=[NumberRange(min=0, max=100)], default=85.0)
    v_desejado = FloatField('Saturação por Bases Desejada (V%)', validators=[NumberRange(min=0, max=100)], default=70.0)
    cultura = SelectField('Cultura', choices=[
        ('milho', 'Milho'),
        ('soja', 'Soja'),
        ('cafe', 'Café'),
        ('frutas', 'Fruticultura'),
        ('hortalicas', 'Hortaliças'),
        ('pastagem', 'Pastagem'),
        ('outros', 'Outros')
    ], default='soja')
    area = FloatField('Área (hectares)', validators=[NumberRange(min=0)], default=1.0)
    submit = SubmitField('Calcular')

# Valores ideais para referência
IDEAL_RANGES = {
    'ph': (5.5, 6.5),               # Faixa ideal de pH
    'phosphorus': (15.0, 30.0),     # P (mg/dm³)
    'potassium': (0.15, 0.30),      # K (cmolc/dm³)
    'calcium': (2.0, 4.0),          # Ca (cmolc/dm³)
    'magnesium': (0.8, 1.5),        # Mg (cmolc/dm³)
    'ca_mg_ratio': (3.0, 5.0),      # Relação Ca/Mg
    'k_percentage': (3.0, 5.0)      # Porcentagem de K na CTC
}

def calculate_ctc(ca, mg, k, h_al):
    """Calcula a CTC do solo"""
    return ca + mg + k + h_al

def calculate_base_saturation(ca, mg, k, ctc):
    """Calcula a saturação por bases (V%)"""
    sum_bases = ca + mg + k
    if ctc > 0:
        v_percent = (sum_bases / ctc) * 100
        return v_percent
    return 0

def calculate_aluminum_saturation(al, ca, mg, k):
    """Calcula a saturação por alumínio (m%)"""
    if al > 0 and (ca + mg + k + al) > 0:
        m_percent = (al / (ca + mg + k + al)) * 100
        return m_percent
    return 0

def calculate_lime_need(ctc, v_atual, v_desejado, prnt=100):
    """Calcula necessidade de calagem pelo método da saturação por bases"""
    if v_atual >= v_desejado:
        return 0
    
    # Fórmula: NC = (V2 - V1) * CTC / (10 * PRNT/100)
    nc = (v_desejado - v_atual) * ctc / (10 * prnt/100)
    return nc

def calculate_lime_need_by_ph(current_ph, target_ph=6.0, soil_type='medio'):
    """Calcula necessidade de calagem baseado no pH"""
    if current_ph >= target_ph:
        return 0

    # Fatores multiplicadores por tipo de solo
    soil_factors = {
        'arenoso': 1.0,
        'medio': 1.5,
        'argiloso': 2.0
    }
    
    factor = soil_factors.get(soil_type, 1.5)
    ph_diff = target_ph - current_ph
    
    # Fórmula simplificada para necessidade de calcário em t/ha
    lime_need = ph_diff * factor
    return lime_need

def get_interpretation(value, parameter):
    """Obter interpretação textual para os valores do solo"""
    if parameter == 'ph':
        if value < 4.5:
            return "Muito Ácido"
        elif value < 5.5:
            return "Ácido"
        elif value < 6.5:
            return "Adequado"
        elif value < 7.5:
            return "Neutro"
        else:
            return "Alcalino"
    
    elif parameter == 'phosphorus':
        if value < 5.0:
            return "Muito Baixo"
        elif value < 10.0:
            return "Baixo"
        elif value < 15.0:
            return "Médio"
        elif value < 30.0:
            return "Bom"
        else:
            return "Muito Bom"
    
    elif parameter == 'potassium':
        if value < 0.08:
            return "Muito Baixo"
        elif value < 0.15:
            return "Baixo"
        elif value < 0.25:
            return "Médio"
        elif value < 0.40:
            return "Bom"
        else:
            return "Muito Bom"
    
    elif parameter == 'calcium':
        if value < 1.0:
            return "Muito Baixo"
        elif value < 2.0:
            return "Baixo"
        elif value < 4.0:
            return "Médio"
        elif value < 7.0:
            return "Bom"
        else:
            return "Muito Bom"
    
    elif parameter == 'magnesium':
        if value < 0.4:
            return "Muito Baixo"
        elif value < 0.8:
            return "Baixo"
        elif value < 1.5:
            return "Médio"
        elif value < 3.0:
            return "Bom"
        else:
            return "Muito Bom"
    
    return "Indeterminado"

def evaluate_soil(form_data):
    """Avalia os parâmetros do solo e calcula as recomendações"""
    # Extrair valores do formulário
    ph = form_data.get('ph')
    phosphorus = form_data.get('fosforo')
    potassium = form_data.get('potassio')
    calcium = form_data.get('calcio')
    magnesium = form_data.get('magnesio')
    aluminum = form_data.get('aluminio')
    h_al = form_data.get('hidrogenio')
    soil_type = form_data.get('tipo_solo')
    prnt = form_data.get('prnt')
    v_desejado = form_data.get('v_desejado')
    cultura = form_data.get('cultura')
    area = form_data.get('area')
    
    # Cálculos
    ctc = calculate_ctc(calcium, magnesium, potassium, h_al)
    v_atual = calculate_base_saturation(calcium, magnesium, potassium, ctc)
    m = calculate_aluminum_saturation(aluminum, calcium, magnesium, potassium)
    
    # Cálculo da necessidade de calagem
    nc = calculate_lime_need(ctc, v_atual, v_desejado, prnt)
    
    # Cálculo da relação Ca/Mg
    ca_mg_ratio = calcium / magnesium if magnesium > 0 else 0
    
    # Interpretações
    interpretacao_ph = get_interpretation(ph, 'ph')
    interpretacao_p = get_interpretation(phosphorus, 'phosphorus')
    interpretacao_k = get_interpretation(potassium, 'potassium')
    interpretacao_ca = get_interpretation(calcium, 'calcium')
    interpretacao_mg = get_interpretation(magnesium, 'magnesium')
    
    # Resultados
    resultados = {
        'ctc': round(ctc, 2),
        'v': round(v_atual, 2),
        'm': round(m, 2),
        'relacao_ca_mg': round(ca_mg_ratio, 2),
        'nc': round(nc, 2),
        'prnt': prnt,
        'v_desejado': v_desejado,
        'cultura': cultura,
        'area': area,
        'interpretacao_ph': interpretacao_ph,
        'interpretacao_p': interpretacao_p,
        'interpretacao_k': interpretacao_k,
        'interpretacao_ca': interpretacao_ca,
        'interpretacao_mg': interpretacao_mg
    }
    
    return resultados

@app.route('/', methods=['GET', 'POST'])
@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    form = SoilCalculatorForm()
    resultados = None
    
    if form.validate_on_submit():
        # Obter dados do formulário
        form_data = {
            'ph': form.ph.data,
            'fosforo': form.fosforo.data,
            'potassio': form.potassio.data,
            'calcio': form.calcio.data,
            'magnesio': form.magnesio.data,
            'aluminio': form.aluminio.data,
            'hidrogenio': form.hidrogenio.data,
            'tipo_solo': form.tipo_solo.data,
            'prnt': form.prnt.data,
            'v_desejado': form.v_desejado.data,
            'cultura': form.cultura.data,
            'area': form.area.data
        }
        
        # Avaliar solo
        resultados = evaluate_soil(form_data)
        
    return render_template('soil_calculator.html', form=form, resultados=resultados)

def save_analysis_to_db(values, user_id=None, area_id=None):
    """Salva os resultados da análise no banco de dados"""
    try:
        analysis = Analysis(
            date=datetime.now(),
            user_id=user_id,
            area_id=area_id,
            ph=values['ph'],
            phosphorus=values['fosforo'],
            potassium=values['potassio'],
            calcium=values['calcio'],
            magnesium=values['magnesio']
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis.id
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar análise: {str(e)}")
        return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002) 