# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from app.admin import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')