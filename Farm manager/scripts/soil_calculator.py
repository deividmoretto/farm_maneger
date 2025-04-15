from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import argparse
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)
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

def calculate_base_saturation(ca, mg, k):
    """Calcula a saturação por bases (V%)"""
    # Supondo CTC total de 10 cmolc/dm³ (valor aproximado comum em solos agrícolas)
    ctc = 10.0  
    sum_bases = ca + mg + k
    v_percent = (sum_bases / ctc) * 100
    return v_percent

def calculate_lime_need(current_ph, target_ph=6.0, soil_type='argiloso'):
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

def evaluate_soil_parameters(values):
    """Avalia os parâmetros de solo e gera recomendações"""
    results = {}
    recommendations = []
    
    # Avaliação de pH
    results['ph'] = {
        'value': values['ph'],
        'ideal_range': IDEAL_RANGES['ph'],
        'status': 'Ideal' if IDEAL_RANGES['ph'][0] <= values['ph'] <= IDEAL_RANGES['ph'][1] else 
                 ('Baixo' if values['ph'] < IDEAL_RANGES['ph'][0] else 'Alto')
    }
    
    if values['ph'] < IDEAL_RANGES['ph'][0]:
        lime_need = calculate_lime_need(values['ph'])
        recommendations.append(f"Necessidade de calagem: {lime_need:.2f} t/ha de calcário")
    elif values['ph'] > IDEAL_RANGES['ph'][1]:
        recommendations.append("pH alto. Considere o uso de fertilizantes acidificantes como o sulfato de amônio")
    
    # Avaliação de fósforo
    results['phosphorus'] = {
        'value': values['phosphorus'],
        'ideal_range': IDEAL_RANGES['phosphorus'],
        'status': 'Ideal' if IDEAL_RANGES['phosphorus'][0] <= values['phosphorus'] <= IDEAL_RANGES['phosphorus'][1] else 
                 ('Baixo' if values['phosphorus'] < IDEAL_RANGES['phosphorus'][0] else 'Alto')
    }
    
    if values['phosphorus'] < IDEAL_RANGES['phosphorus'][0]:
        p_deficit = IDEAL_RANGES['phosphorus'][0] - values['phosphorus']
        p_rec = p_deficit * 10  # Valor aproximado - cada 1 mg/dm³ requer ~10 kg/ha de P2O5
        recommendations.append(f"Aplicar aproximadamente {p_rec:.2f} kg/ha de P2O5")
    
    # Avaliação de potássio
    results['potassium'] = {
        'value': values['potassium'],
        'ideal_range': IDEAL_RANGES['potassium'],
        'status': 'Ideal' if IDEAL_RANGES['potassium'][0] <= values['potassium'] <= IDEAL_RANGES['potassium'][1] else 
                 ('Baixo' if values['potassium'] < IDEAL_RANGES['potassium'][0] else 'Alto')
    }
    
    if values['potassium'] < IDEAL_RANGES['potassium'][0]:
        k_deficit = IDEAL_RANGES['potassium'][0] - values['potassium']
        k_rec = k_deficit * 390  # Aproximadamente 390 kg/ha de K2O para cada 0.1 cmolc/dm³
        recommendations.append(f"Aplicar aproximadamente {k_rec:.2f} kg/ha de K2O")
    
    # Avaliação de cálcio
    results['calcium'] = {
        'value': values['calcium'],
        'ideal_range': IDEAL_RANGES['calcium'],
        'status': 'Ideal' if IDEAL_RANGES['calcium'][0] <= values['calcium'] <= IDEAL_RANGES['calcium'][1] else 
                 ('Baixo' if values['calcium'] < IDEAL_RANGES['calcium'][0] else 'Alto')
    }
    
    # Avaliação de magnésio
    results['magnesium'] = {
        'value': values['magnesium'],
        'ideal_range': IDEAL_RANGES['magnesium'],
        'status': 'Ideal' if IDEAL_RANGES['magnesium'][0] <= values['magnesium'] <= IDEAL_RANGES['magnesium'][1] else 
                 ('Baixo' if values['magnesium'] < IDEAL_RANGES['magnesium'][0] else 'Alto')
    }
    
    # Calcular e avaliar a relação Ca/Mg
    if values['magnesium'] > 0:
        ca_mg_ratio = values['calcium'] / values['magnesium']
        results['ca_mg_ratio'] = {
            'value': ca_mg_ratio,
            'ideal_range': IDEAL_RANGES['ca_mg_ratio'],
            'status': 'Ideal' if IDEAL_RANGES['ca_mg_ratio'][0] <= ca_mg_ratio <= IDEAL_RANGES['ca_mg_ratio'][1] else 
                     ('Baixo' if ca_mg_ratio < IDEAL_RANGES['ca_mg_ratio'][0] else 'Alto')
        }
        
        if ca_mg_ratio < IDEAL_RANGES['ca_mg_ratio'][0]:
            recommendations.append("Relação Ca/Mg baixa. Considere o uso de calcário calcítico")
        elif ca_mg_ratio > IDEAL_RANGES['ca_mg_ratio'][1]:
            recommendations.append("Relação Ca/Mg alta. Considere o uso de calcário dolomítico")
    
    # Calcular saturação por bases
    v_percent = calculate_base_saturation(values['calcium'], values['magnesium'], values['potassium'])
    results['base_saturation'] = {
        'value': v_percent,
        'ideal_range': (60, 80),
        'status': 'Ideal' if 60 <= v_percent <= 80 else ('Baixo' if v_percent < 60 else 'Alto')
    }
    
    if v_percent < 60:
        recommendations.append(f"Saturação por bases baixa ({v_percent:.2f}%). Considere aumentar a calagem")
    
    return {
        'soil_parameters': results,
        'recommendations': recommendations
    }

