from app import db
from datetime import datetime

class Silo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Tipo: Metálico, Concreto, Bolsa, etc.
    capacidade = db.Column(db.Float, nullable=False)  # Capacidade em toneladas
    localizacao = db.Column(db.String(200), nullable=True)
    data_construcao = db.Column(db.Date, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamento com armazenamentos
    armazenamentos = db.relationship('Armazenamento', backref='silo', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Silo {self.nome}>'
    
    def estoque_atual(self):
        """Retorna o somatório dos armazenamentos ativos"""
        ativos = [a for a in self.armazenamentos if a.ativo]
        return sum(a.quantidade for a in ativos) if ativos else 0
    
    def percentual_ocupado(self):
        """Retorna o percentual de ocupação do silo"""
        if self.capacidade > 0:
            return (self.estoque_atual() / self.capacidade) * 100
        return 0


class Armazenamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    silo_id = db.Column(db.Integer, db.ForeignKey('silo.id'), nullable=False)
    cultura = db.Column(db.String(50), nullable=False)  # Tipo de grão: Milho, Soja, Trigo, etc.
    safra = db.Column(db.String(20), nullable=True)  # Ex: "2023/2024"
    data_entrada = db.Column(db.DateTime, nullable=False, default=datetime.now)
    quantidade = db.Column(db.Float, nullable=False)  # Em toneladas
    umidade = db.Column(db.Float, nullable=True)  # Percentual de umidade
    impureza = db.Column(db.Float, nullable=True)  # Percentual de impureza
    preco_unitario = db.Column(db.Float, nullable=True)  # Preço por tonelada na entrada
    ativo = db.Column(db.Boolean, default=True)  # Indica se ainda há estoque ou se foi retirado
    data_saida = db.Column(db.DateTime, nullable=True)  # Data de saída completa (se ativo=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Relacionamento com movimentações (saídas parciais)
    movimentacoes = db.relationship('Movimentacao', backref='armazenamento', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Armazenamento {self.id}: {self.cultura} - {self.quantidade}t>'
    
    def quantidade_atual(self):
        """Retorna a quantidade atual descontando as saídas"""
        saidas = sum(m.quantidade for m in self.movimentacoes)
        return self.quantidade - saidas


class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    armazenamento_id = db.Column(db.Integer, db.ForeignKey('armazenamento.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tipo = db.Column(db.String(10), nullable=False, default='saida')  # 'saida' ou 'ajuste'
    quantidade = db.Column(db.Float, nullable=False)  # Em toneladas
    destino = db.Column(db.String(100), nullable=True)  # Para onde foi o grão
    preco_unitario = db.Column(db.Float, nullable=True)  # Preço por tonelada na saída
    observacoes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Movimentacao {self.id}: {self.quantidade}t>' 