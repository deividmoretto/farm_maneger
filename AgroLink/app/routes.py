from app.models import usuario, informacao_solo
from app import db
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm

def init_app(app):
    @app.route("/")
    def inicio():
        # Exemplo de renderização de template
        return render_template("inicio.html")

    @app.route("/conta")
    def conta():
        # Lista de informações de solo cadastradas
        informacoes = db.session.execute(db.select(informacao_solo).order_by(informacao_solo.id)).scalars()
        return render_template("conta01.html", informacoes=informacoes)
    
    @app.route("/excluir/<int:id>")
    def excluir_user(id):
        # Excluir um usuário pelo ID
        delete = usuario.query.filter_by(id=id).first()
        if delete:
            db.session.delete(delete)
            db.session.commit()
        return redirect(url_for("inicio"))
    
    @app.route("/excluir_solo/<int:id>")
    def excluir_solo(id):
        # Excluir uma informação de solo pelo ID
        delete = informacao_solo.query.filter_by(id=id).first()
        if delete:
            db.session.delete(delete)
            db.session.commit()
        return redirect(url_for("conta"))
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()  # Cria a instância do formulário
        
        if form.validate_on_submit():  # Verifica se o formulário foi submetido corretamente
            email = form.email.data
            senha = form.senha.data

            # Procurar usuário no banco de dados pelo email
            user = usuario.query.filter_by(email=email).first()

            if user and check_password_hash(user.senha, senha):  # Verificar se a senha bate
                login_user(user)  # Fazer login do usuário
                flash("Login bem-sucedido!", "success")  # Mensagem de sucesso
                return redirect(url_for("inicio"))  # Redirecionar para a página inicial

            flash("Email ou senha inválidos. Tente novamente.", "danger")  # Mensagem de erro
        
        return render_template("login.html", form=form)
    
    @app.route("/cad_user", methods=["GET", "POST"])
    def cad_user():
        if request.method == "POST":
            email = request.form.get("email")
            nome = request.form.get("nome")
            senha = request.form.get("senha")
            agro = request.form.get("agro", "Agrônomo")
            prod = request.form.get("prod", "Produtor")

            if not email or not nome or not senha:
                flash("Todos os campos são obrigatórios!", "danger")
                return redirect(url_for("cad_user"))

            # Verificar se o email já está cadastrado
            if usuario.query.filter_by(email=email).first():
                flash("Esse email já está registrado. Tente outro.", "danger")
                return redirect(url_for("cad_user"))

            senha_hash = generate_password_hash(senha, method='sha256')

            novo_usuario = usuario(email=email, nome=nome, senha=senha_hash, agro=agro, prod=prod)

            try:
                db.session.add(novo_usuario)
                db.session.commit()  # Commit para salvar no banco
                flash("Usuário cadastrado com sucesso!", "success")
            except Exception as e:
                db.session.rollback()  # Desfaz a transação se ocorrer um erro
                flash(f"Ocorreu um erro ao cadastrar o usuário: {e}", "danger")

            return redirect(url_for("inicio"))

        return render_template("cad_user.html")

    @app.route("/atualiza_user/<int:id>", methods=["GET", "POST"])
    def atualiza_user(id):
        user = usuario.query.get_or_404(id)
        
        if request.method == "POST":
            user.email = request.form["email"]
            user.nome = request.form["nome"]
            user.senha = generate_password_hash(request.form["senha"], method='sha256')
            db.session.commit()
            return redirect(url_for("inicio"))
        
        return render_template("atualiza_user.html", user=user)
    
    @app.route("/cad_solo", methods=["GET", "POST"])
    def cad_solo():
        if request.method == "POST":
            usuario_id = request.form["usuario_id"]
            area = request.form["area"]
            tipo_solo = request.form["tipo_solo"]
            ph_solo = request.form["ph_solo"]
            materia_organica = request.form["materia_organica"]
            ctc = request.form["ctc"]
            nivel_nitrogenio = request.form["nivel_nitrogenio"]
            nivel_fosforo = request.form["nivel_fosforo"]
            nivel_potassio = request.form["nivel_potassio"]
            aplicacao_recomendada = request.form["aplicacao_recomendada"]
            
            # Criar uma nova informação de solo
            nova_informacao = informacao_solo(
                usuario_id=usuario_id, area=area, tipo_solo=tipo_solo, ph_solo=ph_solo, 
                materia_organica=materia_organica, ctc=ctc, nivel_nitrogenio=nivel_nitrogenio, 
                nivel_fosforo=nivel_fosforo, nivel_potassio=nivel_potassio, aplicacao_recomendada=aplicacao_recomendada)
            
            db.session.add(nova_informacao)
            db.session.commit()
            return redirect(url_for("conta"))
        
        # Listar usuários para associar o solo ao agrônomo
        usuarios = usuario.query.all()
        return render_template("cad_solo.html", usuarios=usuarios)