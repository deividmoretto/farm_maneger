from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.silo import Silo, Armazenamento, Movimentacao
from app.forms.silo_forms import SiloForm, ArmazenamentoForm, MovimentacaoForm
from datetime import datetime, date
import json

silos_bp = Blueprint('silos', __name__)

@silos_bp.route('/silos')
@login_required
def listar_silos():
    silos = Silo.query.filter_by(user_id=current_user.id).all()
    # Preparar dados para o gráfico
    dados_grafico = []
    for silo in silos:
        # Calcular ocupação atual
        estoque = silo.estoque_atual()
        percentual = silo.percentual_ocupado()
        
        # Obter distribuição por cultura
        culturas = {}
        for armazenamento in silo.armazenamentos:
            if armazenamento.ativo:
                if armazenamento.cultura in culturas:
                    culturas[armazenamento.cultura] += armazenamento.quantidade_atual()
                else:
                    culturas[armazenamento.cultura] = armazenamento.quantidade_atual()
        
        dados_grafico.append({
            'id': silo.id,
            'nome': silo.nome,
            'capacidade': silo.capacidade,
            'estoque': estoque,
            'percentual': percentual,
            'culturas': culturas
        })
    
    return render_template('silos/listar_silos.html', silos=silos, dados_grafico=json.dumps(dados_grafico))

@silos_bp.route('/silos/novo', methods=['GET', 'POST'])
@login_required
def novo_silo():
    form = SiloForm()
    if form.validate_on_submit():
        silo = Silo(
            nome=form.nome.data,
            tipo=form.tipo.data,
            capacidade=form.capacidade.data,
            localizacao=form.localizacao.data,
            data_construcao=form.data_construcao.data,
            observacoes=form.observacoes.data,
            user_id=current_user.id
        )
        db.session.add(silo)
        db.session.commit()
        flash('Silo cadastrado com sucesso!', 'success')
        return redirect(url_for('silos.listar_silos'))
    return render_template('silos/novo_silo.html', form=form)

