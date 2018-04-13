# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint('admin', __name__)

from app.admin.views import *
from app.admin.api import *