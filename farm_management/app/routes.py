from app.models import usuario
from app.models import contabilidade
from app import db
from app.forms import LoginForm
from datetime import timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

def init_app(app):
        
    #@app.route("/")
    #def principal():        
        #return render_template("seu_job/index.html")
    #Entrada do usuario
    @app.route("/", methods=["GET", "POST"])
    def index():
        form = LoginForm()

        if form.validate_on_submit():
        #if request.method == "POST":
            user = usuario.query.filter_by(email=form.email.data).first()
            
            if not user:
                flash("Email do usuario incorreto, por favor verifique!")
                return redirect(url_for("index"))
                #return render_template("user_inv.html")
            
            elif not check_password_hash(user.senha, form.senha.data):
                flash("Senha de usuario incorreto, por favor verifique")
                return redirect(url_for("index"))
                #return render_template("user_inv.html")           
            
            login_user(user, remember=form.remember.data, duration=timedelta(days=7))
            #login_user(user)
            return redirect(url_for("inicio"))

        return render_template("index.html", form=form)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index")) 
    
    
    @app.route("/inicio")
    @login_required
    def inicio():        
        return render_template("/inicio.html", usuarios=db.session.execute(db.select(usuario).order_by(usuario.id)).scalars())
    
   
    @app.route("/excluir/<int:id>")
    def excluir_user(id):
        delete=usuario.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("inicio"))
    

    @app.route("/cad_user", methods=["GET", "POST"])
    def cad_user():        
        if request.method == "POST":
            user = usuario()
            user.email = request.form["email"]
            user.nome = request.form["nome"]        
            user.senha = generate_password_hash(request.form["senha"])
            db.session.add(user)
            db.session.commit()
                            
            flash("Usuario criado com sucesso!")       
            return redirect(url_for("cad_user"))
        return render_template("cad_user.html")
    
   
    @app.route("/atualiza_user")
    def atualiza_user():        
        return render_template("atualiza_user.html")

       
    @app.route("/conta")
    
    def conta():        
        return render_template("/conta01.html", contil=db.session.execute(db.select(contabilidade).order_by(contabilidade.id)).scalars())
        
    @app.route("/excluir_cont/<int:id>")
    def excluir_cont(id):
        delete=contabilidade.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("conta"))
    
    @app.route("/cad_conta", methods=["GET", "POST"])
    def cad_conta():        
        if request.method == "POST":
            cont = contabilidade()
            cont.fatura = request.form["fatura"]
            cont.fiscal = request.form["fiscal"]           
            db.session.add(cont)
            db.session.commit()
                            
            flash("Dados contabil criado com sucesso!")       
            return redirect(url_for("cad_conta"))
        return render_template("cad_conta.html")
    
    @app.route("/atualiza_conta/<int:id>", methods=["GET", "POST"])
    def atualiza_conta(id):  
        contas01 = contabilidade.query.filter_by(id=id).first()      
        if request.method == "POST":
            fatura_contabil = request.form["fatura"]
            fiscal_contabil = request.form["fiscal"]
                            
            flash("Dados contabil alterado com sucesso!")
            
            contas01.query.filter_by(id=id).update({"fatura":fatura_contabil, "fiscal":fiscal_contabil})       
            db.session.commit()
            return redirect(url_for("conta"))
        return render_template("atualiza_conta.html", conts = contas01)

   