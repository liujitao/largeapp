#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, make_response
from functools import wraps
import rrdtool
from datetime import datetime

app = Flask(__name__)

def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_funs

@app.route('/api/performance', methods=['GET'])
@allow_cross_domain
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
            time_range, none, values = rrdtool.fetch(str(rrd_file), 'AVERAGE', '--resolution', str(resolution), '--start', str(start), '--end', str(end), '--align-start', '--daemon', 'unix:/var/run/rrdcached.sock')

            # 生成数据
            timestamps = [i for i in range(time_range[0], time_range[1], time_range[2])]
            data = [i for i in map(lambda x, y: {'x': datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), 'y': y[0]}, timestamps, values)]
        except rrdtool.OperationalError:
            data = {'message': '请求数据异常'}

    else:
        data = {'message': '请求参数异常'}

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)