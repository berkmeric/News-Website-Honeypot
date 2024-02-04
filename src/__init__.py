from decouple import config
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import logging

#Prevent werkzeug from logging to stdout except warnings and errors
logging.getLogger('werkzeug').setLevel(logging.WARNING)



app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "berkmeric1@gmail.com"
app.config['MAIL_PASSWORD'] = "htbx bzhl pbgb jdsa"
mail = Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


from src.accounts.views import accounts_bp
from src.core.views import core_bp

app.register_blueprint(accounts_bp)
app.register_blueprint(core_bp)

from src.accounts.models import User

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()





@app.errorhandler(401)
def unauthorized_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500
