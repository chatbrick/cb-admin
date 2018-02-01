import os
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, template_folder=os.path.join(os.pardir, 'templates'), static_url_path='/api/static', static_folder=os.path.join(os.pardir, 'static'))

app.debug = True
app.secret_key = 'bluehack_secret_ket'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MONGO_HOST'] = os.environ['DB_CHATBRICK_HOST']
app.config['MONGO_PORT'] = os.environ['DB_CHATBRICK_PORT']
app.config['MONGO_DBNAME'] = os.environ['DB_CHATBRICK_NAME']
app.config['MONGO_USERNAME'] = os.environ['DB_CHATBRICK_USER_NAME']
app.config['MONGO_PASSWORD'] = os.environ['DB_CHATBRICK_USER_PASSWORD']
app.config['UPLOAD_FOLDER'] = '/home/ec2-user/app/chatbrick_admin/src/static'

mongo3 = PyMongo(app)
from chatbrick_admin.chatbrick import *