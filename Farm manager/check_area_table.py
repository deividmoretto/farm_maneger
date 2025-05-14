from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def main():
    print("Verificando colunas da tabela area...")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print(f"Conectado ao banco de dados: {DATABASE_URL}")

            # Listar todas as colunas da tabela area
            result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'area' ORDER BY ordinal_position"))
            columns = result.fetchall()
            
            if not columns:
                print("ERRO: A tabela 'area' não existe ou não tem colunas!")
                return False
            
            print("\nColunas na tabela 'area':")
            print("-----------------------------")
            for column in columns:
                print(f"{column[0]} ({column[1]})")
            
            # Lista das colunas esperadas do modelo Area
            expected_columns = [
                'id', 'nome', 'tamanho', 'endereco', 'latitude', 
                'longitude', 'cultura', 'user_id', 'created_at', 'updated_at'
            ]
            
            existing_columns = [col[0] for col in columns]
            
            print("\nStatus das colunas esperadas:")
            print("-----------------------------")
            for col in expected_columns:
                exists = col in existing_columns
                status = "✓ Presente" if exists else "✗ Ausente"
                print(f"{col}: {status}")
            
            missing_columns = [col for col in expected_columns if col not in existing_columns]
            if missing_columns:
                print("\nColunas ausentes:")
                for col in missing_columns:
                    print(f"- {col}")
            else:
                print("\nTodas as colunas esperadas estão presentes na tabela!")
            
            return True
            
    except Exception as e:
        print(f"ERRO durante a verificação: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 