@silos_bp.route('/silos/<int:id>')
@login_required
def detalhes_silo(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    armazenamentos = Armazenamento.query.filter_by(silo_id=silo.id, ativo=True).all()
    historico = Armazenamento.query.filter_by(silo_id=silo.id, ativo=False).order_by(Armazenamento.data_saida.desc()).all()
    
    # Preparar dados para o gráfico de ocupação por cultura
    dados_culturas = {}
    for armazenamento in armazenamentos:
        if armazenamento.cultura in dados_culturas:
            dados_culturas[armazenamento.cultura] += armazenamento.quantidade_atual()
        else:
            dados_culturas[armazenamento.cultura] = armazenamento.quantidade_atual()
    
    # Calcular valor total estimado
    valor_total = sum(a.quantidade_atual() * (a.preco_unitario or 0) for a in armazenamentos)
    
    return render_template(
        'silos/detalhes_silo.html', 
        silo=silo, 
        armazenamentos=armazenamentos,
        historico=historico,
        dados_culturas=json.dumps(dados_culturas),
        valor_total=valor_total
    )

@silos_bp.route('/silos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_silo(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SiloForm(obj=silo)
    
    if form.validate_on_submit():
        silo.nome = form.nome.data
        silo.tipo = form.tipo.data
        silo.capacidade = form.capacidade.data
        silo.localizacao = form.localizacao.data
        silo.data_construcao = form.data_construcao.data
        silo.observacoes = form.observacoes.data
        
        db.session.commit()
        flash('Silo atualizado com sucesso!', 'success')
        return redirect(url_for('silos.detalhes_silo', id=silo.id))
    
    return render_template('silos/editar_silo.html', form=form, silo=silo)

@silos_bp.route('/silos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_silo(id):
    silo = Silo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Verificar se há armazenamentos ativos
    if any(a.ativo for a in silo.armazenamentos):
        flash('Não é possível excluir um silo com armazenamentos ativos!', 'danger')
        return redirect(url_for('silos.detalhes_silo', id=silo.id))
    
    db.session.delete(silo)
    db.session.commit()
    flash('Silo excluído com sucesso!', 'success')
    return redirect(url_for('silos.listar_silos'))

@silos_bp.route('/armazenamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_armazenamento():
    form = ArmazenamentoForm()
    
    # Preencher opções de silos
    form.silo_id.choices = [(s.id, s.nome) for s in Silo.query.filter_by(user_id=current_user.id).all()]
    
    # Se não houver silos cadastrados
    if not form.silo_id.choices:
        flash('Você precisa cadastrar pelo menos um silo antes de registrar armazenamentos!', 'warning')
        return redirect(url_for('silos.novo_silo'))
    
    if form.validate_on_submit():
        # Verificar capacidade disponível
        silo = Silo.query.get(form.silo_id.data)
        if not silo or silo.user_id != current_user.id:
            flash('Silo inválido!', 'danger')
            return redirect(url_for('silos.listar_silos'))
        
        estoque_atual = silo.estoque_atual()
        if estoque_atual + form.quantidade.data > silo.capacidade:
            flash(f'A quantidade excede a capacidade disponível do silo! Disponível: {silo.capacidade - estoque_atual:.2f} toneladas', 'danger')
            return render_template('silos/novo_armazenamento.html', form=form)
        
        armazenamento = Armazenamento(
            silo_id=form.silo_id.data,
            cultura=form.cultura.data,
            safra=form.safra.data,
            data_entrada=form.data_entrada.data,
            quantidade=form.quantidade.data,
            umidade=form.umidade.data,
            impureza=form.impureza.data,
            preco_unitario=form.preco_unitario.data,
            observacoes=form.observacoes.data
        )
        db.session.add(armazenamento)
        db.session.commit()
        flash('Armazenamento registrado com sucesso!', 'success')
        return redirect(url_for('silos.detalhes_silo', id=form.silo_id.data))
    
    # Se vier da página de detalhes de um silo, pré-selecionar o silo
    silo_id = request.args.get('silo_id', type=int)
    if silo_id:
        silo = Silo.query.filter_by(id=silo_id, user_id=current_user.id).first()
        if silo:
            form.silo_id.data = silo.id
    
    return render_template('silos/novo_armazenamento.html', form=form)

@silos_bp.route('/armazenamentos/<int:id>')
@login_required
def detalhes_armazenamento(id):
    armazenamento = Armazenamento.query.join(Silo).filter(
        Armazenamento.id == id,
        Silo.user_id == current_user.id
    ).first_or_404()
    
    # Preparar formulário para registrar saída
    form = MovimentacaoForm()
    form.armazenamento_id.data = armazenamento.id
    
    # Obter movimentações ordenadas por data
    movimentacoes = Movimentacao.query.filter_by(armazenamento_id=armazenamento.id).order_by(Movimentacao.data.desc()).all()
    
    # Calcular quantidade atual
    quantidade_atual = armazenamento.quantidade_atual()
    
    return render_template(
        'silos/detalhes_armazenamento.html', 
        armazenamento=armazenamento,
        movimentacoes=movimentacoes,
        quantidade_atual=quantidade_atual,
        form=form
    )

@silos_bp.route('/movimentacoes/nova', methods=['POST'])
@login_required
def nova_movimentacao():
    form = MovimentacaoForm()
    
    if form.validate_on_submit():
        # Verificar armazenamento
        armazenamento = Armazenamento.query.join(Silo).filter(
            Armazenamento.id == form.armazenamento_id.data,
            Silo.user_id == current_user.id,
            Armazenamento.ativo == True
        ).first_or_404()
        
        # Verificar quantidade disponível
        quantidade_atual = armazenamento.quantidade_atual()
        if form.quantidade.data > quantidade_atual:
            flash(f'A quantidade de saída excede o estoque disponível! Disponível: {quantidade_atual:.2f} toneladas', 'danger')
            return redirect(url_for('silos.detalhes_armazenamento', id=armazenamento.id))
        
        # Registrar movimentação
        movimentacao = Movimentacao(
            armazenamento_id=armazenamento.id,
            data=form.data.data,
            tipo=form.tipo.data,
            quantidade=form.quantidade.data,
            destino=form.destino.data,
            preco_unitario=form.preco_unitario.data,
            observacoes=form.observacoes.data
        )
        db.session.add(movimentacao)
        
        # Se a retirada for total, marcar como inativo
        nova_quantidade = quantidade_atual - form.quantidade.data
        if nova_quantidade <= 0.001:  # Considera retirada total se ficar menos de 1kg
            armazenamento.ativo = False
            armazenamento.data_saida = form.data.data
        
        db.session.commit()
        flash('Movimentação registrada com sucesso!', 'success')
        
        # Se o armazenamento foi encerrado, redirecionar para o silo
        if not armazenamento.ativo:
            return redirect(url_for('silos.detalhes_silo', id=armazenamento.silo_id))
        else:
            return redirect(url_for('silos.detalhes_armazenamento', id=armazenamento.id))
    
    # Em caso de erro no formulário
    flash('Erro ao registrar movimentação. Verifique os dados informados.', 'danger')
    return redirect(url_for('silos.detalhes_armazenamento', id=form.armazenamento_id.data))

@silos_bp.route('/api/silos/estatisticas')
@login_required
def estatisticas_silos():
    """Endpoint para obter estatísticas de todos os silos do usuário"""
    silos = Silo.query.filter_by(user_id=current_user.id).all()
    
    # Estatísticas gerais
    total_capacidade = sum(s.capacidade for s in silos)
    total_armazenado = sum(s.estoque_atual() for s in silos)
    ocupacao_media = (total_armazenado / total_capacidade * 100) if total_capacidade > 0 else 0
    
    # Distribuição por cultura
    culturas = {}
    for silo in silos:
        for armazenamento in silo.armazenamentos:
            if armazenamento.ativo:
                if armazenamento.cultura in culturas:
                    culturas[armazenamento.cultura] += armazenamento.quantidade_atual()
                else:
                    culturas[armazenamento.cultura] = armazenamento.quantidade_atual()
    
    # Estimar valor total armazenado
    valor_total = 0
    for silo in silos:
        for armazenamento in silo.armazenamentos:
            if armazenamento.ativo and armazenamento.preco_unitario:
                valor_total += armazenamento.quantidade_atual() * armazenamento.preco_unitario
    
    return jsonify({
        'capacidade_total': total_capacidade,
        'total_armazenado': total_armazenado,
        'ocupacao_media': ocupacao_media,
        'culturas': culturas,
        'valor_total': valor_total
    }) 