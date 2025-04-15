import importlib.util
import os
import sys

# Caminho para o arquivo app.py
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')

# Carregar o módulo app.py dinamicamente
spec = importlib.util.spec_from_file_location("app_py", app_path)
app_py = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_py)

# Acessar app, db e User do módulo carregado
app = app_py.app
db = app_py.db
User = app_py.User

try:
    with app.app_context():
        # Verificar se já existe um usuário admin
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print(f"Usuário admin já existe (ID: {admin.id})")
            print("Atualizando senha e garantindo privilégios de admin...")
            admin.set_password('admin')
            
            # Verificar se o campo is_admin existe no modelo User
            if hasattr(User, 'is_admin'):
                admin.is_admin = True
                print("Campo is_admin atualizado.")
            else:
                print("AVISO: O modelo User não possui o campo is_admin. Verifique o seu modelo.")
            
            db.session.commit()
            print("Dados atualizados com sucesso!")
        else:
            print("Criando usuário admin...")
            # Criar novo usuário administrador
            new_admin_data = {
                'username': 'admin',
                'email': 'admin@example.com'
            }
            
            # Verificar se o campo is_admin existe no modelo User
            if hasattr(User, 'is_admin'):
                new_admin_data['is_admin'] = True
                print("Campo is_admin será definido como True.")
            else:
                print("AVISO: O modelo User não possui o campo is_admin. Verifique o seu modelo.")
            
            # Criar o objeto User com os dados apropriados
            new_admin = User(**new_admin_data)
            new_admin.set_password('admin')
            
            # Salvar no banco de dados
            db.session.add(new_admin)
            db.session.commit()
            
            print("Usuário admin criado com sucesso!")
            print("Username: admin")
            print("Password: admin")
            print("Email: admin@example.com")
            if hasattr(User, 'is_admin'):
                print("is_admin: True")
except Exception as e:
    print(f"Erro ao criar/atualizar admin: {str(e)}")
    print("Detalhes:")
    import traceback
    traceback.print_exc() 