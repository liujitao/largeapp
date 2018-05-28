# -*- coding: utf-8 -*-

import collectd
import redis
from redis.sentinel import Sentinel
import re
import json

CONFIG = []

def configure_callback(config):
    host = '127.0.0.1'
    port = 6379
    password = '@sentinel'
    sentinel_port = 26379
    sentinel_name = 'mymaster'
    redis_info = {}

    for node in config.children:
        k, v = node.key,  node.values[0]
        match = re.search(r'Redis_(.*)$', k, re.M|re.I)

        if k == 'Host':
            host = v
        elif k == 'Port':
            port = int(v)
        elif k == 'Password':
            password = v
        elif k == 'Sentinel_port':
            sentinel_port = int(v)
        elif k == 'Sentinel_name':
            sentinel_name = v   
        elif match:
            redis_info[match.group(1)] = v
        else:  
            collectd.warning('unknown config key: %s' % (k))

    CONFIG.append({'host': host, 'port': port, 'password': password, 'sentinel_port': sentinel_port, 'sentinel_name': sentinel_name, 'redis_info': redis_info})

def fetch_redis_info(conf):
    info = {}

    # 获取redis状态信息(0 dead, 1 master, -1 slave)
    try:
        r = redis.Redis(host=conf['host'], port=conf['port'], password=conf['password'])
        for k, v in r.info().items():
            if k in conf['redis_info'].keys():
               info[k] = v
            elif k.startswith('db'):
                for i in ['keys','expires']: 
                   info[k+'_'+i] = v[i]
            elif k == 'role':
                if v == 'master':
                    info['redis_alive'] = 1
                else:
                    info['redis_alive'] = -1

        if info['maxmemory'] > 0:
            info['mem_used_ratio'] = round(float(info['used_memory'])/float(info['maxmemory'])*100, 2)
        else:
            info['mem_used_ratio'] = 0

        for k, v in r.info('commandstats').items():
            if k+'_calls' in conf['redis_info'].keys():
                info[k+'_calls'] = v['calls']

    except redis.RedisError as e:
        collectd.error('redis %s:%s connection error!' % (conf['host'], conf['port']))
        info['redis_alive'] = 0

    #  获取sentinel状态信息 (0 dead, 1 leader, -1 leaf)
    try:
        s = Sentinel([(conf['host'], conf['sentinel_port'])], socket_timeout=0.1)
        if conf['host'] == s.discover_master(conf['sentinel_name'])[0]:
            info['sentinel_alive'] = 1
        else:
            info['sentinel_alive'] = -1
    except redis.RedisError as e:
        collectd.error('sentinel %s:%s connection error!' % (conf['host'], conf['sentinel_port']))
        info['sentinel_alive'] = 0

    return info

def read_callback():
    for conf in CONFIG:
        info = fetch_redis_info(conf)

        plugin_instance = '%s:%d' % (conf['host'], conf['port'])
        for k, v in info.items():
            if k in conf['redis_info'].keys():
                dispatch_value(k, v, conf['redis_info'][k], plugin_instance)

def dispatch_value(key, value, type, plugin_instance):       
    val = collectd.Values(plugin='redis_info')
    val.type = type
    val.type_instance = key
    val.plugin_instance = plugin_instance
    val.values = [value]
    val.dispatch()

#注册回调函数
collectd.register_config(configure_callback)
collectd.register_read(read_callback)
