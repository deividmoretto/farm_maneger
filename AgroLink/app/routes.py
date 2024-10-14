from app.models import informacao_solo
from app.models import usuario
from app import db
from app.forms import LoginForm
from datetime import timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
from flask_login import login_required, login_user, logout_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

def init_app(app):
    mail = Mail(app)
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
            
            elif user.status != "on":
                flash("Usuario desativado no sistema Palmaflex,por favor verifique com o administrador do sistema")
                return redirect(url_for("index"))
            
            
            login_user(user, remember=form.remember.data, duration=timedelta(days=7))
            #login_user(user)
            return redirect(url_for("pagina_inicial"))

        return render_template("index.html", form=form)

    #Saida do usuario do sistema
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))    
    

    @app.route("/pagina_inicial")
    #@login_required
    def pagina_inicial():        
        return render_template("pagina.html")
    
    #Tela de operações de cadastro de organizações, leitura, inclusão, exclusão e alteração.
    @app.route("/inicio")
    @login_required
    def inicio():        
        return render_template("inicio.html", organiza=db.session.execute(db.select(organizacao).order_by(organizacao.id)).scalars())

    @app.route("/organiza/<int:id>")
    @login_required
    def unique_organi(id):
        return render_template("organiza.html", organi_uni=organizacao.query.get(id))
    
    @app.route("/organi_consulta")    
    @jwt_required()
    def organi_consulta(): 
          
        organi_nome = request.args.get('organi_nome')
        organi_cnpj = request.args.get('organi_cnpj')
        organi_telefone = request.args.get('organi_telefone')
        organi_email = request.args.get('organi_email')
        organi_representante = request.args.get('organi_representante')
        organi_endereco = request.args.get('organi_endereco')
        organi_status = request.args.get('organi_status')
        organi_nivel = request.args.get('organi_nivel') 
             
        if organi_nome:
            organi = organizacao.query.filter(organizacao.nome.contains(organi_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_cnpj:
            organi = organizacao.query.filter(organizacao.cnpj.contains(organi_cnpj))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_telefone:
            organi = organizacao.query.filter(organizacao.telefone.contains(organi_telefone))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_email:
            organi = organizacao.query.filter(organizacao.email.contains(organi_email))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_representante:
            organi = organizacao.query.filter(organizacao.representante.contains(organi_representante))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_endereco:
            organi = organizacao.query.filter(organizacao.endereco.contains(organi_endereco))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_status:
            organi = organizacao.query.filter(organizacao.status.contains(organi_status))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif organi_nivel:
            organi = organizacao.query.filter(organizacao.nivel.contains(organi_nivel))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        else:
            organi=db.session.execute(db.select(organizacao).order_by(organizacao.id)).scalars() 

        organi_json = []
        for organ in organi:
            organ_dict = {'id': organ.id, 
                           'nome': organ.nome,
                           'cnpj': organ.cnpj,
                           'telefone': organ.telefone,
                           'email': organ.email,
                           'representante': organ.representante,
                           'endereco': organ.endereco,
                           'status': organ.status,
                           'nivel': organ.nivel,
                           'data': organ.data                                                      
                         }
            organi_json.append(organ_dict)

        return jsonify(organi_json)  

    @app.route("/cad_organi", methods=["GET", "POST"])
    #@login_required
    def cad_organi():
        if request.method == "POST":
            organi = organizacao()        
            organi.nome = request.form["nome_organi"]
            organi.cnpj = request.form["cnpj"]        
            organi.telefone = request.form["telefone"]
            organi.email = request.form["email"]
            organi.endereco = request.form["endere"]
            organi.representante = request.form["representa"]
            organi.nivel = request.form["nivel"]
                     
            db.session.add(organi)
            db.session.commit()
             
            flash("Usuario criado com sucesso!")       
            return redirect(url_for("cad_organi"))
        return render_template("cad_organi.html", organiza=organizacao.query.all())

    @app.route("/organiza/atualiza/<int:id>", methods=["GET", "POST"])
    def atualiza_organi(id):
        organi=organizacao.query.filter_by(id=id).first()
        if request.method == "POST":
            nome = request.form["nome_organi"]
            cnpj = request.form["cnpj"]        
            telefone = request.form["telefone"]
            email = request.form["email"]
            endereco = request.form["endere"]
            representante = request.form["representa"]
            nivel_acesso = request.form["nivel"]
            
            organi.query.filter_by(id=id).update({"nome":nome, "cnpj":cnpj, "email":email, "telefone":telefone, "endereco":endereco, "representante":representante, "nivel":nivel_acesso })
            db.session.commit()
            return redirect(url_for("inicio"))

        return render_template("atualiza_organi.html", organi=organi, organiza=organizacao.query.all())

    @app.route("/organiza/excluir/<int:id>")
    @login_required
    def excluir_organi(id):
        delete_organi=organizacao.query.filter_by(id=id).first()
        db.session.delete(delete_organi)
        db.session.commit()
        return redirect(url_for("inicio"))

    #Tela de operações de cadastro de usuarios, leitura, inclusão, exclusão e alteração.
    @app.route("/usuarios")
    @login_required
    def usuarios():
        return render_template("/usuarios/usuarios.html", usuarios=db.session.execute(db.select(usuario).order_by(usuario.id)).scalars())
    @app.route("/usuario/<int:id>")
    @login_required
    def unique(id):
        return render_template("/usuarios/usuario.html", usuario=usuario.query.get(id), user_organi = db.session.query(usuario).join(organizacao).filter(usuario.id==id).first())
    
    @app.route("/user_consulta")    
    @jwt_required()
    def user_consulta(): 
              
        user_email = request.args.get('user_email')
        user_organi_id = request.args.get('user_organi_id')
        user_nome = request.args.get('user_nome')
        user_cpf = request.args.get('user_cpf')
        user_endereco = request.args.get('user_endereco')
        user_status = request.args.get('user_status')
        user_nivel = request.args.get('user_nivel')
        user_senha = request.args.get('user_senha') 
        user_token = request.args.get('user_token')   
                     
        if user_email and user_senha:
            user = usuario.query.filter_by(email=user_email, senha=user_senha).first()

            if user:
                # usuario autenticado, retornar JSON com seus dados
                dados_user = {
                                    'id': user.id,
                                    'organi_user_id':user.organi_user_id,
                                    'email': user.email, 
                                    'nome': user.nome,
                                    'cpf': user.cpf,
                                    'endereco': user.endereco,
                                    'telefone': user.telefone,                         
                                    'intervalo_auto': user.intervalo_auto,
                                    'notifica_inatividade': user.notifica_inatividade,
                                    'alerta_valores': user.alerta_valores,
                                    'valores_fora': user.valores_fora,                         
                                    'status': user.status,
                                    'nivel': user.nivel,
                                    'senha': user.senha,
                                    'token': user.token,
                                    'data': user.data 
                                }

                return jsonify(dados_user)                               
            else:
                return jsonify({'menssagem': 'Usuario ou senha invalido.'}), 400
        elif user_organi_id:
            users = usuario.query.filter(usuario.organi_user_id.contains(user_organi_id))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif user_cpf:
            users = usuario.query.filter(usuario.cpf.contains(user_cpf))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif user_nome:
            users = usuario.query.filter(usuario.nome.contains(user_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif user_endereco:
            users = usuario.query.filter(usuario.endereco.contains(user_endereco))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif user_status:
            users = usuario.query.filter(usuario.status.contains(user_status))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif user_nivel:
            users = usuario.query.filter(usuario.nivel.contains(user_nivel))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif user_token:
            users = usuario.query.filter(usuario.token.contains(user_token))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        else:
            return jsonify({'menssagem': 'Dados do usuario não encontrado.'}), 400

        user_json = []
        for user in users:
            user_dict = {'id': user.id,
                         'organi_user_id':user.organi_user_id,
                         'email': user.email, 
                         'nome': user.nome,
                         'cpf': user.cpf,
                         'endereco': user.endereco,
                         'telefone': user.telefone,                         
                         'intervalo_auto': user.intervalo_auto,
                         'notifica_inatividade': user.notifica_inatividade,
                         'alerta_valores': user.alerta_valores,
                         'valores_fora': user.valores_fora,                         
                         'status': user.status,
                         'nivel': user.nivel,
                         'senha': user.senha,
                         'token': user.token,
                         'data': user.data                                                      
                         }
            user_json.append(user_dict)

        return jsonify(user_json)  

      
           
       

    @app.route("/cad_user", methods=["GET", "POST"])
    #@login_required
    def cad_user():
        if request.method == "POST":
            nome_usuario = request.form["nome"]
            email_usuario = request.form["email"]
            user = usuario()
            user.email = request.form["email"]
            user.nome = request.form["nome"]        
            user.organi_user_id = request.form["organi"]
            user.endereco = request.form["endere"]
            user.cpf = request.form["cpf"]
            user.nivel = request.form["nivel"]
            user.intervalo_auto = request.form["intervalo_auto"]
            #user.notifica_inatividade = request.form["notifica_inatividade"]
            #user.alerta_valores = request.form["alerta_valores"]
            #user.valores_fora = request.form["valores_fora"] 
            user.notifica_inatividade = request.form.get("notifica_inatividade")
            user.alerta_valores = request.form.get("alerta_valores")
            user.valores_fora = request.form.get("valores_fora")
            user.status = request.form.get("status")                           
            #user.senha = generate_password_hash(request.form["senha"])
            db.session.add(user)
            db.session.commit()
            #return redirect("/usuarios")
            # Gere um token JWT para o usuário
            token = create_access_token(identity=user.email)

            # Grave o token JWT no banco de dados
            user.token = token
            db.session.commit()
            msg = Message(                
                subject="Bem vindo(a) ao sistema Palmaflex", 
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email_usuario],
                html=render_template("email/email.html", nome_user=nome_usuario, email_user=email_usuario, email_send=usuario.query.filter_by(email=email_usuario).first())
            )
            mail.send(msg)
    
            flash("Usuario criado com sucesso e enviado por email!")       
            return redirect(url_for("cad_user"))
        return render_template("/usuarios/cad_user.html", organiza=organizacao.query.all())
        

    @app.route("/registra_email/<int:id>", methods=["GET", "POST"])
    #@login_required
    def registro(id):
        reg=usuario.query.filter_by(id=id).first()
        nome = reg.nome
        email_user = reg.email
        if request.method == "POST":            
            senha = generate_password_hash(request.form["senha"])

            reg.query.filter_by(id=id).update({"senha":senha})
            db.session.commit()           
    
            flash("Senha criado com sucesso!")       
            return redirect(url_for("index"))
        return render_template("/email/registra.html", reg=reg)

    @app.route("/usuario/atualiza/<int:id>", methods=["GET", "POST"])
    def atualiza_user(id):
        usua=usuario.query.filter_by(id=id).first()
        if request.method == "POST":
            nome_usuario = request.form["nome"]
            email_usuario = request.form["email"]        
            organi_user = request.form["organi"]
            endereco = request.form["endere"]
            cpf = request.form["cpf"]
            nivel_usuario = request.form["nivel"]
            intervalo_automa = request.form["intervalo_auto"]
            notifi_inatividade = request.form.get("notifica_inatividade")
            alerta_valor = request.form.get("alerta_valores")
            valor_fora = request.form.get("valores_fora")
            status = request.form.get("status")     
            #senha = generate_password_hash(request.form["senha"])
            msg = Message(                
                subject="Alteração do usuario Palmaflex", 
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email_usuario],
                html=render_template("email/email_altera.html", nome_user=nome_usuario, email_user=email_usuario, email_send=usuario.query.filter_by(email=email_usuario).first())
            )
            mail.send(msg)

            flash("Usuario alterado com sucesso e enviado por email!")     

            usua.query.filter_by(id=id).update({"email":email_usuario, "nome":nome_usuario, "organi_user_id":organi_user, "endereco":endereco, "cpf":cpf, "nivel":nivel_usuario, "intervalo_auto":intervalo_automa, 
                                                "notifica_inatividade":notifi_inatividade, "alerta_valores": alerta_valor, "valores_fora":valor_fora, "status":status })
            db.session.commit()
            return redirect(url_for("usuarios"))
        return render_template("/usuarios/atualiza_user.html", usua=usua, user_organi = db.session.query(usuario).join(organizacao).filter(usuario.id==id).first(), organiza=organizacao.query.all()) 

    @app.route("/usuario/excluir/<int:id>")
    @login_required
    def excluir_user(id):
        delete=usuario.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("usuarios"))

    #Tela de operações de cadastro de coletores, leitura, inclusão, exclusão e alteração.
    @app.route("/coletores")
    @login_required
    def coletores():
        return render_template("/coletores/coletores.html", coletores=db.session.execute(db.select(coletor).order_by(coletor.id)).scalars())

    @app.route("/coletores/<int:id>")
    @login_required
    def unique_coleta(id):
        return render_template("/coletores/coletor.html", coleta=coletor.query.get(id), coleta_organi = db.session.query(coletor).join(organizacao).filter(coletor.id==id).first())
    
    @app.route("/coletores_consulta")
    #@jwt_required()
    def coleta_consulta():       
        coletores_id = request.args.get('coletores_id')
        coletores_tag = request.args.get('coletores_tag')
        coletores_serie = request.args.get('coletores_serie')
        coletores_modelo = request.args.get('coletores_modelo')               
        if coletores_id:
            coleta = coletor.query.filter(coletor.id_dispositivo.contains(coletores_id))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif coletores_tag:
            coleta = coletor.query.filter(coletor.tag.contains(coletores_tag))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif coletores_serie:
            coleta = coletor.query.filter(coletor.serie.contains(coletores_serie))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif coletores_modelo:
            coleta = coletor.query.filter(coletor.modelo.contains(coletores_modelo))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        else:
            #coleta=db.session.execute(db.select(coletor).order_by(coletor.id)).scalars() 
            # Retornar resposta em JSON indicando que a consulta está incompleta
            return jsonify({'menssagem': 'Dados do coletor inexistente.'}), 400
        coletores_json = []
        for coletores in coleta:
            coletor_dict = {'id': coletores.id, 
                            'f': coletores.id_dispositivo,
                            'tag': coletores.tag,
                            'serie': coletores.serie,
                            'modelo': coletores.modelo,
                            'firmware': coletores.firmware,
                            'hardware': coletores.hardware,
                            'dado_irriga': coletores.dado_irriga,
                            'efici_sistema': coletores.efici_sistema,
                            'vazao_emissor': coletores.vazao_emissor,
                            'vazao_sistema_pivo': coletores.vazao_sistema_pivo,
                            'espa_linha': coletores.espa_linha,
                            'espa_emissores': coletores.espa_emissores,
                            'proje_sala': coletores.proje_sala,
                            'area_pivo': coletores.area_pivo,
                            'tempo_zero_cem': coletores.tempo_zero_cem,
                            'tensao_critica_irriga': coletores.tensao_critica_irriga,
                            'ponto_permanente_irriga': coletores.ponto_permanente_irriga,
                            'hidrico_irriga': coletores.hidrico_irriga,
                            'data_irriga': coletores.data_irriga,
                            'tipo_solo': coletores.tipo_solo,
                            'nome_curva': coletores.nome_curva,
                            'argila': coletores.argila,
                            'areia': coletores.areia,
                            'selte': coletores.selte,
                            'materia_organica': coletores.materia_organica,
                            'data_cultura': coletores.data_cultura,
                            'cultura': coletores.cultura,
                            'espa_linha_cultura': coletores.espa_linha_cultura,
                            'espa_planta_cultura': coletores.espa_planta_cultura,
                            'tensao_otima_60': coletores.tensao_otima_60,
                            'coleta.tensao_critica_60': coletores.tensao_critica_60,
                            'coleta.tensao_otima_20': coletores.tensao_otima_20,
                            'coleta.tensao_critica_20': coletores.tensao_critica_20,
                            'data': coletores.data                            
                            }
            coletores_json.append(coletor_dict)

        return jsonify(coletores_json)   


    @app.route("/cad_coleta", methods=["GET", "POST"])
    #@login_required
    def cad_coleta():
        if request.method == "POST":
            coleta = coletor()
            coleta.id_dispositivo = request.form["dispositivo"]
            coleta.tag = request.form["tag"]
            coleta.serie = request.form["serie"]        
            coleta.organi_coletor_id = request.form["organi"]
            coleta.modelo = request.form["modelo"]
            coleta.concentrador = request.form["concentrador"]            
            coleta.firmware = request.form["firmware"]
            coleta.hardware = request.form["hardware"]
            coleta.dado_irriga = request.form["dado_irriga"]
            coleta.efici_sistema = request.form["efici_sistema"]
            coleta.vazao_emissor = request.form["vazao_emissor"]
            coleta.vazao_sistema_pivo = request.form["vazao_sistema_pivo"]
            coleta.espa_linha = request.form["espa_linha"]
            coleta.espa_emissores = request.form["espa_emissores"]
            coleta.proje_sala = request.form["proje_sala"]
            coleta.area_pivo = request.form["area_pivo"]
            coleta.tempo_zero_cem = request.form["tempo_zero_cem"]
            coleta.tensao_critica_irriga = request.form["tensao_critica_irriga"]
            coleta.ponto_permanente_irriga = request.form["ponto_permanente_irriga"]
            coleta.hidrico_irriga = request.form["hidrico_irriga"]
            coleta.data_irriga = request.form["data_irriga"]
            coleta.tipo_solo = request.form["tipo_solo"]
            coleta.nome_curva = request.form["nome_curva"]
            coleta.argila = request.form["argila"]
            coleta.areia = request.form["areia"]        
            coleta.selte = request.form["selte"]
            coleta.materia_organica = request.form["materia_organica"]
            coleta.data_cultura = request.form["data_cultura"]
            coleta.cultura = request.form["cultura"]
            coleta.espa_linha_cultura = request.form["espa_linha_cultura"]
            coleta.espa_planta_cultura = request.form["espa_planta_cultura"]
            coleta.tensao_otima_60 = request.form["tensao_otima_60"]
            coleta.tensao_critica_60 = request.form["tensao_critica_60"]
            coleta.tensao_otima_20 = request.form["tensao_otima_20"]
            coleta.tensao_critica_20 = request.form["tensao_critica_20"]
            db.session.add(coleta)
            db.session.commit()
            #return redirect("/usuarios") 
            flash("Coletor criado com sucesso!")       
            return redirect(url_for("cad_coleta"))
        return render_template("/coletores/cad_coleta.html", organiza=organizacao.query.all(), retensao=solo_curva.query.all(), irrigas=irrigacao.query.all(), culturas=cultura.query.all())
        

    @app.route("/coletores/excluir/<int:id>")
    @login_required
    def excluir_coleta(id):
        delete=coletor.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("coletores"))

    @app.route("/coletores/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_coleta(id):
        coleta=coletor.query.filter_by(id=id).first()
        if request.method == "POST": 
            dispositivo_coleta = request.form["dispositivo"]       
            tag = request.form["tag"]
            serie = request.form["serie"]        
            organi_coletor = request.form["organi"]
            modelo = request.form["modelo"]
            concentrador = request.form["concentrador"]
            firmware = request.form["firmware"]
            hardware = request.form["hardware"]
            argila = request.form["argila"]
            areia = request.form["areia"]
            selte = request.form["selte"]               
            materia_organica = request.form["materia_organica"]
            dado_irriga = request.form["dado_irriga"]
            tensao_critica_irriga = request.form["tensao_critica_irriga"]
            ponto_permanente_irriga = request.form["ponto_permanente_irriga"]
            hidrico_irriga = request.form["hidrico_irriga"]
            data_irriga = request.form["data_irriga"]
            tipo_solo = request.form["tipo_solo"]
            nome_curva = request.form["nome_curva"]            
            data_cultura = request.form["data_cultura"]
            culturas = request.form["cultura"]            
            espa_linha_cultura = request.form["espa_linha_cultura"]
            espa_planta_cultura = request.form["espa_planta_cultura"]
            tensao_otima_60 = request.form["tensao_otima_60"]
            tensao_critica_60 = request.form["tensao_critica_60"]
            tensao_otima_20 = request.form["tensao_otima_20"]
            tensao_critica_20 = request.form["tensao_critica_20"]
            db.session.add(coleta)
            db.session.commit()                    
            coleta.query.filter_by(id=id).update({"id_dispositivo":dispositivo_coleta, "tag":tag, "serie":serie, "organi_coletor_id":organi_coletor, "modelo":modelo, "concentrador":concentrador, "firmware":firmware, "hardware":hardware, "argila":argila, "areia":areia, "selte":selte, "materia_organica":materia_organica, "dado_irriga":dado_irriga, "tensao_critica_irriga":tensao_critica_irriga, "ponto_permanente_irriga":ponto_permanente_irriga, "hidrico_irriga":hidrico_irriga, "data_irriga":data_irriga, "tipo_solo":tipo_solo, "nome_curva":nome_curva, "data_cultura":data_cultura, "cultura":culturas, 
                                                  "espa_linha_cultura":espa_linha_cultura, "espa_planta_cultura":espa_planta_cultura, "tensao_otima_60":tensao_otima_60,"tensao_critica_60":tensao_critica_60, "tensao_otima_20":tensao_otima_20, "tensao_critica_20":tensao_critica_20 })
            db.session.commit()
            return redirect(url_for("coletores"))
        return render_template("/coletores/atualiza_coletores.html", coleta=coleta, organiza=organizacao.query.all(), coleta_organi = db.session.query(coletor).join(organizacao).filter(coletor.id==id).first(), retensao=solo_curva.query.all(), irrigas=irrigacao.query.all(), culturas=cultura.query.all()) 

    #Tela de operações de cadastro de sensores, leitura, inclusão, exclusão e alteração.
    @app.route("/sensores")
    @login_required
    def sensores():
              
        return render_template("/sensores/sensor.html", sensores = db.session.execute(db.select(sensor).order_by(sensor.id)).scalars() )

    @app.route("/sensores/<int:id>")
    @login_required
    def unique_sensor(id):
        return render_template("/sensores/sensores.html", sensores=sensor.query.get(id), sensor_organi = db.session.query(sensor).join(organizacao).filter(sensor.id==id).first())
    
    @app.route("/sensores_consulta")
    
    @jwt_required()
    def sensor_consulta():       
        sensor_id = request.args.get('sensor_id')
        sensor_tag = request.args.get('sensor_tag')
        sensor_nome = request.args.get('sensor_nome')
        sensor_serie = request.args.get('sensor_serie')
        sensor_modelo = request.args.get('sensor_modelo')
        sensor_concentrador = request.args.get('sensor_concentrador') 
        sensor_coletor = request.args.get('sensor_coletor')
        sensor_status = request.args.get('sensor_status')
        sensor_alerta_inf = request.args.get('sensor_alerta_inf')
        sensor_alerta_sup = request.args.get('sensor_alerta_sup')
        sensor_alarme_inf = request.args.get('sensor_alarme_inf')
        sensor_alarme_sup = request.args.get('sensor_alarme_sup')
        sensor_correcao = request.args.get('sensor_correcao')       
        if sensor_id:
            sensores = sensor.query.filter(sensor.id_dispositivo.contains(sensor_id))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_tag:
            sensores = sensor.query.filter(sensor.tag.contains(sensor_tag))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_nome:
            sensores = sensor.query.filter(sensor.nome.contains(sensor_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_serie:
            sensores = sensor.query.filter(sensor.serie.contains(sensor_serie))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_modelo:
            sensores = sensor.query.filter(sensor.modelo.contains(sensor_modelo))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_concentrador:
            sensores = sensor.query.filter(sensor.concentrador.contains(sensor_concentrador))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_coletor:
            sensores = sensor.query.filter(sensor.coletor.contains(sensor_coletor))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_status:
            sensores = sensor.query.filter(sensor.status.contains(sensor_status))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_alerta_inf:
            sensores = sensor.query.filter(sensor.alerta_inferior.contains(sensor_alerta_inf))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_alerta_sup:
            sensores = sensor.query.filter(sensor.alerta_superior.contains(sensor_alerta_sup))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_alarme_inf:
            sensores = sensor.query.filter(sensor.alarme_inferior.contains(sensor_alarme_inf))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_alarme_sup:
            sensores = sensor.query.filter(sensor.alarme_superior.contains(sensor_alarme_sup))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif sensor_correcao:
            sensores = sensor.query.filter(sensor.correcao.contains(sensor_correcao))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        else:
            sensores=db.session.execute(db.select(sensor).order_by(sensor.id)).scalars() 

        sensor_json = []
        for sensors in sensores:
            sensor_dict = {'id': sensors.id, 
                           'id_dispositivo': sensors.id_dispositivo,
                           'tag': sensors.tag,
                           'nome': sensors.nome,
                           'serie': sensors.serie,
                           'modelo': sensors.modelo,
                           'concentrador': sensors.concentrador,
                           'coletor': sensors.coletor,
                           'status': sensors.status,
                           'alerta_inferior': sensors.alerta_inferior,
                           'alerta_superior': sensors.alerta_superior,
                           'alarme_inferior': sensors.alarme_inferior,
                           'alarme_superior': sensors.alarme_superior,
                           'correcao': sensors.correcao,
                           'data': sensors.data                           
                                 }
            sensor_json.append(sensor_dict)

        return jsonify(sensor_json)   


    @app.route("/cad_sensor", methods=["GET", "POST"])
    @login_required
    def cad_sensor():
        if request.method == "POST":
            senso = sensor()
            senso.id_dispositivo = request.form["dispositivo"]
            senso.tag = request.form["tag"]            
            senso.serie = request.form["serie"]        
            senso.organi_sensor_id = request.form["organi"]
            senso.modelo_sensor_id = request.form["modelo"]
            #senso.modelo = request.form["modelo"]
            senso.concentrador = request.form["concentrador"]
            senso.coletor = request.form["coletor"]
            #if request.form["alerta_inferior"] != '':
            senso.alerta_inferior = request.form["alerta_inferior"]
            #if request.form["alerta_superior"] != '':
            senso.alerta_superior = request.form["alerta_superior"]
            #if request.form["alarme_inferior"] != '':
            senso.alarme_inferior = request.form["alarme_inferior"]
            #if request.form["alarme_superior"] != '':
            senso.alarme_superior = request.form["alarme_superior"]
            senso.correcao = request.form["correcao"]
            senso.status = request.form.get("ativo")         
            db.session.add(senso)
            db.session.commit()            
            flash("Sensor criado com sucesso!")       
            return redirect(url_for("cad_sensor"))
        return render_template("/sensores/cad_sensor.html", organiza=organizacao.query.all(), modelos=modelo.query.all())

    @app.route("/sensores/excluir/<int:id>")
    @login_required
    def excluir_sensor(id):
        deletes=sensor.query.filter_by(id=id).first()
        db.session.delete(deletes)
        db.session.commit()
        return redirect(url_for("sensores"))

    @app.route("/sensores/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_sensores(id):
        sensors=sensor.query.filter_by(id=id).first()
        if request.method == "POST":
            dispositivo_sensor = request.form["dispositivo"]        
            tag = request.form["tag"]            
            serie = request.form["serie"]        
            organi_sensor = request.form["organi"]
            modelos = request.form["modelo"]
            concentrador = request.form["concentrador"]
            coletor = request.form["coletor"]
            alerta_inferior = request.form["alerta_inferior"]
            alerta_superior = request.form["alerta_superior"]
            alarme_inferior = request.form["alarme_inferior"]
            alarme_superior = request.form["alarme_superior"]
            correcao = request.form["correcao"]
            status = request.form.get("ativo")      
            db.session.add(sensors)
            db.session.commit()               
            sensors.query.filter_by(id=id).update({"id_dispositivo":dispositivo_sensor, "tag":tag, "serie":serie, "organi_sensor_id":organi_sensor, "modelo":modelos, "concentrador":concentrador, "coletor":coletor, "alerta_inferior":alerta_inferior, "alerta_superior":alerta_superior, "alarme_inferior":alarme_inferior, "alarme_superior":alarme_superior, "correcao":correcao, "status":status })
            db.session.commit()
            return redirect(url_for("sensores"))
        return render_template("/sensores/atualiza_sensores.html", sensors=sensors, organiza=organizacao.query.all(), modelos=modelo.query.all(), sensor_organi = db.session.query(sensor).join(organizacao).filter(sensor.id==id).first(), sensor_modelo = db.session.query(sensor).join(modelo).filter(sensor.id==id).first()) 

    #Tela de operações de cadastro de modelos, leitura, inclusão, exclusão e alteração.
    @app.route("/modelos")
    @login_required
    def modelos():
        return render_template("/modelos/modelo.html", modelos=db.session.execute(db.select(modelo).order_by(modelo.id)).scalars())

    @app.route("/modelos/<int:id>")
    @login_required
    def unique_modelo(id):
        return render_template("/modelos/modelos.html", modelos=modelo.query.get(id))

    @app.route("/modelos/excluir/<int:id>")
    @login_required
    def excluir_modelo(id):
        deletes=modelo.query.filter_by(id=id).first()
        db.session.delete(deletes)
        db.session.commit()
        return redirect(url_for("modelos"))
    
    @app.route("/modelo_consulta")
    
    @jwt_required()
    def modelo_consulta():             
        
        modelo_nome = request.args.get('modelo_nome')
        modelo_unidade = request.args.get('modelo_unidade')
        modelo_conversao = request.args.get('modelo_conversao')
        modelo_a4 = request.args.get('modelo_a4')
        modelo_a3 = request.args.get('modelo_a3')
        modelo_a2 = request.args.get('modelo_a2')
        modelo_a1 = request.args.get('modelo_a1')
        modelo_a_1 = request.args.get('modelo_a_1')
        modelo_a_2 = request.args.get('modelo_a_2')
        modelo_b4 = request.args.get('modelo_b4')
        modelo_b3 = request.args.get('modelo_b3')
        modelo_b2 = request.args.get('modelo_b2')
        modelo_b1 = request.args.get('modelo_b1')
        modelo_b_1 = request.args.get('modelo_b_1')
        modelo_b_2 = request.args.get('modelo_b_2')
        modelo_parametros = request.args.get('modelo_parametros')
        modelo_inferior = request.args.get('modelo_inferior') 

        if modelo_nome:
            model = modelo.query.filter(modelo.nome.contains(modelo_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_unidade:
            model = modelo.query.filter(modelo.unidade.contains(modelo_unidade))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_conversao:
            model = modelo.query.filter(modelo.conversao.contains(modelo_conversao))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_a4:
            model = modelo.query.filter(modelo.a4.contains(modelo_a4))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_a3:
            model = modelo.query.filter(modelo.a3.contains(modelo_a3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_a2:
            model = modelo.query.filter(modelo.a2.contains(modelo_a2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_a1:
            model = modelo.query.filter(modelo.a1.contains(modelo_a1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_a_1:
            model = modelo.query.filter(modelo.a_1.contains(modelo_a_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_a_2:
            model = modelo.query.filter(modelo.a_2.contains(modelo_a_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_b4:
            model = modelo.query.filter(modelo.b4.contains(modelo_b4))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_b3:
            model = modelo.query.filter(modelo.b3.contains(modelo_b3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_b2:
            model = modelo.query.filter(modelo.b4.contains(modelo_b2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_b1:
            model = modelo.query.filter(modelo.b4.contains(modelo_b1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_b_1:
            model = modelo.query.filter(modelo.b_1.contains(modelo_b_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_b_2:
            model = modelo.query.filter(modelo.b_2.contains(modelo_b_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif modelo_parametros:
            model = modelo.query.filter(modelo.parametros.contains(modelo_parametros))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif modelo_inferior:
            model = modelo.query.filter(modelo.inferior.contains(modelo_inferior))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))             
        else:
            return jsonify({'menssagem': 'Dados do modelo não encontrado.'}), 400

        modelo_json = []
        for mode in model:
            modelo_dict = {'id': mode.id, 
                           'nome': mode.nome,
                           'unidade': mode.unidade,
                           'conversao': mode.conversao,
                           'a4': mode.a4,
                           'a3': mode.a3,
                           'a2': mode.a2,
                           'a1': mode.a1,
                           'a_1': mode.a_1,
                           'a_2': mode.a_2,
                           'b4': mode.b4,
                           'b3': mode.b3,
                           'b2': mode.b2,
                           'b1': mode.b1,
                           'b_1': mode.b_1,
                           'b_2': mode.b_2,
                           'parametros': mode.parametros,
                           'inferior': mode.inferior,
                           'data': mode.data                                                      
                         }
            modelo_json.append(modelo_dict)

        return jsonify(modelo_json)  


    @app.route("/cad_modelo", methods=["GET", "POST"])
    @login_required
    def cad_modelo():
        if request.method == "POST":
            model = modelo()
            model.nome = request.form["nome"]
            model.conversao = request.form["conversao"]
            model.unidade = request.form["unidade"]              
            model.a4 = request.form["a4"]
            model.a3 = request.form["a3"]
            model.a2 = request.form["a2"]
            model.a1 = request.form["a1"]
            model.a0 = request.form["a0"]
            model.a_1 = request.form["a_1"]
            model.a_2 = request.form["a_2"]
            model.b4 = request.form["b4"]
            model.b3 = request.form["b3"]
            model.b2 = request.form["b2"]
            model.b1 = request.form["b1"]
            model.b0 = request.form["b0"]
            model.b_1 = request.form["b_1"]
            model.b_2 = request.form["b_2"]
            #if request.form["inferior"] and request.form["superior"] != "null":
            if request.form["inferior"] and request.form["superior"]  != "null":
                model.inferior = request.form["inferior"]
                model.superior = request.form["superior"]
           
            db.session.add(model)
            db.session.commit()         
            flash("Modelo criado com sucesso!")       
            return redirect(url_for("cad_modelo"))
        return render_template("/modelos/cad_modelo.html")   

    @app.route("/modelos/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_modelo(id):
        modelos=modelo.query.filter_by(id=id).first()
        if request.method == "POST":        
            nome = request.form["nome"]
            conversao = request.form["conversao"]
            unidade = request.form["unidade"]              
            a4 = request.form["a4"]
            a3 = request.form["a3"]
            a2 = request.form["a2"]
            a1 = request.form["a1"]
            a0 = request.form["a0"]
            a_1 = request.form["a_1"]
            a_2 = request.form["a_2"]
            b4 = request.form["b4"]
            b3 = request.form["b3"]
            b2 = request.form["b2"]
            b1 = request.form["b1"]
            b0 = request.form["b0"]
            b_1 = request.form["b_1"]
            b_2 = request.form["b_2"]
            inferior = request.form["inferior"]
            superior = request.form["superior"]      
            modelos.query.filter_by(id=id).update({"nome":nome, "conversao":conversao, "unidade":unidade, "a4":a4, "a3":a3, "a2":a2, "a1":a1, "a0":a0, "a_1":a_1, "a_2":a_2, "b4":b4, "b3":b3, "b2":b2, "b1":b1, "b0":b0, "b_1":b_1, "b_2":b_2,"inferior":inferior, "superior":superior})
            db.session.commit()
            return redirect(url_for("modelos"))
        return render_template("/modelos/atualiza_modelo.html", modelos=modelos)

    @app.route("/modelos/atualiza_2/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_modelo_2(id):
        modelos=modelo.query.filter_by(id=id).first()
        if request.method == "POST":        
            nome = request.form["nome"]
            conversao = request.form["conversao"]
            unidade = request.form["unidade"]              
            a4 = request.form["a4"]
            a3 = request.form["a3"]
            a2 = request.form["a2"]
            a1 = request.form["a1"]
            a0 = request.form["a0"]
            a_1 = request.form["a_1"]
            a_2 = request.form["a_2"]
            b4 = request.form["b4"]
            b3 = request.form["b3"]
            b2 = request.form["b2"]
            b1 = request.form["b1"]
            b0 = request.form["b0"]
            b_1 = request.form["b_1"]
            b_2 = request.form["b_2"]          
            modelos.query.filter_by(id=id).update({"nome":nome,  "conversao":conversao, "unidade":unidade, "a4":a4, "a3":a3, "a2":a2, "a1":a1, "a0":a0, "a_1":a_1, "a_2":a_2, "b4":b4, "b3":b3, "b2":b2, "b1":b1, "b0":b0, "b_1":b_1, "b_2":b_2})
            db.session.commit()
            return redirect(url_for("modelos"))
        return render_template("/modelos/atualiza_modelo_2.html", modelos=modelos) 

    #Tela de operações de cadastro de concentradores, leitura, inclusão, exclusão e alteração.
    @app.route("/concentradores")
    @login_required
    def concentradores():
        return render_template("/concentradores/concentrador.html", concentradores=db.session.execute(db.select(concentrador).order_by(concentrador.id)).scalars())

    @app.route("/concentradores/<int:id>")
    @login_required
    def unique_concentrador(id):
        return render_template("/concentradores/concentradores.html", concentradores=concentrador.query.get(id), concentra_organi = db.session.query(concentrador).join(organizacao).filter(concentrador.id==id).first())

    @app.route("/concentradores/excluir/<int:id>")
    @login_required
    def excluir_concentrador(id):
        delete=concentrador.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("concentradores"))
    
    @app.route("/gateway_consulta", methods=['GET'])
    #@login_required
    @jwt_required()
    def concentrador_consulta():   
        concentra_id = request.args.get('concentra_id')
        concentra_guid = request.args.get('concentra_guid')
        concentra_tag = request.args.get('concentra_tag')
        concentra_serie = request.args.get('concentra_serie')
        concentra_modelo = request.args.get('concentra_modelo')
        concentra_firmware = request.args.get('concentra_firmware')
        concentra_hardware = request.args.get('concentra_hardware')
        

        if concentra_id and concentra_guid:
            concentra_enc = concentrador.query.filter_by(id_dispositivo=concentra_id, GUID=concentra_guid).first()

            if concentra_enc:
                # Concentrador autenticado, retornar JSON com seus dados
                dados_concentra = {
                                 'id': concentra_enc.id, 
                                 'id_dispositivo': concentra_enc.id_dispositivo,
                                 'tag': concentra_enc.tag,
                                 'serie': concentra_enc.serie,
                                 'modelo': concentra_enc.modelo,
                                 'firmware': concentra_enc.firmware,
                                 'hardware': concentra_enc.hardware,
                                 'status': concentra_enc.status,
                                 'GUID': concentra_enc.GUID,
                                 'data': concentra_enc.data
                                }

                return jsonify(dados_concentra)                               
            else:
                return jsonify({'menssagem': 'Id do dispositivo ou GUID invalido.'}), 400
        elif concentra_tag:
            concentra_enc = concentrador.query.filter_by(tag=concentra_tag).first()

            if concentra_enc:
                # Tag encontrada, retornar JSON com seus dados
                dados_concentra = {
                                 'id': concentra_enc.id, 
                                 'id_dispositivo': concentra_enc.id_dispositivo,
                                 'tag': concentra_enc.tag,
                                 'serie': concentra_enc.serie,
                                 'modelo': concentra_enc.modelo,
                                 'firmware': concentra_enc.firmware,
                                 'hardware': concentra_enc.hardware,
                                 'status': concentra_enc.status,
                                 'GUID': concentra_enc.GUID,
                                 'data': concentra_enc.data
                                }

                return jsonify(dados_concentra)                               
            else:
                return jsonify({'menssagem': 'Tag inexistente.'}), 400

        elif concentra_serie:
            concentra_enc = concentrador.query.filter_by(serie=concentra_serie).first()

            if concentra_enc:
                # Serie encontrada, retornar JSON com seus dados
                dados_concentra = {
                                 'id': concentra_enc.id, 
                                 'id_dispositivo': concentra_enc.id_dispositivo,
                                 'tag': concentra_enc.tag,
                                 'serie': concentra_enc.serie,
                                 'modelo': concentra_enc.modelo,
                                 'firmware': concentra_enc.firmware,
                                 'hardware': concentra_enc.hardware,
                                 'status': concentra_enc.status,
                                 'GUID': concentra_enc.GUID,
                                 'data': concentra_enc.data
                                }

                return jsonify(dados_concentra)                               
            else:
                return jsonify({'menssagem': 'Serie inexistente.'}), 400

        elif concentra_modelo:
            concentra_enc = concentrador.query.filter_by(modelo=concentra_modelo).first()

            if concentra_enc:
                # Modelo encontrada, retornar JSON com seus dados
                dados_concentra = {
                                 'id': concentra_enc.id, 
                                 'id_dispositivo': concentra_enc.id_dispositivo,
                                 'tag': concentra_enc.tag,
                                 'serie': concentra_enc.serie,
                                 'modelo': concentra_enc.modelo,
                                 'firmware': concentra_enc.firmware,
                                 'hardware': concentra_enc.hardware,
                                 'status': concentra_enc.status,
                                 'GUID': concentra_enc.GUID,
                                 'data': concentra_enc.data
                                }

                return jsonify(dados_concentra)                               
            else:
                return jsonify({'menssagem': 'Modelo inexistente.'}), 400

        elif concentra_firmware:
            concentra_enc = concentrador.query.filter_by(firmware=concentra_firmware).first()

            if concentra_enc:
                # Modelo encontrada, retornar JSON com seus dados
                dados_concentra = {
                                 'id': concentra_enc.id, 
                                 'id_dispositivo': concentra_enc.id_dispositivo,
                                 'tag': concentra_enc.tag,
                                 'serie': concentra_enc.serie,
                                 'modelo': concentra_enc.modelo,
                                 'firmware': concentra_enc.firmware,
                                 'hardware': concentra_enc.hardware,
                                 'status': concentra_enc.status,
                                 'GUID': concentra_enc.GUID,
                                 'data': concentra_enc.data
                                }

                return jsonify(dados_concentra)                               
            else:
                return jsonify({'menssagem': 'Firmware inexistente.'}), 400

        elif concentra_hardware:
            concentra_enc = concentrador.query.filter_by(hardware=concentra_hardware).first()

            if concentra_enc:
                # Modelo encontrada, retornar JSON com seus dados
                dados_concentra = {
                                 'id': concentra_enc.id, 
                                 'id_dispositivo': concentra_enc.id_dispositivo,
                                 'tag': concentra_enc.tag,
                                 'serie': concentra_enc.serie,
                                 'modelo': concentra_enc.modelo,
                                 'firmware': concentra_enc.firmware,
                                 'hardware': concentra_enc.hardware,
                                 'status': concentra_enc.status,
                                 'GUID': concentra_enc.GUID,
                                 'data': concentra_enc.data
                                }

                return jsonify(dados_concentra)                               
            else:
                return jsonify({'menssagem': 'Hardware inexistente.'}), 400
        else:
           return jsonify({'menssagem': 'Dados do concentrador não encontrado.'}), 400

    
    @app.route("/cad_concentrador", methods=["GET", "POST"])
    @login_required
    def cad_concentrador():
        if request.method == "POST":
            concentra = concentrador()
            concentra.id_dispositivo = request.form["dispositivo"]
            concentra.tag = request.form["tag"]
            concentra.serie = request.form["serie"]
            concentra.organi_concentra_id = request.form["organi"]        
            concentra.modelo = request.form["modelo"]
            concentra.firmware = request.form["firmware"]
            concentra.hardware = request.form["hardware"]
            #concentra.GUID = request.form["GUID"]
            concentra.previsao = request.form.get("previsao")
            concentra.GUID = secrets.token_hex(16)
            db.session.add(concentra)
            db.session.commit()      
            
            flash("Concentrador criado com sucesso!")       
            return redirect(url_for("cad_concentrador"))
        return render_template("/concentradores/cad_concentrador.html", organiza=organizacao.query.all())

    @app.route("/concentradores/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_concentrador(id):
        concentra=concentrador.query.filter_by(id=id).first()
        if request.method == "POST":
            dispositivo_concentra = request.form["dispositivo"]        
            tag = request.form["tag"]
            serie = request.form["serie"]
            organi_concentra = request.form["organi"]
            modelo = request.form["modelo"]               
            firmware = request.form["firmware"]
            hardware = request.form["hardware"]   
            #GUID = request.form["GUID"]
            previsao = request.form.get("previsao")         
            #return redirect("/usuarios")            
            concentra.query.filter_by(id=id).update({"id_dispositivo":dispositivo_concentra,"tag":tag, "serie":serie, "organi_concentra_id":organi_concentra, "modelo":modelo, "firmware":firmware, "hardware":hardware, "previsao":previsao })
            db.session.commit()
            return redirect(url_for("concentradores"))
        return render_template("/concentradores/atualiza_concentradores.html", concentra=concentra, organiza=organizacao.query.all(), concentra_organi = db.session.query(concentrador).join(organizacao).filter(concentrador.id==id).first())
    
    
    #Tela de operações de cadastro de solos curva de retenção, leitura, inclusão, exclusão e alteração.
    @app.route("/solo_reten")
    @login_required
    def solo_reten():
        return render_template("/solo_retens/solo_reten.html", retensao=solo_curva.query.all())

    @app.route("/solo_reten/<int:id>")
    @login_required
    def unique_retensao(id):
        return render_template("/solo_retens/solo_retens.html", retensao=solo_curva.query.get(id))
    
    @app.route("/solo_consulta")
    #@login_required
    @jwt_required()
    def solo_consulta():       
        
        solo_nome = request.args.get('solo_nome')
        solo_theta_s_1 = request.args.get('solo_theta_s_1')
        solo_theta_s_2 = request.args.get('solo_theta_s_2')
        solo_theta_s_3 = request.args.get('solo_theta_s_3')
        solo_theta_r_1 = request.args.get('solo_theta_r_1')
        solo_theta_r_2 = request.args.get('solo_theta_r_2')
        solo_theta_r_3 = request.args.get('solo_theta_r_3')
        solo_alpha_1 = request.args.get('solo_alpha_1')
        solo_alpha_2 = request.args.get('solo_alpha_2')
        solo_alpha_3 = request.args.get('solo_alpha_3')
        solo_n_solo_1 = request.args.get('solo_n_solo_1')
        solo_n_solo_2 = request.args.get('solo_n_solo_2')
        solo_n_solo_3 = request.args.get('solo_n_solo_3')
        solo_m_solo_1 = request.args.get('solo_m_solo_1')
        solo_m_solo_2 = request.args.get('solo_m_solo_2')
        solo_m_solo_3 = request.args.get('solo_m_solo_3')
                     
        if solo_nome:
            solo = solo_curva.query.filter(solo_curva.nome.contains(solo_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_theta_s_1:
            solo = solo_curva.query.filter(solo_curva.theta_s_0_20.contains(solo_theta_s_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_theta_s_2:
            solo = solo_curva.query.filter(solo_curva.theta_s_20_40.contains(solo_theta_s_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif solo_theta_s_3:
            solo = solo_curva.query.filter(solo_curva.theta_s_40_60.contains(solo_theta_s_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_theta_r_1:
            solo = solo_curva.query.filter(solo_curva.theta_r_0_20.contains(solo_theta_r_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_theta_r_2:
            solo = solo_curva.query.filter(solo_curva.theta_r_20_40.contains(solo_theta_r_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif solo_theta_r_3:
            solo = solo_curva.query.filter(solo_curva.theta_r_40_60.contains(solo_theta_r_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_alpha_1:
            solo = solo_curva.query.filter(solo_curva.alpha_0_20.contains(solo_alpha_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_alpha_2:
            solo = solo_curva.query.filter(solo_curva.alpha_20_40.contains(solo_alpha_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif solo_alpha_3:
            solo = solo_curva.query.filter(solo_curva.alpha_40_60.contains(solo_alpha_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_n_solo_1:
            solo = solo_curva.query.filter(solo_curva.n_solo_0_20.contains(solo_n_solo_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_n_solo_2:
            solo = solo_curva.query.filter(solo_curva.n_solo_20_40.contains(solo_n_solo_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif solo_n_solo_3:
            solo = solo_curva.query.filter(solo_curva.n_solo_40_60.contains(solo_n_solo_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif solo_m_solo_1:
            solo = solo_curva.query.filter(solo_curva.m_solo_0_20.contains(solo_m_solo_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif solo_m_solo_2:
            solo = solo_curva.query.filter(solo_curva.m_solo_20_40.contains(solo_m_solo_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif solo_m_solo_3:
            solo = solo_curva.query.filter(solo_curva.m_solo_40_60.contains(solo_m_solo_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))                     
        else:
            return jsonify({'menssagem': 'Dados do solo não encontrado.'}), 400
       
        solo_json = []
        for sol in solo:
            solo_dict = {'id': sol.id, 
                         'nome': sol.nome,
                         'theta_s_0_20': sol.theta_s_0_20,
                         'theta_s_20_40': sol.theta_s_20_40,
                         'theta_s_40_60': sol.theta_s_40_60,
                         'theta_r_0_20': sol.theta_r_0_20,
                         'theta_r_20_40': sol.theta_r_0_20,
                         'theta_r_40_60': sol.theta_r_0_20,
                         'alpha_0_20': sol.alpha_0_20,
                         'alpha_20_40': sol.alpha_20_40,
                         'alpha_40_60': sol.alpha_40_60,
                         'n_solo_0_20': sol.n_solo_0_20,
                         'n_solo_20_40': sol.n_solo_20_40,
                         'n_solo_40_60': sol.n_solo_40_60,
                         'm_solo_0_20': sol.m_solo_0_20,
                         'm_solo_20_40': sol.m_solo_20_40,
                         'm_solo_40_60': sol.m_solo_40_60,
                         'data': sol.data
                                 }
            solo_json.append(solo_dict)

        return jsonify(solo_json)   

        #return render_template("teste.html", concentradores=concentradores) 

    @app.route("/solo_reten/excluir/<int:id>")
    @login_required
    def excluir_retensao(id):
        delete=solo_curva.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("solo_reten"))

    @app.route("/cad_solo_reten", methods=["GET", "POST"])
    @login_required
    def cad_solo_reten():
        if request.method == "POST":
            solo = solo_curva()
            solo.nome = request.form["nome"]
            solo.theta_s_0_20 = request.form["theta_s_0_20"]
            solo.theta_s_20_40 = request.form["theta_s_20_40"]
            solo.theta_s_40_60 = request.form["theta_s_40_60"]
            solo.theta_r_0_20 = request.form["theta_r_0_20"]
            solo.theta_r_20_40 = request.form["theta_r_20_40"]
            solo.theta_r_40_60 = request.form["theta_r_40_60"]
            solo.alpha_0_20 = request.form["alpha_0_20"]
            solo.alpha_20_40 = request.form["alpha_20_40"]
            solo.alpha_40_60 = request.form["alpha_40_60"]        
            solo.n_solo_0_20 = request.form["n_solo_0_20"]
            solo.n_solo_20_40 = request.form["n_solo_20_40"]
            solo.n_solo_40_60 = request.form["n_solo_40_60"]
            solo.m_solo_0_20 = request.form["m_solo_0_20"]
            solo.m_solo_20_40 = request.form["m_solo_20_40"]
            solo.m_solo_40_60 = request.form["m_solo_40_60"]
            db.session.add(solo)
            db.session.commit()         
            flash("Solo curva de retenção criado com sucesso!")       
            return redirect(url_for("cad_solo_reten"))
        return render_template("/solo_retens/cad_solo_reten.html")

    @app.route("/solo_reten/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_retensao(id):
        retensao=solo_curva.query.filter_by(id=id).first()
        if request.method == "POST":
            nome = request.form["nome"]
            theta_s_0_20 = request.form["theta_s_0_20"]
            theta_s_20_40 = request.form["theta_s_20_40"]
            theta_s_40_60 = request.form["theta_s_40_60"]
            theta_r_0_20 = request.form["theta_r_0_20"]
            theta_r_20_40 = request.form["theta_r_20_40"]
            theta_r_40_60 = request.form["theta_r_40_60"]
            alpha_0_20 = request.form["alpha_0_20"]
            alpha_20_40 = request.form["alpha_20_40"]
            alpha_40_60 = request.form["alpha_40_60"]        
            n_solo_0_20 = request.form["n_solo_0_20"]
            n_solo_20_40 = request.form["n_solo_20_40"]
            n_solo_40_60 = request.form["n_solo_40_60"]
            m_solo_0_20 = request.form["m_solo_0_20"]
            m_solo_20_40 = request.form["m_solo_20_40"]
            m_solo_40_60 = request.form["m_solo_40_60"]
           
            #return redirect("/usuarios")            
            retensao.query.filter_by(id=id).update({"nome":nome, "theta_s_0_20":theta_s_0_20, "theta_s_20_40":theta_s_20_40, "theta_s_40_60":theta_s_40_60, 
                                                    "theta_r_0_20":theta_r_0_20, "theta_r_20_40":theta_r_20_40, "theta_r_40_60":theta_r_40_60,
                                                    "alpha_0_20":alpha_0_20, "alpha_20_40":alpha_20_40, "alpha_40_60":alpha_40_60,
                                                    "n_solo_0_20":n_solo_0_20, "n_solo_20_40":n_solo_20_40, "n_solo_40_60":n_solo_40_60,
                                                    "m_solo_0_20":m_solo_0_20, "m_solo_20_40":m_solo_20_40, "m_solo_40_60":m_solo_40_60 })
            db.session.commit()
            return redirect(url_for("solo_reten"))
        return render_template("/solo_retens/atualiza_retensao.html", retensao=retensao)
    
    #Tela de operações de Cultura, leitura, inclusão, exclusão e alteração.
    @app.route("/cultura")
    @login_required
    def culturas():
        return render_template("/culturas/cultura.html", culturas=cultura.query.all())

    @app.route("/cultura/excluir/<int:id>")
    @login_required
    def excluir_cultura(id):
        delete=cultura.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("culturas"))
    
    @app.route("/cultura_consulta")
    #@login_required
    @jwt_required()
    def cultura_consulta():       
        cultura_nome = request.args.get('cultura_nome')                        
        if cultura_nome:
            cultu = cultura.query.filter(cultura.nome.contains(cultura_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))       
        else:
            return jsonify({'menssagem': 'Dados da cultura não encontrado.'}), 400

        cultura_json = []
        for culto in cultu:
            cultura_dict = {'id': culto.id, 
                              'nome': culto.nome,
                              'data': culto.data
                             }
            cultura_json.append(cultura_dict)

        return jsonify(cultura_json)   

    @app.route("/cad_cultura", methods=["GET", "POST"])
    @login_required
    def cad_cultura():
        if request.method == "POST":
            culto = cultura()
            culto.nome = request.form["nome"]        
            db.session.add(culto)
            db.session.commit()         
            flash("Cultura criado com sucesso!")       
            return redirect(url_for("cad_cultura"))
        return render_template("/culturas/cad_cultura.html")

    @app.route("/cultura/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_cultura(id):
        culto=cultura.query.filter_by(id=id).first()
        if request.method == "POST":        
            nome = request.form["nome"]        
            #return redirect("/usuarios")            
            culto.query.filter_by(id=id).update({"nome":nome})
            db.session.commit()
            return redirect(url_for("culturas"))
        return render_template("/culturas/atualiza_cultura.html", culto=culto)

    #Tela de operações de Cultura, leitura, inclusão, exclusão e alteração.
    @app.route("/fenologica/<int:id>")
    @login_required
    def fenologicas(id):
        return render_template("fenologica/fenologica.html", fenologi = db.session.query(fenologica).join(cultura).filter(fenologica.cultura_feno_id==id).all(), culturas=cultura.query.get(id))

    @app.route("/fenologica/excluir/<int:id>")
    @login_required
    def excluir_fenologica(id):  
        fenologicas=fenologica.query.filter_by(id=id).first()      
        delete=fenologica.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("fenologicas", id=fenologicas.cultura_feno_id))
    
    @app.route("/fenologica_consulta")
    #@login_required
    @jwt_required()
    def fenologica_consulta():       
        fenologica_cultura_id = request.args.get('fenologica_cultura_id')
        fenologica_nome = request.args.get('fenologica_nome')                        
        if fenologica_cultura_id:
            feno = fenologica.query.filter(fenologica.cultura_feno_id.contains(fenologica_cultura_id))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif fenologica_nome:
            feno = fenologica.query.filter(fenologica.nome.contains(fenologica_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))       
        else:
            return jsonify({'menssagem': 'Dados da fenologica não encontrado.'}), 400

        fenologica_json = []
        for fen in feno:
            fenologica_dict = {'id': fen.id,
                               'cultura_feno_id': fen.cultura_feno_id, 
                               'nome': fen.nome,
                               'ciclo': fen.ciclo,
                               'profundidade': fen.profundidade,
                               'kc': fen.kc,
                               'data': fen.data
                             }
            fenologica_json.append(fenologica_dict)

        return jsonify(fenologica_json)   
    
    @app.route("/cad_fenologica/<int:id>", methods=["GET", "POST"])
    @login_required
    def cad_fenologica(id):
        if request.method == "POST":
            fenologicas = fenologica()
            fenologicas.cultura_feno_id = request.form["id_cultura"]
            fenologicas.nome = request.form["nome"]
            fenologicas.ciclo = request.form["ciclo"]
            fenologicas.profundidade = request.form["profundidade"]        
            fenologicas.kc = request.form["kc"]            
            db.session.add(fenologicas)
            db.session.commit()  
            #flash("Fase fenologica criado com sucesso!")                
            return redirect(url_for('fenologicas', id=id ))
        return render_template("/fenologica/cad_fenologica.html", culturas=cultura.query.get(id))

    @app.route("/fenologica/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_fenologica(id):
        fenologicas=fenologica.query.filter_by(id=id).first()
        if request.method == "POST":           
            nome = request.form["nome"]
            escondido = request.form["id_cultura"]
            ciclo = request.form["ciclo"]
            profundidade = request.form["profundidade"]        
            kc = request.form["kc"]            
            fenologicas.query.filter_by(id=id).update({"nome":nome, "ciclo":ciclo, "profundidade":profundidade, "kc":kc })
            db.session.commit()      
            return redirect(url_for("fenologicas",id=fenologicas.cultura_feno_id))
        return render_template("/fenologica/atualiza_fenologica.html",fenologicas=fenologicas, cultu=cultura.query.filter_by(id=fenologicas.cultura_feno_id).first())

#Tela de operações de irrigação, leitura, inclusão, exclusão e alteração.
    @app.route("/irriga")
    @login_required
    def irriga():
        return render_template("/irriga/irriga.html", irrigas=irrigacao.query.all())

    @app.route("/irriga/excluir/<int:id>")
    @login_required
    def excluir_irriga(id):
        delete=irrigacao.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("irriga"))
    
    @app.route("/irriga_consulta")
    #@login_required
    @jwt_required()
    def irriga_consulta():       
        irriga_nome = request.args.get('irriga_nome')                        
        if irriga_nome:
            irriga = irrigacao.query.filter(irrigacao.nome.contains(irriga_nome))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))       
        else:
            return jsonify({'menssagem': 'Dados da irrigação não encontrado.'}), 400

        irrigacao_json = []
        for irrig in irriga:
            irrigacao_dict = {'id': irrig.id, 
                              'nome': irrig.nome,
                              'data': irrig.data
                             }
            irrigacao_json.append(irrigacao_dict)

        return jsonify(irrigacao_json)   

    @app.route("/cad_irriga", methods=["GET", "POST"])
    @login_required
    def cad_irriga():
        if request.method == "POST":
            irrigas = irrigacao()
            irrigas.nome = request.form["nome"]        
            db.session.add(irrigas)
            db.session.commit()         
            flash("Tipo de irrigação criado com sucesso!")       
            return redirect(url_for("cad_irriga"))
        return render_template("/irriga/cad_irriga.html")

    @app.route("/irriga/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_irriga(id):
        irrigas=irrigacao.query.filter_by(id=id).first()
        if request.method == "POST":        
            nome = request.form["nome"]        
            #return redirect("/usuarios")            
            irrigas.query.filter_by(id=id).update({"nome":nome})
            db.session.commit()
            return redirect(url_for("irriga"))
        return render_template("/irriga/atualiza_irriga.html", irrigas=irrigas)
    
    #Tela de operações de publicações do coletor v1, leitura, inclusão, exclusão e alteração.
    @app.route("/pubs")
    @login_required
    def pubs():
        return render_template("/pub/pub.html", pubs=db.session.execute(db.select(pub).order_by(pub.id)).scalars())    

    @app.route("/pubs/<int:id>")
    @login_required
    def unique_pubs(id):
        return render_template("/pub/pubs.html", unique_pubs=pub.query.get(id))


    @app.route("/cad_pub", methods=["GET", "POST"])
    @login_required
    def cad_pub():
        if request.method == "POST":
            pubs = pub()
            pubs.deviceId = request.form["deviceId"]
            pubs.channel = request.form["channel"]
            pubs.payload = request.form["payload"]        
            db.session.add(pubs)
            db.session.commit()         
            flash("Publicação do concentrador criado com sucesso!")       
            return redirect(url_for("cad_pub"))
        return render_template("/pub/cad_pub.html")

    @app.route("/pub/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_pub(id):
        pubs=pub.query.filter_by(id=id).first()
        if request.method == "POST":        
            deviceId = request.form["deviceId"]
            channel = request.form["channel"]
            payload = request.form["payload"]        
            #return redirect("/usuarios")            
            pubs.query.filter_by(id=id).update({"deviceId":deviceId, "channel":channel, "payload":payload})
            db.session.commit()
            return redirect(url_for("pubs"))
        return render_template("/pub/atualiza_pub.html", pubs=pubs)
    
    @app.route("/pub/excluir/<int:id>")
    @login_required
    def excluir_pub(id):
        delete=pub.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("pubs"))
    
    #Tela de operações do coletor v2, leitura, inclusão, exclusão e alteração.
    @app.route("/pubs_espec")
    @login_required
    def pubs_espec():
        return render_template("/pub_espec/pub.html", pubs=db.session.execute(db.select(pub_espec).order_by(pub_espec.id)).scalars())    

    @app.route("/pubs_espec/<int:id>")
    @login_required
    def unique_pub_espec(id):
        return render_template("/pub_espec/pubs.html", unique_pubs=pub_espec.query.get(id))
    
    @app.route("/pub_consulta")
    #@login_required
    @jwt_required()
    def pub_consulta():       
        
        pub_tipoMsg = request.args.get('pub_tipoMsg')
        pub_numBytes = request.args.get('pub_numBytes')
        pub_timestamp = request.args.get('pub_timestamp')
        pub_uidCon = request.args.get('pub_uidCon')
        pub_uidCol = request.args.get('pub_uidCol')
        pub_ts_start = request.args.get('pub_ts_start')
        pub_time_no_net = request.args.get('pub_time_no_net')
        pub_cpu_temp = request.args.get('pub_cpu_temp')
        pub_cpu_freq = request.args.get('pub_cpu_freq')
        pub_batStt = request.args.get('pub_batStt')
        pub_rssiUp = request.args.get('pub_rssiUp')
        pub_rssiDw = request.args.get('pub_rssiDw')
        pub_snrUp = request.args.get('pub_snrUp')
        pub_snrDw = request.args.get('pub_snrDw')
        pub_IdSns_1 = request.args.get('pub_IdSns_1')
        pub_ValorSns_1 = request.args.get('pub_ValorSns_1')
        pub_IdSns_2 = request.args.get('pub_IdSns_1')
        pub_ValorSns_2 = request.args.get('pub_ValorSns_1')
        pub_IdSns_3 = request.args.get('pub_IdSns_1')
        pub_ValorSns_3 = request.args.get('pub_ValorSns_1')
        pub_IdSns_4 = request.args.get('pub_IdSns_1')
        pub_ValorSns_4 = request.args.get('pub_ValorSns_1')
        pub_IdSns_5 = request.args.get('pub_IdSns_1')
        pub_ValorSns_5 = request.args.get('pub_ValorSns_1')
        pub_IdSns_6 = request.args.get('pub_IdSns_1')
        pub_ValorSns_6 = request.args.get('pub_ValorSns_1')
        pub_IdSns_7 = request.args.get('pub_IdSns_1')
        pub_ValorSns_7 = request.args.get('pub_ValorSns_1')
        pub_IdSns_8 = request.args.get('pub_IdSns_1')
        pub_ValorSns_8 = request.args.get('pub_ValorSns_1')
        pub_IdSns_9 = request.args.get('pub_IdSns_1')
        pub_ValorSns_9 = request.args.get('pub_ValorSns_1')
        pub_IdSns_10 = request.args.get('pub_IdSns_1')
        pub_ValorSns_10 = request.args.get('pub_ValorSns_1')
                     
        if pub_tipoMsg:
            pub = pub_espec.query.filter(pub_espec.tipoMsg.contains(pub_tipoMsg))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_numBytes:
            pub = pub_espec.query.filter(pub_espec.numBytes.contains(pub_numBytes))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_timestamp:
            pub = pub_espec.query.filter(pub_espec.timestamp.contains(pub_timestamp))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_uidCon:
            pub = pub_espec.query.filter(pub_espec.uidCon.contains(pub_uidCon))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_uidCol:
            pub = pub_espec.query.filter(pub_espec.uidCol.contains(pub_uidCol))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_ts_start:
            pub = pub_espec.query.filter(pub_espec.ts_start.contains(pub_ts_start))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_time_no_net:
            pub = pub_espec.query.filter(pub_espec.time_no_net.contains(pub_time_no_net))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_cpu_temp:
            pub = pub_espec.query.filter(pub_espec.cpu_temp.contains(pub_cpu_temp))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_cpu_freq:
            pub = pub_espec.query.filter(pub_espec.cpu_freq.contains(pub_cpu_freq))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_batStt:
            pub = pub_espec.query.filter(pub_espec.batStt.contains(pub_batStt))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_rssiUp:
            pub = pub_espec.query.filter(pub_espec.rssiUp.contains(pub_rssiUp))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_rssiDw:
            pub = pub_espec.query.filter(pub_espec.rssiDw.contains(pub_rssiDw))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_snrUp:
            pub = pub_espec.query.filter(pub_espec.snrUp.contains(pub_snrUp))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_snrDw:
            pub = pub_espec.query.filter(pub_espec.snrDw.contains(pub_snrDw))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_1:
            pub = pub_espec.query.filter(pub_espec.IdSns_1.contains(pub_IdSns_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_1:
            pub = pub_espec.query.filter(pub_espec.ValorSns_1.contains(pub_ValorSns_1))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_2:
            pub = pub_espec.query.filter(pub_espec.IdSns_2.contains(pub_IdSns_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_2:
            pub = pub_espec.query.filter(pub_espec.ValorSns_2.contains(pub_ValorSns_2))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_3:
            pub = pub_espec.query.filter(pub_espec.IdSns_3.contains(pub_IdSns_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_3:
            pub = pub_espec.query.filter(pub_espec.ValorSns_3.contains(pub_ValorSns_3))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_4:
            pub = pub_espec.query.filter(pub_espec.IdSns_4.contains(pub_IdSns_4))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_4:
            pub = pub_espec.query.filter(pub_espec.ValorSns_4.contains(pub_ValorSns_4))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_5:
            pub = pub_espec.query.filter(pub_espec.IdSns_5.contains(pub_IdSns_5))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_5:
            pub = pub_espec.query.filter(pub_espec.ValorSns_5.contains(pub_ValorSns_5))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_6:
            pub = pub_espec.query.filter(pub_espec.IdSns_6.contains(pub_IdSns_6))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_6:
            pub = pub_espec.query.filter(pub_espec.ValorSns_6.contains(pub_ValorSns_6))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))    
        elif pub_IdSns_7:
            pub = pub_espec.query.filter(pub_espec.IdSns_7.contains(pub_IdSns_7))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_7:
            pub = pub_espec.query.filter(pub_espec.ValorSns_7.contains(pub_ValorSns_7))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))    
        elif pub_IdSns_8:
            pub = pub_espec.query.filter(pub_espec.IdSns_8.contains(pub_IdSns_8))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_8:
            pub = pub_espec.query.filter(pub_espec.ValorSns_8.contains(pub_ValorSns_8))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif pub_IdSns_9:
            pub = pub_espec.query.filter(pub_espec.IdSns_9.contains(pub_IdSns_9))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_9:
            pub = pub_espec.query.filter(pub_espec.ValorSns_9.contains(pub_ValorSns_9))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))    
        elif pub_IdSns_10:
            pub = pub_espec.query.filter(pub_espec.IdSns_10.contains(pub_IdSns_10))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif pub_ValorSns_10:
            pub = pub_espec.query.filter(pub_espec.ValorSns_10.contains(pub_ValorSns_10))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))                         
        else:
            return jsonify({'menssagem': 'Dados do publicação não encontrado.'}), 400
       
        pub_json = []
        for pu in pub:
            pub_dict = {'id': pu.id, 
                         'tipoMsg': pu.tipoMsg,
                         'numBytes': pu.numBytes,
                         'timestamp': pu.timestamp,
                         'uidCon': pu.uidCon,
                         'uidCol': pu.uidCol,
                         'ts_start': pu.ts_start,
                         'time_no_net': pu.time_no_net,
                         'cpu_temp': pu.cpu_temp,
                         'cpu_freq': pu.cpu_freq,
                         'batStt': pu.batStt,
                         'rssiUp': pu.rssiUp,
                         'rssiDw': pu.rssiDw,
                         'snrUp': pu.snrUp,
                         'snrDw': pu.snrDw,
                         'IdSns_1': pu.IdSns_1,
                         'ValorSns_1': pu.ValorSns_1,
                         'IdSns_2': pu.IdSns_1,
                         'ValorSns_2': pu.ValorSns_1,
                         'IdSns_3': pu.IdSns_1,
                         'ValorSns_3': pu.ValorSns_1,
                         'IdSns_4': pu.IdSns_1,
                         'ValorSns_4': pu.ValorSns_1,
                         'IdSns_5': pu.IdSns_1,
                         'ValorSns_5': pu.ValorSns_1,
                         'IdSns_6': pu.IdSns_1,
                         'ValorSns_6': pu.ValorSns_1,
                         'IdSns_7': pu.IdSns_1,
                         'ValorSns_7': pu.ValorSns_1,
                         'IdSns_8': pu.IdSns_1,
                         'ValorSns_8': pu.ValorSns_1,
                         'IdSns_9': pu.IdSns_1,
                         'ValorSns_9': pu.ValorSns_1,
                         'IdSns_10': pu.IdSns_1,
                         'ValorSns_10': pu.ValorSns_1,
                         'data': pu.data
                                 }
            pub_json.append(pub_dict)

        return jsonify(pub_json)   

        #return render_template("teste.html", concentradores=concentradores) 

    @app.route("/cad_pub_espec", methods=["GET", "POST"])
    @login_required
    def cad_pub_espec():
        if request.method == "POST":
            pubs = pub_espec()          
            pubs.tipoMsg = request.form["tipoMsg"]
            pubs.numBytes = request.form["numBytes"]
            pubs.timestamp = request.form["timestamp"]
            pubs.uidCon = request.form["uidCon"]
            pubs.uidCol = request.form["uidCol"]
            pubs.ts_start = request.form["ts_start"]
            pubs.time_no_net = request.form["time_no_net"]
            pubs.cpu_temp = request.form["cpu_temp"]       
            pubs.cpu_freq = request.form["cpu_freq"]
            pubs.batStt = request.form["batStt"]
            pubs.rssiUp = request.form["rssiUp"]
            pubs.rssiDw = request.form["rssiDw"]
            pubs.snrUp = request.form["snrUp"]
            pubs.snrDw = request.form["snrDw"]
            pubs.IdSns_1 = request.form["IdSns_1"]
            pubs.ValorSns_1 = request.form["ValorSns_1"]
            pubs.IdSns_2 = request.form["IdSns_2"]
            pubs.ValorSns_2 = request.form["ValorSns_2"]
            pubs.IdSns_3 = request.form["IdSns_3"]
            pubs.ValorSns_3 = request.form["ValorSns_3"]
            pubs.IdSns_4 = request.form["IdSns_4"]
            pubs.ValorSns_4 = request.form["ValorSns_4"]
            pubs.IdSns_5 = request.form["IdSns_5"]
            pubs.ValorSns_5 = request.form["ValorSns_5"]
            pubs.IdSns_6 = request.form["IdSns_6"]
            pubs.ValorSns_6 = request.form["ValorSns_6"]
            pubs.IdSns_7 = request.form["IdSns_7"]
            pubs.ValorSns_7 = request.form["ValorSns_7"]
            pubs.IdSns_8 = request.form["IdSns_8"]
            pubs.ValorSns_8 = request.form["ValorSns_8"]
            pubs.IdSns_9 = request.form["IdSns_9"]
            pubs.ValorSns_9 = request.form["ValorSns_9"]
            pubs.IdSns_10 = request.form["IdSns_10"]
            pubs.ValorSns_10 = request.form["ValorSns_10"]                    
            db.session.add(pubs)
            db.session.commit()         
            flash("Publicação do concentrador criado com sucesso!")       
            return redirect(url_for("cad_pub_espec"))
        return render_template("/pub_espec/cad_pub.html")

    @app.route("/pub_espec/atualiza/<int:id>", methods=["GET", "POST"])
    @login_required
    def atualiza_pub_espec(id):
        pubs=pub_espec.query.filter_by(id=id).first()
        if request.method == "POST":        
            tipoMsg = request.form["tipoMsg"]
            numBytes = request.form["numBytes"]
            timestamp = request.form["timestamp"]
            uidCon = request.form["uidCon"]
            uidCol = request.form["uidCol"]
            ts_start = request.form["ts_start"]
            time_no_net = request.form["time_no_net"]
            cpu_temp = request.form["cpu_temp"]       
            cpu_freq = request.form["cpu_freq"]
            batStt = request.form["batStt"]
            rssiUp = request.form["rssiUp"]
            rssiDw = request.form["rssiDw"]
            snrUp = request.form["snrUp"]
            snrDw = request.form["snrDw"]
            IdSns_1 = request.form["IdSns_1"]
            ValorSns_1 = request.form["ValorSns_1"]
            IdSns_2 = request.form["IdSns_2"]
            ValorSns_2 = request.form["ValorSns_2"]
            IdSns_3 = request.form["IdSns_3"]
            ValorSns_3 = request.form["ValorSns_3"]
            IdSns_4 = request.form["IdSns_4"]
            ValorSns_4 = request.form["ValorSns_4"]
            IdSns_5 = request.form["IdSns_5"]
            ValorSns_5 = request.form["ValorSns_5"]
            IdSns_6 = request.form["IdSns_6"]
            ValorSns_6 = request.form["ValorSns_6"]
            IdSns_7 = request.form["IdSns_7"]
            ValorSns_7 = request.form["ValorSns_7"]
            IdSns_8 = request.form["IdSns_8"]
            ValorSns_8 = request.form["ValorSns_8"]
            IdSns_9 = request.form["IdSns_9"]
            ValorSns_9 = request.form["ValorSns_9"]
            IdSns_10 = request.form["IdSns_10"]
            ValorSns_10 = request.form["ValorSns_10"]                    
            #return redirect("/usuarios")            
            pubs.query.filter_by(id=id).update({"tipoMsg":tipoMsg, "numBytes":numBytes, "timestamp":timestamp, "uidCon":uidCon,
                                                "uidCol":uidCol, "ts_start":ts_start, "time_no_net":time_no_net, "cpu_temp":cpu_temp,
                                                "cpu_freq":cpu_freq, "batStt":batStt, "rssiUp":rssiUp, "rssiDw":rssiDw, "snrUp":snrUp,
                                                "snrDw":snrDw, "IdSns_1":IdSns_1, "ValorSns_1":ValorSns_1, "IdSns_2":IdSns_2, "ValorSns_2":ValorSns_2,
                                                "IdSns_3":IdSns_3, "ValorSns_3":ValorSns_3, "IdSns_4":IdSns_4, "IdSns_3":IdSns_3, "ValorSns_4":ValorSns_4,
                                                "IdSns_5":IdSns_5, "ValorSns_5":ValorSns_5, "IdSns_6":IdSns_6, "ValorSns_6":ValorSns_6,
                                                "IdSns_7":IdSns_7, "ValorSns_7":ValorSns_7, "IdSns_8":IdSns_8, "ValorSns_8":ValorSns_8,
                                                "IdSns_9":IdSns_9, "ValorSns_9":ValorSns_9, "IdSns_10":IdSns_10, "ValorSns_10":ValorSns_10 })
            db.session.commit()
            return redirect(url_for("pubs_espec"))
        return render_template("/pub_espec/atualiza_pub.html", pubs=pubs)
    
    @app.route("/pub_espec/excluir/<int:id>")
    @login_required
    def excluir_pub_espec(id):
        delete=pub_espec.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("pubs_espec"))
    
     #Tela de operações do coletor sensores, leitura.
    @app.route("/pubs_sensor")
    @login_required
    def pubs_sensores():
        return render_template("/pub_sensores/pub.html", pubs=db.session.execute(db.select(pub_espec).order_by(pub_espec.id)).scalars())    

    @app.route("/pubs_sensores/<int:id>")
    @login_required
    def unique_pub_sensores(id):
        return render_template("/pub_sensores/pubs.html", unique_pubs=pub_espec.query.get(id))
    

    #Tela de operações do coletor v2, leitura, inclusão, exclusão e alteração.
    @app.route("/temp_diario")
    @login_required
    def temp_diario():
        return render_template("/temp_diario/temp.html", temps=db.session.execute(db.select(dados_diarios_temperatura).order_by(dados_diarios_temperatura.id)).scalars())    

    @app.route("/temp_diario/<int:id>")
    @login_required
    def unique_temp_diario(id):
        return render_template("/temp_diario/temps.html", unique_temps=dados_diarios_temperatura.query.get(id))
    
    @app.route("/temp_consulta")
    #@login_required
    @jwt_required()
    def temp_consulta():       
        
        temp_dispositivo = request.args.get('temp_dispositivo')
        temp_tag = request.args.get('temp_tag')
        temp_valor = request.args.get('temp_valor')
        temp_data = request.args.get('temp_data')
                            
        if temp_dispositivo:
            temp = dados_diarios_temperatura.query.filter(dados_diarios_temperatura.query.id_dispositivo.contains(temp_dispositivo))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif temp_tag:
            temp = dados_diarios_temperatura.query.filter(dados_diarios_temperatura.tag.contains(temp_tag))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        elif temp_valor:
            temp = dados_diarios_temperatura.query.filter(dados_diarios_temperatura.valor.contains(temp_valor))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance)) 
        elif temp_data:
            temp = dados_diarios_temperatura.query.filter(dados_diarios_temperatura.uidCon.contains(temp_data))
            #alcan = alcance.query.filter(alcance.nome.contains(b_alcance)|alcance.tau.contains(b_alcance))
        else:
            return jsonify({'menssagem': 'Dados da temperatura não encontrado.'}), 400
       
        temp_json = []
        for te in temp:
            temp_dict = {'id': te.id, 
                         'id_dispositivo': te.id_dispositivo,
                         'tag': te.tag,
                         'valor': te.valor,
                         'data': te.data                         
                                 }
            temp_json.append(temp_dict)

        return jsonify(temp_json)   

        #return render_template("teste.html", concentradores=concentradores) 

      
    @app.route("/temp_diario/excluir/<int:id>")
    @login_required
    def excluir_temp_diario(id):
        delete=dados_diarios_temperatura.query.filter_by(id=id).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for("temp_diario"))
    

    


    
    
    

