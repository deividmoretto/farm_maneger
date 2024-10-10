from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:incorreta@localhost/RAD'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = 'secret'
    app.config['JWT_SECRET_KEY'] = 'secret'
    app.config['JWT_BLACKLIST_ENABLE'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    
    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app import routes
    routes.init_app(app)

    return app
