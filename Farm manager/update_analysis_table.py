from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def main():
    print("Iniciando atualização da tabela analysis...")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print(f"Conectado ao banco de dados: {DATABASE_URL}")

            # Verificar se a tabela existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analysis')"))
            exists = result.scalar()
            
            if not exists:
                print("ERRO: A tabela 'analysis' não existe no banco de dados!")
                return False
            
            # Lista de colunas a serem adicionadas
            columns = [
                ('aluminum', 'FLOAT'),
                ('sulfur', 'FLOAT'),
                ('organic_matter', 'FLOAT'),
                ('cation_exchange', 'FLOAT'),
                ('base_saturation', 'FLOAT'),
                ('notes', 'TEXT')
            ]
            
            for column_name, column_type in columns:
                # Verificar se a coluna já existe
                result = conn.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'analysis' AND column_name = '{column_name}')"))
                column_exists = result.scalar()
                
                if column_exists:
                    print(f"A coluna '{column_name}' já existe na tabela 'analysis'.")
                else:
                    print(f"Adicionando coluna '{column_name}' à tabela 'analysis'...")
                    try:
                        # Adicionar a coluna
                        conn.execute(text(f'ALTER TABLE "analysis" ADD COLUMN {column_name} {column_type}'))
                        conn.commit()
                        print(f"Coluna '{column_name}' adicionada com sucesso!")
                    except Exception as e:
                        print(f"ERRO ao adicionar coluna '{column_name}': {str(e)}")
                        conn.rollback()
            
            print("Atualização da tabela analysis concluída com sucesso!")
            return True
            
    except Exception as e:
        print(f"ERRO durante a atualização: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 