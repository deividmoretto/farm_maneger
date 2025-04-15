from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.analise import Analysis
from app.models.area import Area
from datetime import datetime

bp = Blueprint('analises', __name__)

@bp.route('/analises')
@login_required
def listar_analises():
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.date).all()
    
    # Preparar dados para o gráfico
    datas = []
    valores_ph = []
    valores_p = []
    valores_k = []
    valores_ca = []
    valores_mg = []
    
    for analise in analyses:
        datas.append(analise.date.strftime('%d/%m/%Y'))
        valores_ph.append(analise.ph)
        valores_p.append(analise.phosphorus)
        valores_k.append(analise.potassium)
        valores_ca.append(analise.calcium)
        valores_mg.append(analise.magnesium)
    
    return render_template('analises/listar_analises.html', 
                          analyses=analyses,
                          datas=datas,
                          valores_ph=valores_ph,
                          valores_p=valores_p,
                          valores_k=valores_k,
                          valores_ca=valores_ca,
                          valores_mg=valores_mg)

@bp.route('/nova-analise', methods=['GET', 'POST'])
@login_required
def nova_analise():
    from app.models.area import Area
    from app.models.analise import Analysis
    
    areas = Area.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        try:
            area_id = request.form.get('area_id')
            if not area_id:
                flash('Selecione uma área para a análise', 'danger')
                return redirect(url_for('analises.nova_analise'))
            
            date_str = request.form.get('date')
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                date = datetime.now()
            
            # Cria a nova análise com todos os parâmetros
            analise = Analysis(
                area_id=area_id,
                date=date,
                ph=float(request.form.get('ph', 0)),
                phosphorus=float(request.form.get('phosphorus', 0)),
                potassium=float(request.form.get('potassium', 0)),
                calcium=float(request.form.get('calcium', 0)),
                magnesium=float(request.form.get('magnesium', 0)),
                aluminum=float(request.form.get('aluminum', 0)) if request.form.get('aluminum') else None,
                sulfur=float(request.form.get('sulfur', 0)) if request.form.get('sulfur') else None,
                organic_matter=float(request.form.get('organic_matter', 0)) if request.form.get('organic_matter') else None,
                cation_exchange=float(request.form.get('cation_exchange', 0)) if request.form.get('cation_exchange') else None,
                base_saturation=float(request.form.get('base_saturation', 0)) if request.form.get('base_saturation') else None,
                notes=request.form.get('notes', '')
            )
            
            db.session.add(analise)
            db.session.commit()
            flash('Análise registrada com sucesso!', 'success')
            return redirect(url_for('analises.listar_analises'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar análise: {str(e)}', 'danger')
    
    return render_template('analises/nova_analise.html', areas=areas) 