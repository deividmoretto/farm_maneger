from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def main():
    print("Iniciando correção dos tipos de colunas...")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print(f"Conectado ao banco de dados: {DATABASE_URL}")

            # Verificar os tipos atuais das colunas
            result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'area' AND (column_name = 'latitude' OR column_name = 'longitude')"))
            columns = result.fetchall()
            
            for column in columns:
                column_name, data_type = column
                print(f"Coluna '{column_name}' é do tipo '{data_type}'")
                
                if data_type != 'double precision':
                    print(f"Alterando tipo da coluna '{column_name}' para 'double precision'...")
                    # Primeiramente, tentar converter os valores existentes
                    try:
                        # Atualizar valores NULL para facilitar a conversão
                        conn.execute(text(f"UPDATE area SET {column_name} = NULL WHERE {column_name} = '' OR {column_name} IS NULL"))
                        conn.commit()
                        
                        # Alterar o tipo da coluna para double precision
                        conn.execute(text(f"ALTER TABLE area ALTER COLUMN {column_name} TYPE double precision USING {column_name}::double precision"))
                        conn.commit()
                        print(f"Coluna '{column_name}' alterada com sucesso para 'double precision'!")
                    except Exception as e:
                        print(f"ERRO ao alterar coluna '{column_name}': {str(e)}")
                        conn.rollback()
                        
                        # Tentar abordagem alternativa: recriar a coluna
                        try:
                            print(f"Tentando abordagem alternativa para '{column_name}'...")
                            # Renomear a coluna antiga
                            conn.execute(text(f"ALTER TABLE area RENAME COLUMN {column_name} TO {column_name}_old"))
                            conn.commit()
                            
                            # Criar nova coluna com o tipo correto
                            conn.execute(text(f"ALTER TABLE area ADD COLUMN {column_name} double precision"))
                            conn.commit()
                            
                            # Copiar dados convertidos
                            conn.execute(text(f"UPDATE area SET {column_name} = {column_name}_old::double precision WHERE {column_name}_old IS NOT NULL"))
                            conn.commit()
                            
                            # Remover coluna antiga
                            conn.execute(text(f"ALTER TABLE area DROP COLUMN {column_name}_old"))
                            conn.commit()
                            print(f"Coluna '{column_name}' recriada com sucesso como 'double precision'!")
                        except Exception as e2:
                            print(f"ERRO na abordagem alternativa para '{column_name}': {str(e2)}")
                            conn.rollback()
                else:
                    print(f"A coluna '{column_name}' já está com o tipo correto!")
            
            print("\nVerificação concluída!")
            return True
            
    except Exception as e:
        print(f"ERRO durante a verificação: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 