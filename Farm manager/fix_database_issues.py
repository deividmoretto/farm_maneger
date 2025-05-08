from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import sys

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da conexão com o banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/farmdb')

def corrigir_tabela_area():
    """Corrige as colunas da tabela area (name -> nome)"""
    print("\n==== Corrigindo tabela AREA ====")
    try:
        # Estabelecer conexão direta com o banco
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Verificar se a tabela existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'area')"))
            exists = result.scalar()
            
            if not exists:
                print("ERRO: A tabela 'area' não existe!")
                return False
            
            # Verificar as colunas atuais
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'area' ORDER BY ordinal_position"))
            columns = [row[0] for row in result.fetchall()]
            print(f"Colunas existentes: {columns}")
            
            # Verificar se a coluna name existe
            name_exists = 'name' in columns
            nome_exists = 'nome' in columns
            
            if not name_exists and nome_exists:
                print("A tabela já está com a coluna 'nome' correta")
                return True
            
            if name_exists and not nome_exists:
                print("Renomeando coluna 'name' para 'nome'")
                conn.execute(text('ALTER TABLE "area" RENAME COLUMN "name" TO "nome"'))
                conn.commit()
                
                # Verificar se 'size' também precisa ser renomeado
                if 'size' in columns and 'tamanho' not in columns:
                    print("Renomeando coluna 'size' para 'tamanho'")
                    conn.execute(text('ALTER TABLE "area" RENAME COLUMN "size" TO "tamanho"'))
                    conn.commit()
                
                # Verificar se 'location' também precisa ser renomeado
                if 'location' in columns and 'endereco' not in columns:
                    print("Renomeando coluna 'location' para 'endereco'")
                    conn.execute(text('ALTER TABLE "area" RENAME COLUMN "location" TO "endereco"'))
                    conn.commit()
                
                # Verificar se 'crop_type' também precisa ser renomeado
                if 'crop_type' in columns and 'cultura' not in columns:
                    print("Renomeando coluna 'crop_type' para 'cultura'")
                    conn.execute(text('ALTER TABLE "area" RENAME COLUMN "crop_type" TO "cultura"'))
                    conn.commit()
                
                print("Colunas da tabela 'area' atualizadas com sucesso!")
                return True
            
            print("Não foi possível determinar o estado das colunas da tabela 'area'")
            return False
            
    except Exception as e:
        print(f"ERRO ao atualizar tabela 'area': {str(e)}")
        return False

def criar_rota_estatisticas_silos():
    """Cria a função para a rota estatisticas_silos no app.py"""
    print("\n==== Adicionando rota estatisticas_silos ====")
    try:
        # Abrir o arquivo app.py
        with open("app.py", "r", encoding="utf-8") as file:
            content = file.read()
        
        # Verificar se a rota já existe
        if "@app.route('/silos/estatisticas')" in content:
            print("A rota já existe no arquivo app.py")
            return True
        
        # Adicionar a rota no final do arquivo
        new_route = """
@app.route('/silos/estatisticas', methods=['GET'])
@login_required
def estatisticas_silos():
    silos = Silo.query.filter_by(user_id=current_user.id).all()
    
    # Estatísticas gerais
    total_capacidade = sum(silo.capacity for silo in silos) if silos else 0
    
    # Calcular ocupação atual
    total_armazenado = 0
    tipos_graos = {}
    valor_estimado = 0
    
    for silo in silos:
        # Filtrar apenas armazenamentos ativos
        armazenamentos_ativos = [a for a in silo.armazenamentos if a.exit_date is None]
        
        # Somar ocupação
        for armazenamento in armazenamentos_ativos:
            quantidade = armazenamento.quantity
            tipo_grao = armazenamento.crop_type
            
            # Somar ao total
            total_armazenado += quantidade
            
            # Adicionar ao dicionário de tipos
            if tipo_grao in tipos_graos:
                tipos_graos[tipo_grao] += quantidade
            else:
                tipos_graos[tipo_grao] = quantidade
            
            # Calcular valor estimado
            if armazenamento.price_per_ton:
                valor_estimado += quantidade * armazenamento.price_per_ton
    
    # Calcular porcentagem de ocupação
    capacidade_utilizada = (total_armazenado / total_capacidade * 100) if total_capacidade > 0 else 0
    
    # Formatar dados para retorno JSON
    tipos_formatados = [{"tipo": tipo, "quantidade": quantidade} for tipo, quantidade in tipos_graos.items()]
    
    return jsonify({
        "totalCapacidade": total_capacidade,
        "totalArmazenado": total_armazenado,
        "capacidadeUtilizada": capacidade_utilizada,
        "valorEstimado": valor_estimado,
        "tiposGraos": tipos_formatados
    })
"""
        
        # Adicionar a importação de jsonify se necessário
        if "from flask import jsonify" not in content:
            import_jsonify = "from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify\n"
            content = content.replace("from flask import Flask, render_template, request, redirect, url_for, flash, session", import_jsonify)
        
        # Adicionar a nova rota no final do arquivo
        with open("app.py", "w", encoding="utf-8") as file:
            if "if __name__ == '__main__':" in content:
                content = content.replace("if __name__ == '__main__':", new_route + "\nif __name__ == '__main__':")
            else:
                content += new_route
            file.write(content)
        
        print("Rota estatisticas_silos adicionada com sucesso!")
        return True
        
    except Exception as e:
        print(f"ERRO ao adicionar rota: {str(e)}")
        return False

