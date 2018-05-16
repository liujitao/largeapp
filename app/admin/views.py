# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, url_for
from app.admin import bp
from app.models import Host


@bp.route('/', methods=['GET'])
def index():
    return render_template('admin/index.html')

@bp.route('/dashboard/<id>', methods=['GET'])
def dashboard(id=1):
    return render_template('admin/dashboard.html', id=id)

@bp.route('/host', methods=['GET'])
def host():
    return render_template('admin/host.html')