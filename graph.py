#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, make_response
import rrdtool
from datetime import datetime

app = Flask(__name__)

@app.route('/api/performance', methods=['GET'])
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

    # return jsonify(data)

    # 支持跨域
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')