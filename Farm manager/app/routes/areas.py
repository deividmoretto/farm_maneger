from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.area import Area
from app.forms.area_form import AreaForm
import requests
import os
from dotenv import load_dotenv

load_dotenv()

areas_bp = Blueprint('areas', __name__)

@areas_bp.route('/areas')
@login_required
def listar_areas():
    areas = Area.query.filter_by(user_id=current_user.id).all()
    return render_template('areas/listar_areas.html', areas=areas)

@areas_bp.route('/areas/nova', methods=['GET', 'POST'])
@login_required
def nova_area():
    form = AreaForm()
    if form.validate_on_submit():
        area = Area(
            nome=form.nome.data,
            cultura=form.cultura.data,
            tamanho=form.tamanho.data,
            endereco=form.endereco.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            descricao=form.descricao.data,
            user_id=current_user.id
        )
        db.session.add(area)
        db.session.commit()
        flash('Área cadastrada com sucesso!', 'success')
        return redirect(url_for('areas.listar_areas'))
    return render_template('areas/nova_area.html', form=form)

@areas_bp.route('/areas/<int:id>')
@login_required
def detalhes_area(id):
    area = Area.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('areas/detalhes_area.html', area=area)

@areas_bp.route('/areas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_area(id):
    area = Area.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = AreaForm(obj=area)
    
    if form.validate_on_submit():
        area.nome = form.nome.data
        area.cultura = form.cultura.data
        area.tamanho = form.tamanho.data
        area.endereco = form.endereco.data
        area.latitude = form.latitude.data
        area.longitude = form.longitude.data
        area.descricao = form.descricao.data
        
        db.session.commit()
        flash('Área atualizada com sucesso!', 'success')
        return redirect(url_for('areas.listar_areas'))
    
    return render_template('areas/editar_area.html', form=form, area=area)

@areas_bp.route('/areas/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_area(id):
    area = Area.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(area)
    db.session.commit()
    flash('Área excluída com sucesso!', 'success')
    return redirect(url_for('areas.listar_areas'))

@areas_bp.route('/api/geocode', methods=['POST'])
@login_required
def geocode_address():
    """API para geocodificar um endereço usando a API do OpenStreetMap Nominatim"""
    data = request.get_json()
    endereco = data.get('endereco', '')
    
    if not endereco:
        return jsonify({'error': 'Endereço não fornecido'}), 400
    
    try:
        # Usando OpenStreetMap Nominatim API (gratuito e não requer chave API)
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': endereco,
                'format': 'json',
                'limit': 1
            },
            headers={'User-Agent': 'FarmApp/1.0'}
        )
        
        response.raise_for_status()
        results = response.json()
        
        if not results:
            return jsonify({'error': 'Endereço não encontrado'}), 404
        
        result = results[0]
        return jsonify({
            'endereco': endereco,
            'latitude': result['lat'],
            'longitude': result['lon'],
            'display_name': result['display_name']
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro ao geocodificar endereço: {str(e)}'}), 500 