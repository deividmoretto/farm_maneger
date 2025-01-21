from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app import create_app, db
from blacklist import BLACKLIST
from app.recursos import User_modelo, Users_modelo

# Criação da aplicação
app = create_app()
api = Api(app)
jwt = JWTManager(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

# Configuração do JWT
@jwt.token_in_blocklist_loader
def verifica_blacklist(self, token):
    return token['jti'] in BLACKLIST

@jwt.revoked_token_loader
def token_de_acesso_invalidado(jwt_header, jwt_payload):
    return jsonify({'message': 'Você saiu do sistema.'}), 401  # unauthorized

# Recursos da API
api.add_resource(User_modelo, '/user_api')
api.add_resource(Users_modelo, '/users_api/<string:id>')

if __name__ == "__main__":
    app.run(debug=True)