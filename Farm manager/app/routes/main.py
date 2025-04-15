from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('main', __name__)

@bp.route('/calculadora')
@login_required
def calculadora():
    return render_template('soil_calculator.html')

@bp.route('/precos')
def precos():
    return render_template('precos.html')

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500 