def save_analysis_to_db(values, area_id=None, user_id=None):
    """Salva os resultados da análise no banco de dados"""
    with app.app_context():
        analysis = Analysis(
            date=datetime.now(),
            area_id=area_id,
            user_id=user_id,
            ph=values['ph'],
            phosphorus=values['phosphorus'],
            potassium=values['potassium'],
            calcium=values['calcium'],
            magnesium=values['magnesium']
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis.id

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description='Calculadora de Análise de Solo')
    parser.add_argument('--ph', type=float, required=True, help='Valor do pH do solo')
    parser.add_argument('--p', '--phosphorus', type=float, required=True, help='Fósforo (P) em mg/dm³')
    parser.add_argument('--k', '--potassium', type=float, required=True, help='Potássio (K) em cmolc/dm³')
    parser.add_argument('--ca', '--calcium', type=float, required=True, help='Cálcio (Ca) em cmolc/dm³')
    parser.add_argument('--mg', '--magnesium', type=float, required=True, help='Magnésio (Mg) em cmolc/dm³')
    parser.add_argument('--save', action='store_true', help='Salvar análise no banco de dados')
    parser.add_argument('--area-id', type=int, help='ID da área (opcional)')
    parser.add_argument('--user-id', type=int, help='ID do usuário (opcional)')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='Formato de saída')
    
    args = parser.parse_args()
    
    soil_values = {
        'ph': args.ph,
        'phosphorus': args.p,
        'potassium': args.k,
        'calcium': args.ca,
        'magnesium': args.mg
    }
    
    try:
        # Criar tabelas se não existirem
        with app.app_context():
            db.create_all()
        
        # Avaliar solo e gerar recomendações
        evaluation = evaluate_soil_parameters(soil_values)
        
        # Salvar análise no banco de dados, se solicitado
        if args.save:
            analysis_id = save_analysis_to_db(soil_values, args.area_id, args.user_id)
            print(f"Análise salva no banco de dados com ID: {analysis_id}")
        
        # Formatar e exibir resultados
        if args.output == 'json':
            print(json.dumps(evaluation, indent=2))
        else:
            print("\n=== RESULTADO DA ANÁLISE DE SOLO ===\n")
            
            for param, info in evaluation['soil_parameters'].items():
                param_name = {
                    'ph': 'pH',
                    'phosphorus': 'Fósforo (P)',
                    'potassium': 'Potássio (K)',
                    'calcium': 'Cálcio (Ca)',
                    'magnesium': 'Magnésio (Mg)',
                    'ca_mg_ratio': 'Relação Ca/Mg',
                    'base_saturation': 'Saturação por Bases'
                }.get(param, param)
                
                status_color = {
                    'Ideal': '',
                    'Baixo': ' - BAIXO',
                    'Alto': ' - ALTO'
                }.get(info['status'], '')
                
                print(f"{param_name}: {info['value']:.2f} {status_color}")
                print(f"  Faixa ideal: {info['ideal_range'][0]} - {info['ideal_range'][1]}")
            
            print("\n=== RECOMENDAÇÕES ===\n")
            if evaluation['recommendations']:
                for i, rec in enumerate(evaluation['recommendations'], 1):
                    print(f"{i}. {rec}")
            else:
                print("Não há recomendações específicas. Os parâmetros do solo estão em níveis adequados.")
        
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    main() 