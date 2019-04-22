import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://letnetco_oit1:Oit_2019@64.37.61.194/letnetco_oit1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mysql@localhost/flowapp2'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'usuarios.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'siscudud@gmail.com'
app.config['MAIL_PASSWORD'] = 'siscudprueba'
mail = Mail(app)

#Registrar los componentes
from flowapp.usuarios.routes import usuarios
from flowapp.dispositivos.routes import dispositivos
from flowapp.principal.routes import principal


app.register_blueprint(usuarios)
app.register_blueprint(dispositivos)
app.register_blueprint(principal)
