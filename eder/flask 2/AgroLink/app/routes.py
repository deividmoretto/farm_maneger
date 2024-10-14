from app.models import usuario, informacao_solo
from app import db
from app.forms import LoginForm
from datetime import timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

def init_app(app):
        
    # Rota de login e página principal
    @app.route("/", methods=["GET", "POST"])
    def index():
        form = LoginForm()

        if form.validate_on_submit():
            user = usuario.query.filter_by(email=form.email.data).first()
            
            if not user:
                flash("Email do usuário incorreto, por favor verifique!")
                return redirect(url_for("index"))
            
            elif not check_password_hash(user.senha, form.senha.data):
                flash("Senha do usuário incorreta, por favor verifique!")
                return redirect(url_for("index"))
            
            login_user(user, remember=form.remember.data, duration=timedelta(days=7))
            return redirect(url_for("inicio"))

        return render_template("index.html", form=form)

    # Rota de logout
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index")) 
    
    # Página inicial após login
    @app.route("/inicio")
    @login_required
    def inicio():        
        return render_template("inicio.html", usuarios=db.session.execute(db.select(usuario).order_by(usuario.id)).scalars())
    
    # Rota para excluir usuário
    @app.route("/excluir/<int:id>")
    def excluir_user(id):
        delete = usuario.query.filter_by(id=id).first()
        if delete:
            db.session.delete(delete)
            db.session.commit()
            flash("Usuário excluído com sucesso!")
        else:
            flash("Usuário não encontrado!")
        return redirect(url_for("inicio"))
    
    # Cadastro de novo usuário
    @app.route("/cad_user", methods=["GET", "POST"])
    def cad_user():        
        if request.method == "POST":
            user = usuario()
            user.email = request.form["email"]
            user.nome = request.form["nome"]
            user.prod = request.form["produtor"]        
            user.agro = request.form["agronomo"]
            user.senha = generate_password_hash(request.form["senha"])
            db.session.add(user)
            db.session.commit()
                            
            flash("Usuário criado com sucesso!")       
            return redirect(url_for("inicio"))
        return render_template("cad_user.html")
    
    # Atualizar informações de usuário
    @app.route("/atualiza_user/<int:id>", methods=["GET", "POST"])
    def atualiza_user(id):        
        usua = usuario.query.filter_by(id=id).first()
        if request.method == "POST":
            email = request.form["email"]
            nome = request.form["nome"]
            prod = request.form["prod"]        
            agro = request.form["agro"]
            senha = generate_password_hash(request.form["senha"])

            usuario.query.filter_by(id=id).update({
                "email": email, 
                "nome": nome, 
                "agro": agro, 
                "prod": prod, 
                "senha": senha
            })
            db.session.commit()
            flash("Informações atualizadas com sucesso!")
            return redirect(url_for("inicio"))
        return render_template("atualiza_user.html", usua=usua)
    
    # Cadastro de solo
    @app.route("/cad_solo", methods=["GET", "POST"])
    def cad_solo():
        if request.method == "POST":
            solo = informacao_solo()
            solo.usuario_id = request.form["usuario_id"]
            solo.area = request.form["area"]
            solo.tipo_solo = request.form["tipo_solo"]
            solo.ph_solo = request.form["ph_solo"]
            solo.materia_organica = request.form["materia_organica"]
            solo.ctc = request.form["ctc"]
            solo.nivel_nitrogenio = request.form["nivel_nitrogenio"]
            solo.nivel_fosforo = request.form["nivel_fosforo"]
            solo.nivel_potassio = request.form["nivel_potassio"]
            solo.aplicacao_recomendada = request.form["aplicacao_recomendada"]
            db.session.add(solo)
            db.session.commit()
            flash("Informações de solo cadastradas com sucesso!")
            return redirect(url_for("cad_solo"))

        return render_template("cad_solo.html")