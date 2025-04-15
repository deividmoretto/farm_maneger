from sqlalchemy import create_engine, text
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def main():
    print("Iniciando atualização do esquema do banco de dados...")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print(f"Conectado ao banco de dados: {DATABASE_URL}")

            # Verificar se a tabela existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')"))
            exists = result.scalar()
            
            if not exists:
                print("ERRO: A tabela 'user' não existe no banco de dados!")
                return False
            
            # Verificar se a coluna já existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'is_admin')"))
            column_exists = result.scalar()
            
            if column_exists:
                print("A coluna 'is_admin' já existe na tabela 'user'.")
            else:
                print("Adicionando coluna 'is_admin' à tabela 'user'...")
                try:
                    # Adicionar a coluna is_admin com valor padrão false
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'))
                    conn.commit()
                    print("Coluna 'is_admin' adicionada com sucesso!")
                    
                    # Atualizar o usuário 'admin' (se existir) para ter privilégios administrativos
                    print("Verificando usuário admin...")
                    result = conn.execute(text("SELECT id FROM \"user\" WHERE username = 'admin' LIMIT 1"))
                    admin_user = result.fetchone()
                    
                    if admin_user:
                        admin_id = admin_user[0]
                        conn.execute(text(f"UPDATE \"user\" SET is_admin = TRUE WHERE id = {admin_id}"))
                        conn.commit()
                        print(f"Usuário 'admin' (ID: {admin_id}) foi marcado como administrador.")
                    else:
                        print("Nenhum usuário 'admin' encontrado.")
                    
                except Exception as e:
                    print(f"ERRO ao adicionar coluna: {str(e)}")
                    return False
            
            print("Verificando administradores existentes...")
            result = conn.execute(text("SELECT COUNT(*) FROM \"user\" WHERE is_admin = TRUE"))
            admin_count = result.scalar()
            print(f"Total de administradores: {admin_count}")
            
            print("Atualização concluída com sucesso!")
            return True
            
    except Exception as e:
        print(f"ERRO durante a atualização: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 