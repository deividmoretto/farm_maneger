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
    
    @app.route("/")
    def inicio():        
        return render_template("/inicio.html", usuarios=db.session.execute(db.select(usuario).order_by(usuario.id)).scalars())

    @app.route("/conta")
    def conta():        
        return render_template("/conta01.html", contil=db.session.execute(db.select(contabilidade).order_by(contabilidade.id)).scalars())
    
    @app.route("/excluir/<int:id>")
    def excluir_user(id):
        delete=usuario.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("inicio"))
    
    @app.route("/excluir_conta/<int:id>")
    def excluir_conta(id):
        delete=contabilidade.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("conta"))
    
    @app.route("/cad_user")
    def cad_user():        
        return render_template("cad_user.html")
    
    @app.route("/atualiza_user")
    def atualiza_user():        
        return render_template("atualiza_user.html")
    
    
    