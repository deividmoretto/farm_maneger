from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from app import db
from app.models import usuario, informacao_solo, Safra
from app.forms import LoginForm


def init_app(app):
    # Rota de login
    @app.route("/", methods=["GET", "POST"])
    def index():
        form = LoginForm()
        if form.validate_on_submit():
            user = usuario.query.filter_by(email=form.email).first()
            if not user or not check_password_hash(user.senha, form.senha.data):
                flash("Email ou senha incorretos!")
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
        usuarios = usuario.query.all()
        return render_template("inicio.html", usuarios=usuarios)

    # Página de gestão de solo
    @app.route("/solo")
    @login_required
    def solo():
        solos = informacao_solo.query.all()
        return render_template("solo.html", solos=solos)

    # Cadastro de solo
    @app.route("/cad_solo", methods=["GET", "POST"])
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
                aplicacao_recomendada=request.form["aplicacao_recomendada"],
            )
            db.session.add(solo)
            db.session.commit()
            flash("Informações de solo cadastradas com sucesso!")
            return redirect(url_for("solo"))
        return render_template("cad_solo.html")

    # Página de gestão de safra
    @app.route("/safra")
    def safra():
        safras = Safra.query.all()

        # Processar dados para os gráficos
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        produtividade_mensal = [0] * len(meses)
        lucro_mensal = [0] * len(meses)

        for i, mes in enumerate(meses):
            produtividade_mensal[i] = sum(
                safra.produtividade_estimada for safra in safras
            )
            lucro_mensal[i] = sum(
                safra.produtividade_estimada * safra.area for safra in safras
            )

        return render_template(
            "safra.html",
            safras=safras,
            meses=meses,
            produtividade_mensal=produtividade_mensal,
            lucro_mensal=lucro_mensal,
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
    def alterar_safra(id):
        safra = Safra.query.get_or_404(id)
        if request.method == "POST":
            safra.nome = request.form["nome"]
            safra.cultura = request.form["cultura"]
            safra.area = float(request.form["area"])
            safra.previsao_plantio = request.form["previsao_plantio"]
            safra.previsao_colheita = request.form["previsao_colheita"]
            safra.produtividade_estimada = float(request.form["produtividade_estimada"])
            db.session.commit()
            flash("Safra atualizada com sucesso!")
            return redirect(url_for("safra"))
        return render_template("alterar_safra.html", safra=safra)

    # Excluir safra
    @app.route("/excluir_safra/<int:id>", methods=["POST"])
    def excluir_safra(id):
        safra = Safra.query.get_or_404(id)
        db.session.delete(safra)
        db.session.commit()
        flash("Safra excluída com sucesso!")
        return redirect(url_for("safra"))