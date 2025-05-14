from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def check_table(conn, table_name):
    """Verifica as colunas de uma tabela específica"""
    print(f"\n=== Verificando colunas da tabela {table_name} ===")
    
    # Listar todas as colunas da tabela
    result = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position"))
    columns = result.fetchall()
    
    if not columns:
        print(f"ERRO: A tabela '{table_name}' não existe ou não tem colunas!")
        return False
    
    print("\nColunas na tabela:")
    print("-----------------------------")
    for column in columns:
        print(f"{column[0]} ({column[1]})")
    
    return True

def main():
    print("Iniciando verificação de tabelas...")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print(f"Conectado ao banco de dados: {DATABASE_URL}")

            # Verificar tabelas principais
            tables = ['area', 'analysis', 'user', 'silo', 'armazenamento']
            for table in tables:
                check_table(conn, table)
            
            print("\nVerificação concluída!")
            return True
            
    except Exception as e:
        print(f"ERRO durante a verificação: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 