def atualizar_template_silos():
    """Atualiza o template para usar a rota correta"""
    print("\n==== Atualizando template de silos ====")
    try:
        template_path = "templates/silos/listar_silos.html"
        # Verificar se o arquivo existe
        if not os.path.exists(template_path):
            print(f"ERRO: Arquivo {template_path} não encontrado!")
            return False
        
        # Ler o conteúdo do arquivo
        with open(template_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Substituir a URL incorreta pela correta
        updated_content = content.replace("{{ url_for('silos.estatisticas_silos') }}", "{{ url_for('estatisticas_silos') }}")
        
        # Salvar o arquivo atualizado
        with open(template_path, "w", encoding="utf-8") as file:
            file.write(updated_content)
        
        print("Template atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"ERRO ao atualizar template: {str(e)}")
        return False

def atualizar_codigo_areas():
    """Atualiza o código que usa 'name' para usar 'nome'"""
    print("\n==== Atualizando código para usar 'nome' ao invés de 'name' ====")
    try:
        with open("app.py", "r", encoding="utf-8") as file:
            content = file.read()
        
        # Atualizar a consulta de área
        if "Area.query.filter_by(user_id=current_user.id).all()" in content:
            print("Não é necessário alterar a consulta principal")
        
        # Atualizar o código de nova_area para usar nome ao invés de name
        if "name=request.form.get('name')" in content:
            content = content.replace(
                "name=request.form.get('name')",
                "nome=request.form.get('name')"
            )
            print("Atualizada a criação de área para usar 'nome'")
        
        # Salvar as alterações
        with open("app.py", "w", encoding="utf-8") as file:
            file.write(content)
        
        print("Código atualizado com sucesso para usar 'nome'!")
        return True
        
    except Exception as e:
        print(f"ERRO ao atualizar código: {str(e)}")
        return False

def main():
    """Função principal que coordena as correções"""
    print("=== INICIANDO CORREÇÕES DE BANCO DE DADOS ===")
    
    # Corrigir a tabela area (name -> nome)
    area_ok = corrigir_tabela_area()
    
    # Criar a rota estatisticas_silos que está faltando
    rota_ok = criar_rota_estatisticas_silos()
    
    # Atualizar o template para usar a rota correta
    template_ok = atualizar_template_silos()
    
    # Atualizar código para usar 'nome' ao invés de 'name'
    codigo_ok = atualizar_codigo_areas()
    
    # Reportar resultados
    print("\n=== RESULTADO DAS CORREÇÕES ===")
    print(f"Tabela area: {'✓ Corrigido' if area_ok else '✗ Falhou'}")
    print(f"Rota estatisticas_silos: {'✓ Corrigido' if rota_ok else '✗ Falhou'}")
    print(f"Template silos: {'✓ Corrigido' if template_ok else '✗ Falhou'}")
    print(f"Código para usar 'nome': {'✓ Corrigido' if codigo_ok else '✗ Falhou'}")
    
    if area_ok and rota_ok and template_ok and codigo_ok:
        print("\n✓ TODAS AS CORREÇÕES FORAM APLICADAS COM SUCESSO!")
        print("Agora o sistema deve funcionar corretamente. Execute o aplicativo novamente para testar.")
        return True
    else:
        print("\n✗ ALGUMAS CORREÇÕES FALHARAM. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 