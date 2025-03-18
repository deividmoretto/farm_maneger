from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app import create_app, db
from blacklist import BLACKLIST, is_blacklisted
from app.recursos import User_modelo, Users_modelo, UserLogin, UserLogout

# Criação da aplicação
app = create_app()
api = Api(app)
jwt = JWTManager(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

# Configuração do JWT
@jwt.token_in_blocklist_loader
def verifica_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return is_blacklisted(jti)

@jwt.revoked_token_loader
def token_de_acesso_invalidado(jwt_header, jwt_payload):
    return jsonify({'message': 'Você saiu do sistema.', 'error': 'token_revoked'}), 401  # unauthorized

@jwt.expired_token_loader
def token_expirado(jwt_header, jwt_payload):
    return jsonify({'message': 'O token de acesso expirou.', 'error': 'token_expired'}), 401

@jwt.invalid_token_loader
def token_invalido(error):
    return jsonify({'message': 'Verificação de token falhou.', 'error': 'invalid_token'}), 401

@jwt.unauthorized_loader
def token_nao_fornecido(error):
    return jsonify({'message': 'Token de acesso não fornecido.', 'error': 'authorization_required'}), 401

# Recursos da API
api.add_resource(User_modelo, '/api/usuarios')
api.add_resource(Users_modelo, '/api/usuarios/<string:id>')
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogout, '/api/logout')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)