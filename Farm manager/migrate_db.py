from app import create_app, db
import os
import sys

def main():
    print("Inicializando migração do banco de dados...")
    try:
        # Criar a aplicação Flask
        app = create_app()
        
        with app.app_context():
            # Inicializar pasta de migração se não existir
            if not os.path.exists('migrations'):
                print("Criando repositório de migração...")
                os.system('flask db init')
                print("Repositório de migração criado.")
            
            # Criar migração para o campo is_admin
            print("Gerando migração para as mudanças no modelo...")
            os.system('flask db migrate -m "add is_admin to user"')
            
            # Aplicar a migração
            print("Aplicando migração ao banco de dados...")
            os.system('flask db upgrade')
            
            print("Migração concluída com sucesso!")
            return True
            
    except Exception as e:
        print(f"ERRO durante a migração: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 