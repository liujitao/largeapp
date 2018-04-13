# -*- coding: utf-8 -*-

enable_utc = True
timezone = 'Asia/Shanghai'

broker_url = 'redis://:@127.0.0.1:6379/0'
result_backend = 'redis://:@127.0.0.1:6379/1'

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
result_expires = 60 # 结果保留600秒

task_default_queue = 'default'
'''
task_routes = ([
    ('tasks.get_server_info', {'queue': 'server'}),
    ('tasks.get_performance_info', {'queue': 'performance'}),
    ('tasks.parse_performance_info', {'queue': 'parse'}),
    ('tasks.write_performance_info', {'queue': 'write'}),
])
'''