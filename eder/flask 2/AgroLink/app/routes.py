from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, login_user, logout_user, current_user
from psutil import users
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from app import db
from app.models import usuario, informacao_solo, Safra
from app.forms import LoginForm
import os
from functools import wraps

# Decorator para verificar se o usuário está ativo
def require_active_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.ativo:
            flash("Sua conta está desativada. Entre em contato com o administrador.", "danger")
            logout_user()
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

def init_app(app):
    # Rota de login
    @app.route("/", methods=["GET", "POST"])
    def index():
        form = LoginForm()
        if form.validate_on_submit():
            # Busca o usuário pelo email
            user = usuario.query.filter_by(email=form.email.data).first()
            
            # Verifica se o usuário existe e a senha está correta
            if not user or not check_password_hash(user.senha, form.senha.data):
                flash("Email ou senha incorretos!", "danger")
                return redirect(url_for("index"))
            
            # Verifica se o usuário está ativo
            if not user.ativo:
                flash("Sua conta está desativada. Entre em contato com o administrador.", "danger")
                return redirect(url_for("index"))
            
            # Atualiza o último acesso
            user.atualizar_ultimo_acesso()
            
            # Faz login do usuário
            login_user(user, remember=form.remember.data, duration=timedelta(days=7))
            
            # Redireciona para a página inicial
            return redirect(url_for("inicio"))
        
        return render_template("index.html", form=form)
    
    @app.route("/resumo")
    @login_required
    @require_active_user
    def resumo():
        # Obtém totais
        total_usuarios = usuario.query.count()
        total_solos = informacao_solo.query.filter_by(usuario_id=current_user.id).count()
        total_safras = Safra.query.filter_by(usuario_id=current_user.id).count()

        # Obtém as 5 últimas análises de solo do usuário atual
        ultimos_solos = informacao_solo.query.filter_by(usuario_id=current_user.id).order_by(
            informacao_solo.id.desc()
        ).limit(5).all()

        # Obtém as próximas 5 safras do usuário atual
        proximas_safras = Safra.query.filter_by(usuario_id=current_user.id).order_by(
            Safra.id.desc()
        ).limit(5).all()

        # Formata as datas antes de enviar para o template
        for safra in proximas_safras:
            if safra.previsao_plantio:
                safra.previsao_plantio = safra.previsao_plantio.strftime('%d/%m/%Y')
            if safra.previsao_colheita:
                safra.previsao_colheita = safra.previsao_colheita.strftime('%d/%m/%Y')

        return render_template(
            "resumo.html",
            total_usuarios=total_usuarios,
            total_solos=total_solos,
            total_safras=total_safras,
            ultimos_solos=ultimos_solos,
            proximas_safras=proximas_safras
        )
    
    # Cadastro de Usuário
    @app.route("/cad_user", methods=["GET", "POST"])
    @login_required
    def cad_user():
        if request.method == "POST":
            nome = request.form["nome"]
            email = request.form["email"]
            senha = generate_password_hash(request.form["senha"])
            agro = request.form.get("agro", False)
            prod = request.form.get("prod", False)

            novo_usuario = usuario(nome=nome, email=email, senha=senha, agro=agro, prod=prod)
            db.session.add(novo_usuario)
            db.session.commit()
            flash("Usuário cadastrado com sucesso!")
            return redirect(url_for("inicio"))
       
        return render_template("cad_user.html")
    
    # Rota para atualizar usuário
    @app.route("/atualiza_user/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_user(id):
        user = usuario.query.get_or_404(id)
        if request.method == "POST":
            user.nome = request.form["nome"]
            user.email = request.form["email"]
            user.agro = request.form["agro"]
            user.prod = request.form["prod"]
        
            if request.form["senha"]:
                user.senha = generate_password_hash(request.form["senha"])
        
            db.session.commit()
            flash("Usuário atualizado com sucesso!")
            return redirect(url_for("inicio"))
    
        return render_template("atualiza_user.html", user=user)
    
    @app.route("/excluir_user/<int:id>", methods=["POST"])
    @login_required
    def excluir_user(id):
        user = usuario.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        flash("Usuário excluído com sucesso!")
        return redirect(url_for("inicio"))

    # Rota para a página inicial
    @app.route("/inicio")
    @login_required
    def inicio():
        usuarios = usuario.query.all()
        return render_template("inicio.html", usuarios=usuarios)    

    # Rota de logout
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index"))

    # Página de gestão de solo
    @app.route("/solo")
    @login_required
    def solo():
        solos = informacao_solo.query.all()
        return render_template("solo.html", solos=solos)

    @app.route("/alterar_solo/<int:id>", methods=["GET", "POST"])
    @login_required
    def alterar_solo(id):
        solo = informacao_solo.query.get_or_404(id)
        if request.method == "POST":
            solo.area = request.form["area"]
            solo.tipo_solo = request.form["tipo_solo"]
            solo.ph_solo = request.form["ph_solo"]
            solo.materia_organica = request.form["materia_organica"]
            solo.ctc = request.form["ctc"]
            solo.nivel_nitrogenio = request.form["nivel_nitrogenio"]
            solo.nivel_fosforo = request.form["nivel_fosforo"]
            solo.nivel_potassio = request.form["nivel_potassio"]
            solo.aplicacao_recomendada = request.form["aplicacao_recomendada"]
            
            db.session.commit()
            flash("Informações do solo atualizadas com sucesso!")
            return redirect(url_for("solo"))
        
        return render_template("alterar_solo.html", solo=solo)

    @app.route("/excluir_solo/<int:id>")
    @login_required
    def excluir_solo(id):
        solo = informacao_solo.query.get_or_404(id)
        db.session.delete(solo)
        db.session.commit()
        flash("Registro de solo excluído com sucesso!")
        return redirect(url_for("solo"))

    @app.route("/cad_solo", methods=["GET", "POST"])
    @login_required
    def cad_solo():
        if request.method == "POST":
            solo = informacao_solo(
                area=request.form["area"],
                tipo_solo=request.form["tipo_solo"],
                ph_solo=request.form["ph_solo"],
                materia_organica=request.form["materia_organica"],
                ctc=request.form["ctc"],
                nivel_nitrogenio=request.form["nivel_nitrogenio"],
                nivel_fosforo=request.form["nivel_fosforo"],
                nivel_potassio=request.form["nivel_potassio"],
                aplicacao_recomendada=request.form["aplicacao_recomendada"]
            )
            db.session.add(solo)
            db.session.commit()
            flash("Informações de solo cadastradas com sucesso!")
            return redirect(url_for("solo"))
        return render_template("cad_solo.html")

    # Página de gestão de safra
    @app.route("/safra")
    @login_required
    def safra():
        safras = Safra.query.all()

        # Preparar dados mais detalhados para os gráficos
        dados_graficos = {
            'nomes': [s.nome for s in safras],
            'culturas': [s.cultura for s in safras],
            'areas': [float(s.area) for s in safras],
            'produtividades': [float(s.produtividade_estimada) for s in safras],
            'producao_total': [float(s.area * s.produtividade_estimada) for s in safras],
            # Cálculo básico de lucro: produção total * preço médio - custos
            'lucros': [float(s.area * s.produtividade_estimada * 100) for s in safras],
            'datas_plantio': [s.previsao_plantio.strftime('%d/%m/%Y') for s in safras],
            'datas_colheita': [s.previsao_colheita.strftime('%d/%m/%Y') for s in safras]
        }
    
        return render_template(
            "safra.html",
            safras=safras,
            dados_graficos=dados_graficos
        )

    # Cadastro de safra
    @app.route("/cad_safra", methods=["GET", "POST"])
    def cad_safra():
        if request.method == "POST":
            nova_safra = Safra(
                nome=request.form["nome"],
                cultura=request.form["cultura"],
                area=float(request.form["area"]),
                previsao_plantio=request.form["previsao_plantio"],
                previsao_colheita=request.form["previsao_colheita"],
                produtividade_estimada=float(request.form["produtividade_estimada"]),
            )
            db.session.add(nova_safra)
            db.session.commit()
            flash("Safra cadastrada com sucesso!")
            return redirect(url_for("safra"))
        return render_template("cad_safra.html")

    # Alterar safra
    @app.route("/alterar_safra/<int:id>", methods=["GET", "POST"])
    @login_required
    def alterar_safra(id):
        safra = Safra.query.get_or_404(id)
        
        if request.method == "POST":
            try:
                safra.nome = request.form["nome"]
                safra.cultura = request.form["cultura"]
                safra.area = float(request.form["area"])
                safra.previsao_plantio = datetime.strptime(request.form["previsao_plantio"], '%Y-%m-%d')
                safra.previsao_colheita = datetime.strptime(request.form["previsao_colheita"], '%Y-%m-%d')
                safra.produtividade_estimada = float(request.form["produtividade_estimada"])
                
                db.session.commit()
                flash("Safra alterada com sucesso!")
                return redirect(url_for("safra"))
            except Exception as e:
                flash(f"Erro ao alterar safra: {str(e)}")
                db.session.rollback()
        
        return render_template("alterar_safra.html", safra=safra)

    # Excluir safra
    @app.route("/excluir_safra/<int:id>", methods=["POST"])
    def excluir_safra(id):
        safra = Safra.query.get_or_404(id)
        db.session.delete(safra)
        db.session.commit()
        flash("Safra excluída com sucesso!")
        return redirect(url_for("safra"))