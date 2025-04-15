from app import db
from app import create_app

# Criar a aplicação Flask
app = create_app()

# Garante que o script será executado dentro do contexto da aplicação Flask
with app.app_context():
    print("Iniciando criação das tabelas...")
    db.create_all()
    print("Tabelas criadas com sucesso!") 