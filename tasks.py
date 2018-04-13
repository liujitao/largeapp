# -*- coding: utf-8 -*-

from celery import Celery, chain
from celery.schedules import crontab

import celeryconfig
import config

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_, func

from datetime import datetime, timedelta
import time
import os, json
import redis, rrdtool
import logging

from app import db
from app.models import Host

celery = Celery()
celery.config_from_object(celeryconfig)

celery.conf.beat_schedule = {
    'get_performance_info': {
        'task': 'tasks.performance',
        'schedule': 10,
    }
}

# 日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('celery-worker.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


@celery.task
def performance():
    res = chain(get_info.s(), write_info.s())()

def read_redis_info(ip, port, password):
    try:
        pool = redis.ConnectionPool(host=ip, port=port, password=password)
        r = redis.Redis(connection_pool=pool)
        return r.info()

    except redis.RedisError as e:
        logger.error('redis数据库连接错误\n%s' % e)

    return None

@celery.task(max_retries=1)
def get_info():
    ''' 获取目标服务器信息 '''

    now = datetime.utcnow()
    try:
        # 最后检测时间为空，或者与当前时间间隔超过60秒，需要进行检测
        host = Host.query.filter(or_(Host.last_check_time < now - timedelta(seconds=60), Host.last_check_time == None)).filter(Host.status == 1).first()

        if host:
            info = read_redis_info(host.ip, host.port, host.password)
            
            if info:
                logger.info('成功获取 %s 性能数据' % host.name)
                # 修改最后检测时间，然后返回服务器信息
                host.last_check_time = now
                db.session.commit()
                
                return {'host': host.name, 'info': info}

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error('数据库错误\n%s' % e)
        
    return None

def create_rrd(rrd_file, datasource):
    ds = [ 'DS:%s:GAUGE:120:0:U' % datasource ]
    rra = [
        'RRA:AVERAGE:0.5:1:1440',  # 60s * 1 * 1440 = 24h
        'RRA:AVERAGE:0.5:15:672',  # 60s * 15 * 672 = 7d
        'RRA:AVERAGE:0.5:60:744',  # 60s * 60 * 744 = 31d
        'RRA:AVERAGE:0.5:1440:375', # 60s * 1440 * 375 = 375d
        'RRA:MIN:0.5:1:1440', 
        'RRA:MIN:0.5:15:672',
        'RRA:MIN:0.5:60:744',
        'RRA:MIN:0.5:1440:375',
        'RRA:MAX:0.5:1:1440', 
        'RRA:MAX:0.5:15:672',
        'RRA:MAX:0.5:60:744',
        'RRA:MAX:0.5:1440:375',
        'RRA:LAST:0.5:1:1440', 
        'RRA:LAST:0.5:15:672',
        'RRA:LAST:0.5:60:744',
        'RRA:LAST:0.5:1440:375',
    ]
    
    rrdtool.create(rrd_file, '--step', '60', '--start', '-1y', ds, rra)
    logger.info('建立 %s 数据文件' % rrd_file)

def update_rrd(path, datasource, value):
    # rrd数据文件是否存在
    rrd_file = os.path.join(path, '%s.rrd' % datasource)
    if not os.path.exists(rrd_file):
        create_rrd(rrd_file, datasource)
    
    rrdtool.update(rrd_file, '--template', datasource, 'N:%s' % value)
    logger.info('更新 %s 数据文件' % rrd_file)

@celery.task(max_retries=1)
def write_info(perf):
    if perf:
        host, info = perf['host'], perf['info']

        # rrd目录是否存在
        path = os.path.join(config.DATA_PATH, host)
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info('建立 %s 数据目录' % path)

        # 性能数据
        for tag in ['used_cpu_sys', 'used_cpu_user', 'used_memory', 'used_memory_rss', 'total_system_memory', 'connected_clients', 'blocked_clients', \
            'keyspace_hits', 'keyspace_misses', 'expired_keys', 'evicted_keys']:
            update_rrd(path, tag, info[tag])
