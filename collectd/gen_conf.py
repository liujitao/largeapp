# -*- coding: utf-8 -*-

module = '''  <Module redis_info>
    Host "{}"
    Port {}
    Password "{}"
    sentinel_port {}
    sentinel_name {}

    Redis_redis_alive "gauge"
    Redis_sentinel_alive "gauge"

    Redis_connected_clients "gauge"
    Redis_blocked_clients "gauge"
    Redis_rejected_connections "counter"

    Redis_expired_keys "counter"
    Redis_evicted_keys "counter"
    
    Redis_used_memory "gauge"
    Redis_used_memory_rss "gauge"
    Redis_maxmemory "gauge"
    Redis_mem_used_ratio "gauge"
    Redis_mem_fragmentation_ratio "gauge"

    Redis_instantaneous_ops_per_sec "gauge"

    Redis_total_connections_received "counter"
    Redis_total_commands_processed "counter"

    Redis_keyspace_hits "derive"
    Redis_keyspace_misses "derive"

    Redis_cmdstat_get_calls "counter"
    Redis_cmdstat_set_calls "counter"

    Redis_db0_keys "gauge"
    Redis_db0_expires "gauge"
  </Module>'''

content = '''<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/opt/redis-collectd-plugin"
  Import "redis_info"'

{}
</Plugin>'''

port = 6379
password = '@sentinel'
sentinel_port = 26379
sentinel_name = 'mymaster'

hosts = [
'10.105.225.8', '10.154.146.25', '10.154.43.8', '10.105.93.170', '10.154.160.30', '10.154.162.125',
'10.154.165.211', '10.154.160.239', '10.105.9.94', '10.105.89.141', '10.105.51.187', '10.154.25.166',
'10.105.28.5', '10.105.15.122', '10.154.157.194', '10.154.157.133', '10.154.151.203', '10.105.212.194',
'10.154.165.84', '10.105.76.116', '10.154.165.132', '10.105.205.61', '10.154.163.45', '10.154.162.34',
'10.154.163.41', '10.105.6.58', '10.154.143.134', '10.154.163.30', '10.105.199.188', '10.105.78.0',
'10.154.38.188', '10.154.169.6', '10.154.143.59', '10.105.48.0', '10.105.209.162', '10.154.164.227',
'10.154.60.73', '10.105.107.23', '10.105.41.139', '10.105.241.162', '10.154.128.103', '10.133.206.103', 
'10.105.205.80', '10.154.172.95', '10.154.172.109', '10.105.13.202', '10.105.103.187', '10.105.72.189', 
'10.105.126.113', '10.154.14.117', '10.133.202.184', '10.154.26.182', '10.105.223.86'
]

modules = [ module.format(host, port, password, sentinel_port, sentinel_name) for host in hosts ]
    
with open('redis_info.conf', 'w') as f:
    f.write(content.format('\n'.join(modules)))
    f.write('\n')
