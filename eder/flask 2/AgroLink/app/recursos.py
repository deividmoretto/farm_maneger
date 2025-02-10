from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from blacklist import BLACKLIST
from app import db

class User_modelo(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome')
    argumentos.add_argument('email')
    argumentos.add_argument('senha')

    #@jwt_required()
    def get(self):
        from app.models import usuario  # Importação local
        return {'Usuarios': [usuari.json() for usuari in usuario.query.all()]}

    def post(self):
        from app.models import usuario  # Importação local
        dados = User_modelo.argumentos.parse_args()
        users = usuario(**dados)
        db.session.add(users)
        db.session.commit()
        return users.json(), 201

class Users_modelo(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome')
    argumentos.add_argument('email')
    argumentos.add_argument('senha')

    #@jwt_required()
    def get(self, id):
        from app.models import usuario  # Importação local
        users = usuario.query.filter_by(id=id).first()
        if users:
            return users.json()
        return {'message': 'Usuario inexistente'}, 404

    #@jwt_required()
    def put(self, id):
        from app.models import usuario  # Importação local
        dados = Users_modelo.argumentos.parse_args()
        user_encontrado = usuario.query.filter_by(id=id).first()
        if user_encontrado:
            user_encontrado.query.filter_by(id=id).update({**dados})
            db.session.commit()
            return user_encontrado.json(), 200
        users = usuario(**dados)
        db.session.add(users)
        db.session.commit()
        return users.json(), 201

    #@jwt_required()
    def delete(self, id):
        from app.models import usuario  # Importação local
        users = usuario.query.filter_by(id=id).first()
        if users:
            db.session.delete(users)
            db.session.commit()
            return {'message': 'Usuario excluido com sucesso.'}
        return {'message': 'Usuario inexistente'}, 404