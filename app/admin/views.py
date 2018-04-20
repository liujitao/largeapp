# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, url_for
from app.admin import bp
from app.models import Host


@bp.route('/', methods=['GET'])
def index():
    if request.args:
        host = Host.query.filter(Host.uuid==request.args['uuid']).first()
    else:
        host = Host.query. filter(Host.status==1).first()
    return render_template('admin/dashboard.html', host=host)

@bp.route('/host', methods=['GET'])
def host():
    return render_template('admin/host.html')
