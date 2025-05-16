from app import db

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cultura = db.Column(db.String(50), default='soja')
    tamanho = db.Column(db.Float, nullable=False)
    endereco = db.Column(db.String(200))
    latitude = db.Column(db.String(30))
    longitude = db.Column(db.String(30))
    polygon_points = db.Column(db.Text)  # JSON serializado dos pontos do polígono
    descricao = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analyses = db.relationship('Analysis', backref='area', lazy=True) 