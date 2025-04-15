from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash(f'Usuário "{username}" não encontrado', 'danger')
            return render_template('auth/login.html')
            
        if user and user.check_password(password):
            login_user(user)
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Senha incorreta', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f'Usuário "{username}" já existe', 'danger')
            return render_template('auth/register.html')
            
        # Criar novo usuário
        new_user = User(
            username=username,
            email=email,
            is_admin=False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html') 