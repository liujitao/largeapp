# -*- coding: utf-8 -*-

from app import db
from app.admin import bp
from app.models import Host
import config

from flask import jsonify, request, make_response
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from functools import wraps
import uuid
import rrdtool
import os

def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun

@bp.route('/api/host', methods=['GET'])
@allow_cross_domain
def get_host():
    if request.args:
        if request.args.get('uuid'):
            host = Host.query.filter(Host.uuid == request.args['uuid']).first()
            if host:
                data = {'uuid': host.uuid, 'name': host.name, 'ip': host.ip, 'port': host.port, 'password': host.password,
                        'status': host.status, 'last_check_time': host.last_check_time, 'create_time': host.create_time, 'update_time': host.update_time}
            else:
                data = {'message': '没有匹配记录'}
        else:
            hosts = Host.query.all()
            data = [{'uuid': q.uuid, 'name': q.name, 'ip': q.ip, 'port': q.port, 'password': q.password,
                     'status': q.status, 'last_check_time': q.last_check_time, 'create_time': q.create_time, 'update_time': q.update_time}
                    for q in hosts]
    else:
        data = {'message': '请求参数异常'}

    return jsonify(data)


@bp.route('/api/host', methods=['POST'])
@allow_cross_domain
def add_host():
    if request.json:
        host = Host()
        host.uuid = str(uuid.uuid1())
        host.name = request.json['name']
        host.ip = request.json['ip']
        host.port = request.json['port']
        host.password = request.json['password']
        host.status = request.json['status']
        host.create_time = datetime.utcnow()
        db.session.add(host)

        try:
            db.session.commit()
            data = {'message': '新建数据成功'}

        except SQLAlchemyError as e:
            db.session.rollback()
            data = {'message': ' 新建数据失败'}

    else:
        data = {'message': '请求数据异常'}

    return jsonify(data)


@bp.route('/api/host', methods=['PUT'])
def update_host():
    if request.json:
        host = Host.query.filter(Host.uuid == request.json['uuid']).first()
        host.name = request.json['name']
        host.ip = request.json['ip']
        host.port = request.json['port']
        host.password = request.json['password']

        host.status = request.json['status']
        host.update_time = datetime.utcnow()

        try:
            db.session.commit()
            data = {'message': '更新数据成功'}

        except SQLAlchemyError as e:
            db.session.rollback()
            data = {'message': '更新数据失败'}

    else:
        data = {'message': '请求数据异常'}

    return jsonify(data)


@bp.route('/api/host', methods=['DELETE'])
def delete_host():
    if request.args and request.args.get('uuid'):
        host = Host.query.filter(Host.uuid == request.args['uuid']).first()
        if host:
            db.session.delete(host)

            try:
                db.session.commit()
                data = {'message': '删除数据成功'}

            except SQLAlchemyError as e:
                db.session.rollback()
                data = {'message': ' 删除数据失败'}

        else:
            data = {'message': '没有匹配记录'}
    else:
        data = {'message': '请求参数异常'}

    return jsonify(data)


@bp.route('/api/performance', methods=['GET'])
def get_performance():
    if request.args['host'] and request.args['metric'] and request.args['start'] and request.args['end']:
        host = request.args['host']
        metric = request.args['metric']
        resolution = request.args.get('resolution', '60')
        start = request.args['start']
        # 延迟60秒
        end = str(int(request.args['end']) - 60)

        path = os.path.join(config.DATA_PATH, host)
        rrd_file = os.path.join(path, '%s.rrd' % metric)

        # 读取rrd数据文件
        try:
            time_range, none, values = rrdtool.fetch(
                rrd_file, 'AVERAGE', '--resolution', resolution, '--start', start, '--end', end)

            # 生成数据
            timestamps = [i for i in range(
                time_range[0], time_range[1], time_range[2])]
            data = [i for i in map(lambda x, y: {'x': datetime.fromtimestamp(
                x).strftime('%Y-%m-%d %H:%M:%S'), 'y': y[0]}, timestamps, values)]
        except rrdtool.OperationalError as e:
            data = {'message': '请求数据异常'}

    else:
        data = {'message': '请求参数异常'}

    return jsonify(data)


@bp.route('/api/jstree', methods=['GET'])
def get_jstree():
    hosts = Host.query.all()
    data = [{'id': q.ip, 'parent': '#', 'text': q.name}
            for q in hosts if q.status == 1]

    return jsonify(data)
