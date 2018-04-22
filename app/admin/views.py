# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, url_for
from app.admin import bp
from app.models import Host


@bp.route('/', methods=['GET'])
def index():
    return render_template('admin/dashboard.html')

@bp.route('/new', methods=['GET'])
def new():
    return render_template('admin/new.html')


@bp.route('/host', methods=['GET'])
def host():
    return render_template('admin/host.html')