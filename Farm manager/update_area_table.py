from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import sqlite3
import sys

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def update_area_table():
    # Encontra o caminho do banco de dados
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'farm_db.sqlite')
    
    if not os.path.exists(db_path):
        print(f"Banco de dados não encontrado em: {db_path}")
        sys.exit(1)
    
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se a coluna polygon_points já existe
        cursor.execute("PRAGMA table_info(area)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'polygon_points' not in columns:
            # Adiciona a coluna polygon_points se ela não existir
            cursor.execute("ALTER TABLE area ADD COLUMN polygon_points TEXT")
            conn.commit()
            print("Coluna polygon_points adicionada com sucesso à tabela area")
        else:
            print("Coluna polygon_points já existe na tabela area")
        
        # Fecha a conexão com o banco de dados
        conn.close()
        
        print("Atualização concluída com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
        sys.exit(1)

def main():
    print("Iniciando atualização da tabela area...")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print(f"Conectado ao banco de dados: {DATABASE_URL}")

            # Verificar se a tabela existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'area')"))
            exists = result.scalar()
            
            if not exists:
                print("ERRO: A tabela 'area' não existe no banco de dados!")
                return False
            
            # Adicionar a coluna created_at se não existir
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'area' AND column_name = 'created_at')"))
            created_at_exists = result.scalar()
            
            if not created_at_exists:
                print("Adicionando coluna 'created_at' à tabela 'area'...")
                try:
                    conn.execute(text("ALTER TABLE area ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
                    conn.commit()
                    print("Coluna 'created_at' adicionada com sucesso!")
                except Exception as e:
                    print(f"ERRO ao adicionar coluna 'created_at': {str(e)}")
                    conn.rollback()
                    return False
            else:
                print("A coluna 'created_at' já existe na tabela 'area'.")
            
            # Adicionar a coluna updated_at se não existir
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'area' AND column_name = 'updated_at')"))
            updated_at_exists = result.scalar()
            
            if not updated_at_exists:
                print("Adicionando coluna 'updated_at' à tabela 'area'...")
                try:
                    conn.execute(text("ALTER TABLE area ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
                    conn.commit()
                    print("Coluna 'updated_at' adicionada com sucesso!")
                except Exception as e:
                    print(f"ERRO ao adicionar coluna 'updated_at': {str(e)}")
                    conn.rollback()
                    return False
            else:
                print("A coluna 'updated_at' já existe na tabela 'area'.")
            
            # Verificar se a coluna polygon_points existe no modelo, mas não na tabela
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'area' AND column_name = 'polygon_points')"))
            polygon_points_exists = result.scalar()
            
            if not polygon_points_exists:
                print("Adicionando coluna 'polygon_points' à tabela 'area'...")
                try:
                    conn.execute(text("ALTER TABLE area ADD COLUMN polygon_points TEXT"))
                    conn.commit()
                    print("Coluna 'polygon_points' adicionada com sucesso!")
                except Exception as e:
                    print(f"ERRO ao adicionar coluna 'polygon_points': {str(e)}")
                    conn.rollback()
                    return False
            else:
                print("A coluna 'polygon_points' já existe na tabela 'area'.")
            
            print("Atualização da tabela area concluída com sucesso!")
            return True
            
    except Exception as e:
        print(f"ERRO durante a atualização: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        update_area_table()
    exit(0 if success else 1) 