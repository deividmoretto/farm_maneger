from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

# Configuração para conexão direta com o banco de dados
db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')
db_parts = db_url.replace('postgresql://', '').split('/')
db_params = db_parts[0].split('@')

if len(db_params) == 2:
    user_parts = db_params[0].split(':')
    host_parts = db_params[1].split(':')
    
    user = user_parts[0]
    password = user_parts[1] if len(user_parts) > 1 else None
    host = host_parts[0]
    port = host_parts[1] if len(host_parts) > 1 else '5432'
    dbname = db_parts[1]

    print(f"Conectando ao banco de dados: {dbname} em {host}")
    print(f"Usuário: {user}, Porta: {port}")

    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Conexão estabelecida com sucesso!")
        
        # Verificar se a coluna is_admin existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' AND column_name='is_admin';
        """)
        
        # Se a coluna não existir, cria
        if cursor.fetchone() is None:
            print("Coluna is_admin não encontrada, criando...")
            cursor.execute("ALTER TABLE \"user\" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;")
            print("Coluna is_admin adicionada com sucesso!")
        else:
            print("Coluna is_admin já existe, pulando criação.")
        
        # Alterar a tabela 'user' para aumentar o tamanho da coluna password_hash
        cursor.execute("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(255);")
        print("Coluna password_hash alterada para VARCHAR(255) com sucesso!")
        
        # Fechar a conexão
        cursor.close()
        conn.close()
        print("Operação concluída com sucesso.")
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")

else:
    print("Formato da URL do banco de dados inválido:", db_url) 