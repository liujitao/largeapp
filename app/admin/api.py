# -*- coding: utf-8 -*-

from app import db
from app.admin import bp
from app.models import Host
import config

from flask import jsonify, request, make_response
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

import uuid
import rrdtool
import os

@bp.route('/api/host', methods=['GET'])
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

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Referer,Accept,Origin,User-Agent'
    return response


@bp.route('/api/host', methods=['POST'])
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

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Referer,Accept,Origin,User-Agent'
    return response


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

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Referer,Accept,Origin,User-Agent'
    return response

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

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Referer,Accept,Origin,User-Agent'
    return response

@bp.route('/api/jstree', methods=['GET'])
def get_jstree():
    hosts = Host.query.filter(Host.group_id==request.args['group_id']).all()
    data = [{'id': q.ip, 'parent': '#', 'text': q.name}
            for q in hosts if q.status == 1]

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Referer,Accept,Origin,User-Agent'
    return response

@bp.route('/api/performance', methods=['GET'])
def get_performance():
    if request.args['host'] and request.args['metric'] and request.args['start'] and request.args['end']:
        host = request.args['host']
        metric = request.args['metric']
        resolution = request.args.get('resolution', '60')
        start = request.args['start']
        end = request.args['end']

        rrd_file = '/opt/rrd/localhost/redis_info-%s:6379/%s.rrd' % (host, metric)

        # 读取rrd数据文件
        try:
            time_range, none, values = rrdtool.fetch(str(rrd_file), 'AVERAGE', '--resolution', str(resolution), '--start', str(start), '--end', str(end), '--daemon', 'unix:/var/run/rrdcached.sock')

            # 生成数据
            timestamps = [i for i in range(time_range[0], time_range[1], time_range[2])]
            data = [i for i in map(lambda x, y: {'x': datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), 'y': round(y[0], 2) if y[0] else y[0]}, timestamps, values)]
        except rrdtool.OperationalError:
            data = {'message': '请求数据异常'}

    else:
        data = {'message': '请求参数异常'}

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Referer,Accept,Origin,User-Agent'
    return response
