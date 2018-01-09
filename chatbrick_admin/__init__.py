import os
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, template_folder=os.path.join(os.pardir, 'templates'), static_folder=os.path.join(os.pardir, 'static'))

app.debug = True
app.config['MONGO_HOST'] = os.environ['DB_CHATBRICK_HOST']
app.config['MONGO_PORT'] = os.environ['DB_CHATBRICK_PORT']
app.config['MONGO_DBNAME'] = os.environ['DB_CHATBRICK_NAME']

mongo3 = PyMongo(app)
from chatbrick_admin.chatbrick import *