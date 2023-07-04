# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_moment import Moment

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object('app.config.Config')

db = SQLAlchemy(app)  # flask-sqlalchemy
bc = Bcrypt(app)  # flask-bcrypt
fa = Admin(app) # flask Admin

lm = LoginManager()  # flask-loginmanager
lm.init_app(app)       # init the login manager

mg = Migrate(app, db)
mm = Moment(app)

# Setup database
with app.app_context():
    db.create_all()


# Import routing, models and Start the App
from app import views, models

#set up admin
class DivisionAdminView(ModelView):
    column_list = ['name', 'short_name', 'projects']


class ProjectAdminView(ModelView):
    column_list = ['title', 'Division.short_name','supporting_divisions', 'action_items']


fa.add_view(ModelView(models.Users, db.session))
fa.add_view(DivisionAdminView(models.Division, db.session))
fa.add_view(ProjectAdminView(models.Project, db.session))
fa.add_view(ModelView(models.ActionItem, db.session))
fa.add_view(ModelView(models.Deliverable, db.session))
