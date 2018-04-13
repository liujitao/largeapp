# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for
from app.admin import bp

@bp.route('/', methods=['GET'])
def index():
    return render_template('admin/dashboard.html')

@bp.route('/host', methods=['GET'])
def host():
    return render_template('admin/host.html')