# -*- coding: utf-8 -*-

import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))  
DATA_PATH = os.path.join(BASE_PATH, 'data')

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 2
CSRF_ENABLED = True
CSRF_SESSION_KEY = '35fb7c8e-2e74-11e8-9601-f0def165d278'
SECRET_KEY = '35fb7c8e2e7411e89601f0def165d278'  # 涉及数据库密码加解密，第1次设置后，请不要修改