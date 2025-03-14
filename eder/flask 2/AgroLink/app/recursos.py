from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from blacklist import BLACKLIST, add_to_blacklist
from app import db
from datetime import timedelta
import re

# Validação de email
def validar_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de email inválido")
    return email

# Validação de senha
def validar_senha(senha):
    if len(senha) < 6:
        raise ValueError("A senha deve ter pelo menos 6 caracteres")
    return senha

class User_modelo(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help='O campo nome é obrigatório')
    argumentos.add_argument('email', type=validar_email, required=True, help='O campo email é obrigatório e deve ser válido')
    argumentos.add_argument('senha', type=validar_senha, required=True, help='O campo senha é obrigatório e deve ter pelo menos 6 caracteres')
    argumentos.add_argument('agro', type=str, required=True, help='O campo agro é obrigatório')
    argumentos.add_argument('prod', type=str, required=True, help='O campo prod é obrigatório')

    @jwt_required()
    def get(self):
        from app.models import usuario  # Importação local
        return {'Usuarios': [user.json() for user in usuario.query.all()]}

    def post(self):
        from app.models import usuario  # Importação local
        dados = User_modelo.argumentos.parse_args()
        
        # Verifica se o email já existe
        if usuario.query.filter_by(email=dados['email']).first():
            return {'message': 'Email já cadastrado'}, 400
        
        # Hash da senha
        dados['senha'] = generate_password_hash(dados['senha'])
        
        # Cria o usuário
        novo_usuario = usuario(**dados)
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            return novo_usuario.json(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Erro ao cadastrar usuário', 'error': str(e)}, 500

class Users_modelo(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str)
    argumentos.add_argument('email', type=validar_email)
    argumentos.add_argument('senha', type=validar_senha)
    argumentos.add_argument('agro', type=str)
    argumentos.add_argument('prod', type=str)

    @jwt_required()
    def get(self, id):
        from app.models import usuario  # Importação local
        user = usuario.query.filter_by(id=id).first()
        if user:
            return user.json()
        return {'message': 'Usuário não encontrado'}, 404

    @jwt_required()
    def put(self, id):
        from app.models import usuario  # Importação local
        dados = Users_modelo.argumentos.parse_args()
        user_encontrado = usuario.query.filter_by(id=id).first()
        
        if user_encontrado:
            # Se a senha foi fornecida, faz o hash
            if dados['senha']:
                dados['senha'] = generate_password_hash(dados['senha'])
            
            # Remove campos None
            dados = {k: v for k, v in dados.items() if v is not None}
            
            try:
                for key, value in dados.items():
                    setattr(user_encontrado, key, value)
                db.session.commit()
                return user_encontrado.json(), 200
            except Exception as e:
                db.session.rollback()
                return {'message': 'Erro ao atualizar usuário', 'error': str(e)}, 500
        
        return {'message': 'Usuário não encontrado'}, 404

    @jwt_required()
    def delete(self, id):
        from app.models import usuario  # Importação local
        user = usuario.query.filter_by(id=id).first()
        if user:
            try:
                db.session.delete(user)
                db.session.commit()
                return {'message': 'Usuário excluído com sucesso.'}
            except Exception as e:
                db.session.rollback()
                return {'message': 'Erro ao excluir usuário', 'error': str(e)}, 500
        return {'message': 'Usuário não encontrado'}, 404

class UserLogin(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('email', type=str, required=True, help='O campo email é obrigatório')
    argumentos.add_argument('senha', type=str, required=True, help='O campo senha é obrigatório')
    
    def post(self):
        from app.models import usuario  # Importação local
        dados = self.argumentos.parse_args()
        
        user = usuario.query.filter_by(email=dados['email']).first()
        
        if user and check_password_hash(user.senha, dados['senha']):
            # Cria o token de acesso com expiração de 1 dia
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(days=1)
            )
            return {'access_token': access_token}, 200
        
        return {'message': 'Email ou senha incorretos'}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        add_to_blacklist(jwt_id)
        return {'message': 'Logout realizado com sucesso'}, 200